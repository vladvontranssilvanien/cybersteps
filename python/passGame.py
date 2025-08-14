print("Welcome to The Cyber Password Quest 🔐")
print("Step by step, build the ultimate password...")

# Rule 1
password = input("Rule 1: Password must start with 'W': ")
if not password.startswith("W"):
    print("❌ Wrong ending! Try again.")
    print("💀 Game Over")
else:
    print("✅ Rule 1 passed!")

    # Rule 2
    password = input("Rule 2: Add numbers '34' after W: ")
    if password != "W34":
        print("❌ Wrong ending! Try again.")
        print("💀 Game Over")
    else:
        print("✅ Rule 2 passed!")

        # Rule 3
        password = input("Rule 3: Continue with 'r37h3': ")
        if password != "W34r37h3":
            print("❌ Wrong ending! Try again.")
            print("💀 Game Over")
        else:
            print("✅ Rule 3 passed!")

            # Rule 4
            password = input("Rule 4: Add 'Cy83r734MB': ")
            if password != "W34r37h3Cy83r734MB":
                print("❌ Wrong ending! Try again.")
                print("💀 Game Over")
            else:
                print("✅ Rule 4 passed!")

                # Final Rule
                password = input("Final Rule: End with '!!!': ")
                if password == "W34r37h3Cy83r734MB!!!":
                    print("Congrats, you unlocked the Cyber Password 🛡️🤖🦾🦿!!!")
                else:
                    print("❌ Wrong ending! Try again.")
                    print("💀 Game Over")
