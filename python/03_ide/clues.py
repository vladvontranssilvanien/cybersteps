# Observe the color of this comment line
investigator_name = "Sherlock Coder"
clue_count = 0

print("Investigator:", investigator_name)


def find_clue(clue_number):
    # Observe the color of the 'def' keyword above
    location = "Study"   # Observe the color of this text string
    global clue_count
    clue_count = clue_count + 1
    print
    (f"Found clue {clue_number} in the {location}. Total clues: {clue_count}")
    # Breakpoint goes here!

# Start typing 'find' below this line. Does VS Code suggest 'find_clue'?


find_clue(1)

# Now start typing 'inv'. Does VS Code suggest 'investigator_name'?
print("Checking investigator:", investigator_name)
# Hover your mouse cursor over the function name 'find_clue' on the line above.
# Hover your mouse cursor over the built-in function name 'print'.
