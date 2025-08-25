
def process_numbers(numbers):
    odds = []
    evens = []
    for num in numbers:
        if num % 2 == 0:
            evens.append(num)
        else:
            odds.append(num)
    print("Evens:", evens)
    print("Odds:", odds)
