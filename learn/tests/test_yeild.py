def test_yield():
    aa = {"name": "test", "age": 18}
    bb = [1, 2, 3]

    print("进入1")
    yield 1

    cc = ("hello", "world")
    print("进入2")
    yield 2

    dd = "this is a var"
    print("进入3")
    yield 3

    print("进入4")
    print(aa)
    print(bb)


obj = test_yield()
print(obj.__class__)

print(obj.__next__())
print(next(obj))
print(obj.__next__())
print(obj.__next__())
print(obj.__next__())

print("===========")