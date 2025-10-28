import json

tenders = [
    {"title": "Tender 1","province": "Bagmati","organization": "Urban Dev Office", "amount" : 50000, "deadline" : "2024-2-2"},
    {"title": "Tender 2","province": "Karnali","organization": "DoJ", "amount" : 52000, "deadline" : "2024-3-2"},
    {"title": "Tender 3","province": "Bagmati","organization": "PLE", "amount" : 12000, "deadline" : "2024-1-2"},
    {"title": "Tender 4","province": "Madesh","organization": "Urban Dev Office", "amount" : 30000, "deadline" : "2023-2-2"}
]

def ViewAllTenders():
    print(json.dumps(tenders, indent=2, ensure_ascii=False))

def Search():
    print("what to search by: ")
    print("1. province")
    print("2. title")
    print("3. organization")
    
    choice = input("choose:")
    found = False

    if choice == "1":
        term = input("enter province: ").strip().lower()
        for tender in tenders:
            if tender["province"].lower() == term:
                print(json.dumps(tender, indent=2, ensure_ascii=False))
                found = True
        if not found:
            print("no tender with matching province")

    elif choice == "2":
        term = input("enter title: ").strip().lower()
        for tender in tenders:
            if tender["title"].lower() == term:
                print(json.dumps(tender, indent=2, ensure_ascii=False))
                found = True
        if not found:
            print("no tender with matching title")

    elif choice == "3":
        term = input("enter organization: ").strip().lower()
        for tender in tenders:
            if tender["organization"].lower() == term:
                print(json.dumps(tender, indent=2, ensure_ascii=False))
                found = True
        if not found:
            print("no tender with matching organization")

    else:
        print("invalid choice")

while True:
    fo = open("tenders.json", "w")
    fo.write(json.dumps(tenders, indent=2))

    print("--options--")
    print("1. view all tenders")
    print("2. search")
    print("3. Add tender")
    print("4. Exit")

    choice = input("Enter the action")

    match choice:
        case "1":
            ViewAllTenders()

        case "2":
            Search()

        case "3":
            title = input("Enter title: ")
            province = input("Enter province: ")
            organization = input("Enter organization: ")
            amount = float(input("enter amount:"))
            deadline = input("enter deadline (YYY-MM-DD): ")
            new_tender = {
                "title": title,
                "province": province,
                "organization": organization,
                "amount": amount,
                "deadline": deadline
            }
            tenders.append(new_tender)

        case "4":
            break
        case _:
            print("invalid choice")
    fo.close()
    break
