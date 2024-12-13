import inspect


def say_hello():
    print("function，Hello, world!")


class MyClass:
    def __init__(self):
        print("init")

    def say_hello(self):
        print("method，Hello, world!" + self.__class__.__name__)


print(inspect.isfunction(say_hello()))
print(inspect.ismethod(say_hello))

print(inspect.isfunction(MyClass.say_hello))
print(inspect.ismethod(MyClass.say_hello))
