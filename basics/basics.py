print("this is a calculator")


def add(a,b):
    print(a+b)


def sub(a,b):
    print(a-b)


def mult(a,b):
    print(a*b)


def div(a,b):
    if (b != 0):
        print(a/b)
    else:
        print("division by zero not possible")

print("select first operand: ")
a = float(input())

print("select second operand:")
b = float(input())

print("select operation:")
op = input()

match op: 
    case "+":
        add(a,b)
    case "-":
        sub(a,b)
    case "*":
        mult(a,b)
    case "/":
        div(a,b)
    case _:
        print("invalid operation")

cont = input("continue?(y/n)")
if cont == "y":
    import basics
else:
    print("done")



