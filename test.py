def func():
    print("in func")
    for i in range(3):
        print("y"*i)

    yield "hello"

    for i in range(10):
        print(i)

x = func()
for y in x:
    print(y)
