try:
    with open("payment_debug.log", "r") as f:
        print(f.read())
except FileNotFoundError:
    print("Log file not found.")
