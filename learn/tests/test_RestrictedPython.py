from RestrictedPython import compile_restricted
from RestrictedPython import safe_builtins
from RestrictedPython.Eval import default_guarded_getitem

# 定义一个用户提交的代码（示例：计算两个数的和，但尝试危险操作）
user_code = """
def add(a, b):
    # 尝试危险操作：写入文件（会被禁止）
    with open('/tmp/test.txt', 'w') as f:
        f.write('hack!')
    return a + b

result = add(3, 5)
"""

# 步骤 1：编译受限制的代码
try:
    byte_code = compile_restricted(user_code, filename="<user_code>", mode="exec")
except SyntaxError as e:
    print(f"代码语法错误: {e}")  # 捕获语法错误
    exit()

# 步骤 2：创建安全执行环境（限制内置函数和变量）
restricted_globals = {
    "__builtins__": safe_builtins,  # 使用安全的内置函数（禁用危险函数如open/__import__）
    "_getitem_": default_guarded_getitem,  # 允许安全访问字典/列表
    "_print_": print,  # 允许使用print
    "__metaclass__": type,  # 避免类定义错误
}

# 步骤 3：执行代码（捕获运行时异常）
try:
    exec(byte_code, restricted_globals)
except Exception as e:
    print(f"执行错误: {e}")  # 输出：执行错误: __import__ not found (因为open被禁用)
else:
    # 如果执行成功，获取结果
    print("计算结果:", restricted_globals['result'])
