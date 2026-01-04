"""
使用 browser_cookie3 读取 Chrome 浏览器的 cookie
"""

import json
from urllib.parse import urlparse

import browser_cookie3
import requests


def do_get_chrome_cookies(domain):
    """
    从 Chrome 浏览器读取指定域名的 cookie
    Args:
        domain: 目标域名，例如 'www.baidu.com'
    Returns:
        list: cookie 列表
    注意：
        - 在 Mac 上，系统可能会要求输入登录密码来访问 Chrome 的 cookie 数据库
        - 这是正常的系统安全机制，输入你的 Mac 登录密码即可
        - 如果 Chrome 正在运行，建议先关闭 Chrome 再运行此脚本
    """
    cookies = []
    try:
        # 加载 Chrome 的 cookie
        # 在 Mac 上会自动查找 ~/Library/Application Support/Google/Chrome/Default/Cookies
        # 系统可能会提示输入 Mac 登录密码来访问受保护的文件
        print("正在访问 Chrome cookie 数据库...")
        print("提示：如果系统要求输入密码，请输入你的 Mac 登录密码")
        cj = browser_cookie3.chrome(domain_name=domain)

        for cookie in cj:
            cookies.append({
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'secure': cookie.secure,
                'expires': cookie.expires,
            })
            print(f"Cookie: {cookie.name} = {cookie.value}")
            print(f"  Domain: {cookie.domain}")
            print(f"  Path: {cookie.path}")
            print(f"  Secure: {cookie.secure}")
            print(f"  Expires: {cookie.expires}")
            print("-" * 50)
        return cookies
    except Exception as e:
        error_msg = str(e)
        print(f"读取 cookie 时出错: {error_msg}")
        if "password" in error_msg.lower() or "keychain" in error_msg.lower():
            print("\n提示：")
            print("1. 请确保输入的是你的 Mac 登录密码（用户账户密码）")
            print("2. 如果 Chrome 正在运行，请先关闭 Chrome 浏览器")
            print("3. 确保 Chrome 浏览器已安装并至少登录过一次目标网站")
        return []


def get_cookies_for_url(url):
    """
    从 Chrome 浏览器读取指定 URL 的 cookie
    
    Args:
        url: 目标 URL，例如 'https://www.baidu.com/'
    
    Returns:
        list: cookie 列表
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    # 移除端口号（如果有）
    if ':' in domain:
        domain = domain.split(':')[0]

    print(f"正在读取域名 {domain} 的 cookie...")
    print("=" * 50)

    cookies = do_get_chrome_cookies(domain)
    print(f"总共找到 {len(cookies)} 个 cookie")

    filtered_cookies = [cookie for cookie in cookies if filter_domain in cookie['domain']]
    print(f"过滤后（domain={filter_domain}）找到 {len(filtered_cookies)} 个 cookie")
    print("获取到的cookie如下:\n")
    print(json.dumps(filtered_cookies, ensure_ascii=False))

    return filtered_cookies


if __name__ == "__main__":
    # 目标网站
    target_url = "xxxx.com"

    cookies = get_cookies_for_url(target_url)

    # 过滤出 domain
    filter_domain = target_url
    filtered_cookies = [cookie for cookie in cookies if filter_domain in cookie['domain']]

    # 将 cookie 列表转换为 requests 可用的字典格式
    cookies_dict = {cookie['name']: cookie['value'] for cookie in filtered_cookies}
    # 使用 requests 发送请求
    response = requests.get(
        "xxxx.com",
        cookies=cookies_dict
    )
    print(f"\n请求状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
