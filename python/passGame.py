print("═══════════════════════════════════════════════════════")
print("   Welcome to The Cyber Password Quest 🔐")
print("   Step by step, build the ultimate password...")
print("═══════════════════════════════════════════════════════\n")

# Rule 1
password = input("🧩 Rule 1: Password must start with 'W'\n👉 Enter here: ")
if not password.startswith("W"):
    print("\n❌ Wrong ending! Try again.")
    print("💀 GAME OVER")
else:
    print("✅ Rule 1 passed!\n")

    # Rule 2
    password = input("🧩 Rule 2: Add numbers '34' after W\n👉 Enter here: ")
    if password != "W34":
        print("\n❌ Wrong ending! Try again.")
        print("💀 GAME OVER")
    else:
        print("✅ Rule 2 passed!\n")

        # Rule 3
        password = input("🧩 Rule 3: Continue with 'r37h3'\n👉 Enter here: ")
        if password != "W34r37h3":
            print("\n❌ Wrong ending! Try again.")
            print("💀 GAME OVER")
        else:
            print("✅ Rule 3 passed!\n")

            # Rule 4
            password = input("🧩 Rule 4: Add 'Cy83r734MB'\n👉 Enter here: ")
            if password != "W34r37h3Cy83r734MB":
                print("\n❌ Wrong ending! Try again.")
                print("💀 GAME OVER")
            else:
                print("✅ Rule 4 passed!\n")

                # Final Rule
                password = input("FINAL RULE: End with '!!!'\n👉 Enter here: ")
                if password == "W34r37h3Cy83r734MB!!!":
                    print("\n🎉 Congrats, you unlocked the Cyber Password!!!")
                    print("══════════════════════════════════════════════════")
                    print("      ACCESS GRANTED — SYSTEM SECURED 🔒")
                    print("══════════════════════════════════════════════════")
                else:
                    print("\n❌ Wrong ending! Try again.")
                    print("💀 GAME OVER")
