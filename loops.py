
garbage = ["Trash", "junk", "ness", "stuff", "stuff", "junk", "stuff"]

for item in garbage:
    print(item)
    ulen = garbage.count(item)
    totallen = len(garbage)

print(f"garbage containes {ulen} unqiue items")
print(f"garbage contains total {totallen} items")