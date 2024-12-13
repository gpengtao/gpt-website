from functools import wraps


def a_decorator(a_func):
    """装饰器函数"""
    print("1111111111")

    @wraps(a_func)
    def wrap_the_function(*args, **kwargs):
        print("在执行 a_func() 之前干一些事情")
        for arg in args:
            print("wrap收到的args是:" + arg)
        for key, value in kwargs.items():
            print(f"wrap收到的kwargs是{key}: {value}")
        a_func(*args, **kwargs)
        print("在执行完 a_func() 之后干一些事情")

    print("222222222222")
    return wrap_the_function


@a_decorator
def my_function(arg):
    """这个是我们的目标要执行的函数"""
    print("function执行了,参数是:" + arg)


# 调用函数
my_function("hello")
# 输入的内容如下:
# 在执行 a_func() 之前干一些事情
# function执行了
# 在执行完 a_func() 之后干一些事情

# @a_new_decorator 只是一个简短的下面的写法：
a_function_requiring_decoration = a_decorator(my_function)

# 打印函数名字，因为写了 @wraps(a_func)，所以打印的是原来的方法的信息
print(a_function_requiring_decoration.__name__)
print(a_function_requiring_decoration.__doc__)
