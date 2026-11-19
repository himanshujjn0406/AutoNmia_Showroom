"""
AutoNmia Showroom
A Python-based car catalogue, recommendation and sales management system.

Run:
    python autonmia_showroom.py

Files created/used:
    cars.csv       - car catalogue (created with sample data if missing)
    sales.csv      - sales records (created when first sale is made)
    report.txt     - generated sales summary
"""

import csv
import os
from datetime import datetime
from collections import Counter, defaultdict

CARS_FILE = "cars.csv"
SALES_FILE = "sales.csv"
REPORT_FILE = "report.txt"

# Sample catalogue. Add more rows to cars.csv using the same column headings.
SAMPLE_CARS = [
    ["1", "Maruti Suzuki", "Alto K10", "Petrol", 399000],
    ["2", "Maruti Suzuki", "S-Presso", "Petrol", 426000],
    ["3", "Maruti Suzuki", "Celerio", "Petrol", 537000],
    ["4", "Maruti Suzuki", "Wagon R", "Petrol", 555000],
    ["5", "Maruti Suzuki", "Swift", "Petrol", 649000],
    ["6", "Maruti Suzuki", "Baleno", "Petrol", 649000],
    ["7", "Tata", "Tiago", "Petrol", 500000],
    ["8", "Tata", "Tiago", "CNG", 600000],
    ["9", "Tata", "Punch", "Petrol", 610000],
    ["10", "Tata", "Nexon", "Petrol", 800000],
    ["11", "Hyundai", "Grand i10 Nios", "Petrol", 590000],
    ["12", "Hyundai", "Exter", "Petrol", 600000],
    ["13", "Hyundai", "Venue", "Petrol", 800000],
    ["14", "Mahindra", "Thar", "Petrol", 1150000],
    ["15", "Mahindra", "XUV 3XO", "Petrol", 750000],
    ["16", "Toyota", "Glanza", "Petrol", 680000],
    ["17", "Toyota", "Urban Cruiser Taisor", "Petrol", 770000],
    ["18", "Tata", "Nexon EV", "Electric", 1450000],
    ["19", "Mahindra", "XUV400", "Electric", 1560000],
    ["20", "Tata", "Punch EV", "Electric", 1100000],
]

def create_sample_catalogue():
    """Create cars.csv if it does not already exist."""
    if not os.path.exists(CARS_FILE):
        with open(CARS_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "brand", "model", "fuel", "ex_showroom"])
            writer.writerows(SAMPLE_CARS)

def price_breakdown(car):
    """Calculate estimated on-road price components."""
    ex = float(car["ex_showroom"])
    rto = 0 if car["fuel"].lower() == "electric" else round(ex * 0.10)
    insurance = round(ex * 0.035)
    add_ons = 15000
    gst_on_add_ons = round(add_ons * 0.18)
    return {
        "Ex-showroom": round(ex),
        "RTO": rto,
        "Insurance": insurance,
        "Add-ons": add_ons,
        "GST on add-ons": gst_on_add_ons,
        "On-road": round(ex) + rto + insurance + add_ons + gst_on_add_ons
    }

def load_cars():
    """Read catalogue data and add calculated prices."""
    create_sample_catalogue()
    cars = []
    with open(CARS_FILE, newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            try:
                row["ex_showroom"] = float(row["ex_showroom"])
                row["prices"] = price_breakdown(row)
                row["on_road"] = row["prices"]["On-road"]
                cars.append(row)
            except (ValueError, KeyError):
                print("Skipping an invalid catalogue row:", row)
    return cars

def money(amount):
    return f"Rs. {amount:,.0f}"

def show_cars(cars):
    if not cars:
        print("No matching cars found.")
        return
    print(f"\n{len(cars)} car(s) found")
    print("-" * 76)
    print(f"{'Brand':<16}{'Model':<24}{'Fuel':<12}{'On-road price':>18}")
    print("-" * 76)
    for car in cars:
        print(f"{car['brand']:<16}{car['model']:<24}{car['fuel']:<12}{money(car['on_road']):>18}")
    print("-" * 76)

def show_price_details(car):
    print(f"\nPrice breakdown for {car['brand']} {car['model']}:")
    for label, amount in car["prices"].items():
        print(f"{label:<20}: {money(amount)}")

def get_number(prompt, minimum=None):
    while True:
        try:
            value = float(input(prompt))
            if minimum is not None and value < minimum:
                print(f"Please enter a value of at least {minimum}.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a number.")

def search_cars(cars):
    term = input("Enter car name or brand: ").strip().lower()
    matches = [c for c in cars if term in c["model"].lower() or term in c["brand"].lower()]
    show_cars(matches)
    if matches:
        show_price_details(matches[0])

def filter_budget(cars):
    low = get_number("Minimum budget in lakh (e.g. 5): ", 0) * 100000
    high = get_number("Maximum budget in lakh: ", 0) * 100000
    if high < low:
        print("Maximum budget cannot be lower than minimum budget.")
        return
    fuel = input("Fuel type (Petrol/Diesel/CNG/Electric/Any): ").strip().lower()
    matches = [c for c in cars if low <= c["on_road"] <= high
               and (fuel in ("", "any") or c["fuel"].lower() == fuel)]
    show_cars(sorted(matches, key=lambda c: c["on_road"]))

def compare_cars(cars):
    show_cars(cars)
    names = input("Enter two or more model names separated by commas: ").lower()
    requested = [x.strip() for x in names.split(",") if x.strip()]
    matches = [c for c in cars if c["model"].lower() in requested]
    if len(matches) < 2:
        print("Please enter at least two exact model names from the catalogue.")
        return
    print("\nCOMPARISON")
    for c in matches:
        print(f"\n{c['brand']} {c['model']} ({c['fuel']})")
        show_price_details(c)

def recommend(cars):
    budget = get_number("Your maximum on-road budget in lakh: ", 0) * 100000
    fuel = input("Preferred fuel (Petrol/Diesel/CNG/Electric/Any): ").strip().lower()
    priority = input("Priority (price/brand): ").strip().lower()
    eligible = [c for c in cars if c["on_road"] <= budget
                and (fuel in ("", "any") or c["fuel"].lower() == fuel)]
    if not eligible:
        print("No cars match these choices. Try a higher budget or another fuel type.")
        return
    # Lower on-road price receives a higher score. Brand priority uses a
    # simple alphabetical ordering to make the result deterministic.
    if priority == "brand":
        ranked = sorted(eligible, key=lambda c: (c["brand"].lower(), c["on_road"]))
    else:
        ranked = sorted(eligible, key=lambda c: c["on_road"])
    print("\nTop recommendations:")
    show_cars(ranked[:5])

def calculate_emi(principal, annual_rate, months):
    if principal <= 0 or months <= 0 or annual_rate < 0:
        raise ValueError("Loan amount and months must be positive; rate cannot be negative.")
    monthly_rate = annual_rate / 1200
    if monthly_rate == 0:
        return principal / months
    factor = (1 + monthly_rate) ** months
    return principal * monthly_rate * factor / (factor - 1)

def emi_planner():
    principal = get_number("Loan amount (Rs.): ", 0.01)
    rate = get_number("Annual interest rate (%): ", 0)
    months = int(get_number("Loan tenure in months: ", 1))
    print("Estimated monthly EMI:", money(calculate_emi(principal, rate, months)))

def save_sale(sale):
    exists = os.path.exists(SALES_FILE)
    with open(SALES_FILE, "a", newline="", encoding="utf-8") as file:
        fields = ["date", "customer", "phone", "brand", "model", "fuel",
                  "on_road", "payment_mode", "loan_amount", "emi"]
        writer = csv.DictWriter(file, fieldnames=fields)
        if not exists:
            writer.writeheader()
        writer.writerow(sale)

def buy_car(cars):
    show_cars(cars)
    model = input("Enter the exact car model to purchase: ").strip().lower()
    matches = [c for c in cars if c["model"].lower() == model]
    if not matches:
        print("Model not found.")
        return
    car = matches[0]
    customer = input("Customer full name: ").strip()
    while not customer:
        print("Name cannot be empty.")
        customer = input("Customer full name: ").strip()
    phone = input("10-digit phone number: ").strip()
    while not (phone.isdigit() and len(phone) == 10):
        print("Please enter exactly 10 digits.")
        phone = input("10-digit phone number: ").strip()
    print("Payment modes: Cash / UPI / Card / Loan")
    mode = input("Choose payment mode: ").strip().title()
    while mode not in ("Cash", "Upi", "Card", "Loan"):
        print("Choose Cash, UPI, Card or Loan.")
        mode = input("Choose payment mode: ").strip().title()
    loan_amount, emi = 0, 0
    if mode == "Loan":
        loan_amount = get_number("Loan amount (Rs.): ", 0.01)
        rate = get_number("Annual interest rate (%): ", 0)
        months = int(get_number("Tenure in months: ", 1))
        emi = calculate_emi(loan_amount, rate, months)
        print("Estimated monthly EMI:", money(emi))
    sale = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "customer": customer, "phone": phone,
        "brand": car["brand"], "model": car["model"], "fuel": car["fuel"],
        "on_road": car["on_road"], "payment_mode": mode,
        "loan_amount": round(loan_amount), "emi": round(emi, 2)
    }
    save_sale(sale)
    print("Sale recorded successfully in sales.csv.")

def view_sales():
    if not os.path.exists(SALES_FILE):
        print("No sales have been recorded yet.")
        return
    with open(SALES_FILE, newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    if not rows:
        print("No sales have been recorded yet.")
        return
    print("\nSALES RECORDS")
    for row in rows:
        print(f"{row['date']} | {row['customer']} | {row['brand']} {row['model']} "
              f"| {money(float(row['on_road']))} | {row['payment_mode']}")

def build_report():
    if not os.path.exists(SALES_FILE):
        print("No sales data available. Record a sale first.")
        return
    with open(SALES_FILE, newline="", encoding="utf-8") as file:
        sales = list(csv.DictReader(file))
    if not sales:
        print("No sales data available.")
        return
    revenue = sum(float(s["on_road"]) for s in sales)
    brand_count = Counter(s["brand"] for s in sales)
    model_count = Counter(s["model"] for s in sales)
    payment_count = Counter(s["payment_mode"] for s in sales)
    lines = [
        "AUTONMIA SHOWROOM - SALES REPORT",
        "=" * 38,
        f"Total sales: {len(sales)}",
        f"Total recorded revenue: {money(revenue)}",
        f"Best-selling brand: {brand_count.most_common(1)[0][0]}",
        f"Best-selling model: {model_count.most_common(1)[0][0]}",
        "",
        "Payment mode split:"
    ]
    lines.extend(f"  {mode}: {count}" for mode, count in payment_count.items())
    report = "\n".join(lines)
    print("\n" + report)
    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        file.write(report)
    print(f"\nReport saved to {REPORT_FILE}.")

def main():
    cars = load_cars()
    print(f"\nWelcome to AutoNmia Showroom! {len(cars)} cars loaded.")
    while True:
        print("""
========== MAIN MENU ==========
1. Browse / search cars
2. Filter cars by budget and fuel
3. Compare cars
4. Recommend a car
5. EMI planner
6. Buy a car
7. View sales records
8. Generate sales report
9. Exit
""")
        choice = input("Enter your choice (1-9): ").strip()
        if choice == "1":
            show_cars(cars)
            search_cars(cars)
        elif choice == "2":
            filter_budget(cars)
        elif choice == "3":
            compare_cars(cars)
        elif choice == "4":
            recommend(cars)
        elif choice == "5":
            emi_planner()
        elif choice == "6":
            buy_car(cars)
        elif choice == "7":
            view_sales()
        elif choice == "8":
            build_report()
        elif choice == "9":
            print("Thank you for visiting AutoNmia Showroom!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 9.")

if __name__ == "__main__":
    main()
