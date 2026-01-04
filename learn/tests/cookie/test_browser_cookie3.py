"""
使用 browser_cookie3 读取 Chrome 浏览器的 cookie
"""

from urllib.parse import urlparse

import browser_cookie3


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

    return do_get_chrome_cookies(domain)


if __name__ == "__main__":
    # 目标网站
    target_url = "https://www.baidu.com/"

    print("=" * 50)
    print("Chrome Cookie 读取工具")
    print("=" * 50)
    print(f"目标网站: {target_url}")
    print("\n注意事项：")
    print("- 系统可能会要求输入 Mac 登录密码（这是正常的）")
    print("- 建议先关闭 Chrome 浏览器再运行此脚本")
    print("- 确保已在 Chrome 中访问过目标网站")
    print("=" * 50)
    print()

    cookies = get_cookies_for_url(target_url)

    print(f"\n总共找到 {len(cookies)} 个 cookie")

    # 如果需要将 cookie 转换为字典格式（用于 requests 等库）
    if cookies:
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        print("\nCookie 字典格式:")
        print(cookie_dict)
