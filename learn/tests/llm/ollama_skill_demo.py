"""
演示：用本地 Ollama 模拟 Cursor 里「技能目录进上下文 + 按需加载 SKILL.md 全文」。

Cursor 实际怎么搞（概念上，无官方公开源码）：
- Agent 会话里会出现 <agent_skills> 一类块：每个技能有 name、description、fullPath（路径），
  来自各 SKILL.md 的 YAML 头；这是宿主（Cursor）组装的，不是模型自己发现的。
- 需要执行某技能时，再通过 Read 等工具读文件，把正文追加进上下文。

本脚本做的事：
- 递归扫描你本机 Cursor 技能目录里的 SKILL.md（默认 ~/.cursor/skills 与 ~/.cursor/skills-cursor），
  解析 frontmatter，拼成与「目录」等价的 system 文案。
- 用环境变量 SKILL_FULL_NAME 或 SKILL_FILE 指定「按需加载」哪一条的全文；否则用第一个匹配项。

环境变量（节选）：
- CURSOR_SKILL_DIRS   逗号分隔目录，覆盖默认
- SKILL_FULL_NAME     与 frontmatter 里 name 字段一致，用于第三轮的「全文」
- SKILL_FILE          某 SKILL.md 的绝对路径，优先于 SKILL_FULL_NAME
- SKILL_CATALOG_MAX   目录里最多列几条技能（防撑爆上下文）
- SKILL_BODY_MAX_CHARS  第三轮注入的全文最大字符数；0 表示不截断（长 SKILL 会拖慢本地模型）
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# 默认与 Cursor 文档一致：个人技能目录（项目级可用 .cursor/skills，自行加进 CURSOR_SKILL_DIRS）
_DEFAULT_SKILL_ROOTS = (
    Path.home() / ".cursor" / "skills",
    Path.home() / ".cursor" / "skills-cursor",
)


def _split_frontmatter(markdown: str) -> tuple[str, str]:
    """返回 (frontmatter_raw, body)。无合法 frontmatter 时返回 ("", markdown)。"""
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        return "", markdown
    end = None
    for j in range(1, len(lines)):
        if lines[j].strip() == "---":
            end = j
            break
    if end is None:
        return "", markdown
    fm = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1 :]).lstrip("\n")
    return fm, body


def _strip_yaml_scalar(val: str) -> str:
    """去掉 Cursor 里常见的 name: \"foo\" 这类引号包裹。"""
    val = val.strip()
    if len(val) >= 2 and val[0] in '"\'' and val[0] == val[-1]:
        return val[1:-1]
    return val


def _parse_yamlish_frontmatter(fm: str) -> dict[str, str]:
    """
    解析 Cursor SKILL.md 里常见的 YAML 子集：name、description（含 >- 折行）。
    不依赖 PyYAML，避免额外依赖。
    """
    meta: dict[str, str] = {}
    lines = fm.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip()
        if not line.strip():
            i += 1
            continue
        if line.startswith("name:"):
            meta["name"] = _strip_yaml_scalar(line.split(":", 1)[1])
            i += 1
            continue
        if line.startswith("description:"):
            rest = line.split(":", 1)[1].strip()
            if rest in (">-", ">", "|"):
                i += 1
                parts: list[str] = []
                while i < len(lines):
                    nxt = lines[i]
                    if nxt and not nxt[0].isspace() and not nxt.strip().startswith("#"):
                        break
                    if nxt.strip():
                        parts.append(nxt.strip())
                    i += 1
                meta["description"] = " ".join(parts)
                continue
            meta["description"] = _strip_yaml_scalar(rest)
            i += 1
            continue
        i += 1
    return meta


def discover_skill_files(roots: list[Path]) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        out.extend(sorted(root.rglob("SKILL.md")))
    # 稳定去重
    seen: set[str] = set()
    uniq: list[Path] = []
    for p in out:
        k = str(p.resolve())
        if k not in seen:
            seen.add(k)
            uniq.append(p)
    return uniq


def load_skills_catalog(paths: list[Path]) -> list[dict[str, str]]:
    """每项：name, description, fullPath（与 Cursor agent_skills 里路径含义类似）。"""
    rows: list[dict[str, str]] = []
    for p in paths:
        text = p.read_text(encoding="utf-8", errors="replace")
        fm, _ = _split_frontmatter(text)
        meta = _parse_yamlish_frontmatter(fm)
        name = meta.get("name") or p.parent.name
        desc = meta.get("description") or "(无 description)"
        rows.append(
            {
                "name": name,
                "description": desc,
                "fullPath": str(p.resolve()),
            }
        )
    return rows


def _skill_name_from_file(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, _ = _split_frontmatter(text)
    meta = _parse_yamlish_frontmatter(fm)
    return meta.get("name") or path.parent.name


def pick_full_skill_path(
    catalog: list[dict[str, str]],
    all_paths: list[Path],
    skill_file: str | None,
    skill_full_name: str | None,
) -> Path | None:
    if skill_file:
        fp = Path(skill_file).expanduser()
        if fp.is_file():
            return fp.resolve()
        print(f"警告：SKILL_FILE 不存在 {fp}，将按名称匹配。", file=sys.stderr, flush=True)
    if skill_full_name:
        for r in catalog:
            if r["name"] == skill_full_name:
                return Path(r["fullPath"])
        for p in all_paths:
            try:
                if _skill_name_from_file(p) == skill_full_name:
                    return p.resolve()
            except OSError:
                continue
        print(
            f"警告：未找到 name={skill_full_name!r}，改用列表第一项。",
            file=sys.stderr,
            flush=True,
        )
    if all_paths:
        return all_paths[0].resolve()
    return None


def build_chat_body(model: str, system: str | None, user: str) -> dict:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    return {
        "model": model,
        "messages": messages,
        "stream": False,
    }


def print_chat_request(label: str, base_url: str, body: dict) -> None:
    """把本次调用将发给 Ollama 的 JSON 体打印到 stderr（含 model、messages 全文）。"""
    url = base_url.rstrip("/") + "/api/chat"
    print(f"\n{'=' * 72}", file=sys.stderr, flush=True)
    print(f"{label}", file=sys.stderr, flush=True)
    print(f"POST {url}", file=sys.stderr, flush=True)
    print(json.dumps(body, ensure_ascii=False, indent=2), file=sys.stderr, flush=True)


def ollama_chat(base_url: str, body: dict) -> str:
    url = base_url.rstrip("/") + "/api/chat"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    msg = data.get("message") or {}
    return (msg.get("content") or "").strip()


def _parse_skill_dirs() -> list[Path]:
    raw = os.environ.get("CURSOR_SKILL_DIRS", "").strip()
    if raw:
        return [Path(p.strip()).expanduser() for p in raw.split(",") if p.strip()]
    return list(_DEFAULT_SKILL_ROOTS)


def main() -> None:
    if os.environ.get("LIST_SKILLS", "").strip() in ("1", "true", "yes"):
        roots = _parse_skill_dirs()
        paths = discover_skill_files(roots)
        cat = load_skills_catalog(paths)
        print(json.dumps(cat, ensure_ascii=False, indent=2))
        print(f"\n共 {len(cat)} 个 SKILL.md（扫描根目录：{roots}）", file=sys.stderr)
        return

    base = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
    model = os.environ.get("OLLAMA_MODEL", "llama3:latest")
    user_content = f"用一句话介绍你自己，你能做什么，你有哪些技能。请用简体中文回答。"

    roots = _parse_skill_dirs()
    paths = discover_skill_files(roots)
    max_cat = int(os.environ.get("SKILL_CATALOG_MAX", "40"))
    paths_limited = paths[:max_cat] if len(paths) > max_cat else paths

    catalog_rows = load_skills_catalog(paths_limited)
    skill_file = os.environ.get("SKILL_FILE", "").strip() or None
    skill_full_name = os.environ.get("SKILL_FULL_NAME", "").strip() or None
    full_path = pick_full_skill_path(catalog_rows, paths, skill_file, skill_full_name)

    if not catalog_rows:
        print(
            "未在以下目录发现任何 SKILL.md：\n"
            + "\n".join(str(r) for r in roots)
            + "\n可设置 CURSOR_SKILL_DIRS=路径1,路径2 或在本机安装 Cursor 技能。",
            file=sys.stderr,
            flush=True,
        )
        sys.exit(2)

    # 对齐 Cursor：先给「目录」（元数据），再给「某技能全文」模拟 Read 之后
    catalog_only_system = (
        "回复用户时一律使用简体中文。\n\n"
        "以下为从本机 Cursor 技能目录扫描得到的技能列表（name / description / fullPath），"
        "与对话里 <agent_skills> 类似，仅元数据、不含 SKILL 正文：\n"
        + json.dumps(catalog_rows, ensure_ascii=False, indent=2)
        + "\n\n若任务需要某技能，你应说明将依据哪个 name，并按 description 行事；"
        "正文需通过「读取对应 fullPath 文件」才能获得（本演示第三轮会替你注入其中一份全文）。"
    )

    skill_body = ""
    if full_path and full_path.is_file():
        skill_body = full_path.read_text(encoding="utf-8", errors="replace")
        max_body = int(os.environ.get("SKILL_BODY_MAX_CHARS", "0"))
        if max_body > 0 and len(skill_body) > max_body:
            skill_body = (
                skill_body[:max_body]
                + f"\n\n…（已截断，SKILL_BODY_MAX_CHARS={max_body}）"
            )
    else:
        skill_body = "（错误：未找到要加载全文的 SKILL.md）"

    full_skill_system = (
        catalog_only_system
        + f"\n\n--- 以下为按需加载的技能全文（模拟 Read `{full_path}`） ---\n\n"
        + skill_body
    )

    print("=== Ollama demo（Cursor 技能扫描）===", file=sys.stderr, flush=True)
    print(f"base={base} model={model}", file=sys.stderr, flush=True)
    print(
        f"扫描根目录: {roots} | 列入目录: {len(catalog_rows)} 个 | "
        f"全文来自: {full_path}",
        file=sys.stderr,
        flush=True,
    )
    if len(paths) > len(paths_limited):
        print(
            f"提示：本机共 {len(paths)} 个 SKILL.md，已按 SKILL_CATALOG_MAX={max_cat} 截断目录列表。",
            file=sys.stderr,
            flush=True,
        )

    try:
        body_no = build_chat_body(model, None, user_content)
        print_chat_request("【无 system】请求参数", base, body_no)
        out_no = ollama_chat(base, body_no)
        print("【无 system】\n", out_no, "\n", sep="", flush=True)

        body_cat = build_chat_body(model, catalog_only_system, user_content)
        print_chat_request("【仅目录（元数据，模拟 agent_skills）】请求参数", base, body_cat)
        out_cat = ollama_chat(base, body_cat)
        print("【仅目录（元数据）】\n", out_cat, "\n", sep="", flush=True)

        body_full = build_chat_body(model, full_skill_system, user_content)
        print_chat_request("【目录 + 一份技能全文（模拟 Read）】请求参数", base, body_full)
        out_full = ollama_chat(base, body_full)
        print("【目录 + 技能全文】\n", out_full, "\n", sep="", flush=True)
    except urllib.error.URLError as e:
        print(
            "连接 Ollama 失败。请先启动：`ollama serve`，并拉取模型：`ollama pull "
            + model
            + "`\n",
            e,
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
