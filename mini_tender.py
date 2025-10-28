import json
import os

# Load tenders from file if exists, else start with defaults
if os.path.exists("tenders.json"):
    with open("tenders.json", "r") as f:
        tenders = json.load(f)
else:
    tenders = [
        {"title": "Tender 1","province": "Bagmati","organization": "Urban Dev Office", "amount": 50000, "deadline": "2024-2-2"},
        {"title": "Tender 2","province": "Karnali","organization": "DoJ", "amount": 52000, "deadline": "2024-3-2"},
        {"title": "Tender 3","province": "Bagmati","organization": "PLE", "amount": 12000, "deadline": "2024-1-2"},
        {"title": "Tender 4","province": "Madesh","organization": "Urban Dev Office", "amount": 30000, "deadline": "2023-2-2"}
    ]

def save_tenders():
    """Save tenders to file."""
    with open("tenders.json", "w") as f:
        json.dump(tenders, f, indent=2, ensure_ascii=False)

def ViewAllTenders():
    """Print all tenders in JSON format."""
    print(json.dumps(tenders, indent=2, ensure_ascii=False))

def Search():
    print("what to search by: ")
    print("1. province")
    print("2. title")
    print("3. organization")
    
    choice = input("choose: ")
    found = False

    term = input("enter search term: ").strip().lower()

    for tender in tenders:
        if (
            (choice == "1" and tender["province"].lower() == term)
            or (choice == "2" and tender["title"].lower() == term)
            or (choice == "3" and tender["organization"].lower() == term)
        ):
            print(json.dumps(tender, indent=2, ensure_ascii=False))
            found = True

    if not found:
        print("no matching tender found.")

# Main loop
while True:
    print("\n-- options --")
    print("1. View all tenders")
    print("2. Search")
    print("3. Add tender")
    print("4. Exit")

    choice = input("Enter the action: ")

    match choice:
        case "1":
            ViewAllTenders()

        case "2":
            Search()

        case "3":
            title = input("Enter title: ")
            province = input("Enter province: ")
            organization = input("Enter organization: ")
            amount = float(input("Enter amount: "))
            deadline = input("Enter deadline (YYYY-MM-DD): ")

            new_tender = {
                "title": title,
                "province": province,
                "organization": organization,
                "amount": amount,
                "deadline": deadline
            }
            tenders.append(new_tender)
            save_tenders()  #  Save only after change
            print("Tender added and saved successfully!")

        case "4":
            print("Exiting program.")
            break

        case _:
            print("Invalid choice.")
