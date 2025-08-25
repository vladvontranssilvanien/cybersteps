print("═══════════════════════════════════════════════════════")
print("   Welcome to The Cyber Password Quest 🔐")
print("   Step by step, build the ultimate password...")
print("═══════════════════════════════════════════════════════\n")

# First input
password = input("Enter your starting password (at least 5 characters(any)): ")

# Initialize a placeholder to track the last valid password
last_valid = None

# Start an empty list to store only the inputs that passed each rule
accepted_parts = []

# Rule 1
while True:
    if len(password) >= 5:
        print("✅ Rule 1 passed!\n")
    # Update the placeholder with the current password once a rule is passed
        last_valid = password
        # Append means put this item at the end of the list
        accepted_parts.append(password)
        break

    # Ask first, then print error only if still wrong
    password = input("Enter your password: ")
    if len(password) < 5:
        print("❌ Password must be at least 5 characters long. Try again.")

# Rule 2
months = [
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
]

print("Rule 2: Password must contain a Month name.")
while True:
    # Use lowercase for a case-insensitive check
    # 'month' takes each month from list and checks if it's in password
    if any(month in password.lower() for month in months):
        print("✅ Rule 2 passed!\n")
        last_valid = password
        accepted_parts.append(password)
        break

    password = input("Enter your password: ")
    if not any(month in password.lower() for month in months):
        print("❌ Password must contain one month name. Try again.")

# Rule 3
print("Rule 3: Password must contain 'Cy83rPr0j3c7'.")
while True:
    if "Cy83rPr0j3c7" in password:
        print("✅ Rule 3 passed!\n")
        last_valid = password
        accepted_parts.append(password)
        break

    password = input("Enter your password: ")
    if "Cy83rPr0j3c7" not in password:
        print("❌ Password must contain 'Cy83rPr0j3c7'. Try again.")

# Rule 4
print("Rule 4: Password must contain '734mB'.")
while True:
    if "734mB" in password:
        print("✅ Rule 4 passed!\n")
        last_valid = password
        accepted_parts.append(password)
        break

    password = input("Enter your password: ")
    if "734mB" not in password:
        print("❌ Password must contain '734mB'. Try again.")

# Merge only the approved inputs into one string
build_from_correct_only = "".join(accepted_parts)

print("\nCongratulations!")
# Display only the inputs that passed the rules
print("The final password is:", build_from_correct_only)
