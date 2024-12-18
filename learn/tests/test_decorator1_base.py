from functools import wraps

"""
装饰器函数的基本写法
"""


def my_decorator(fun):
    """my装饰器函数"""

    print("进入装饰器函数,1111111111")

    @wraps(fun)
    def wrap_the_function(*args, **kwargs):
        print(f"在执行目标函数 {fun.__name__} 之前干一些事情")
        for arg in args:
            print("wrap收到的args是:" + arg)
        for key, value in kwargs.items():
            print(f"wrap收到的kwargs是{key}: {value}")
        fun(*args, **kwargs)
        print(f"在执行完目标函数 {fun.__name__} 之后干一些事情")

    print("离开装饰器函数,222222222222")
    return wrap_the_function


@my_decorator
def say_hello_function(arg):
    """我的say hello函数"""

    print("function执行了,参数是:" + arg)


# 调用函数
say_hello_function("hello")
# 输入的内容如下:
# 在执行 a_func() 之前干一些事情
# function执行了
# 在执行完 a_func() 之后干一些事情

# @a_new_decorator 只是一个简短的下面的写法：
a_function_requiring_decoration = my_decorator(say_hello_function)

# 打印函数名字，因为写了 @wraps(a_func)，所以打印的是原来的方法的信息
print(a_function_requiring_decoration.__name__)
print(a_function_requiring_decoration.__doc__)
