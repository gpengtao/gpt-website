from django.utils.decorators import method_decorator

"""
测试Django提供的装饰器
"""


# my装饰器函数
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("装饰器执行前")
        for arg in args:
            print(arg)
        for key, value in kwargs.items():
            print(f"{key}: {value}")
        return func(*args, **kwargs)

    return wrapper


@method_decorator(my_decorator)
def my_function(arg):
    """这个是我们的目标要执行的函数"""
    print("function执行了,参数是:" + arg)


# 调用函数
my_function("hello")
