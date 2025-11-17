me = {
    "name" : "pranaya",
    "age" : 18,
    "hobby" : "none",
    "dog" : False
}

pranjal = {
    "name" : "pranjal",
    "age" : 14,
    "hobby" : "gaming",
    "dog" : True
}

samyak = {
    "name" : "samyak",
    "age" : 18,
    "hobby" : "reading",
    "dog" : True
}


people = [
    { "name" : "someone", "age" : 21, "hobby" : "reading", "dog" : True},
    pranjal , me, samyak
]

brothers = [pranjal, me, samyak]

hobby = input("choose which hobby to search for: ")
found = False

for peps in people:
    if peps["hobby"] == hobby:
        print(peps["name"])
        found = True
    
    if (found == False ):
        print("no people with matching hobby")
    