def add_numbers(a, b):
    result = a + b
    return result


x = 5
y = 10
sum_result = add_numbers(x, y)

print(f"The sum of {x} and {y} is: {sum_result}")

if sum_result > 10:
    print("The result is greater than 10.")
else:
    print("The result is not greater than 10.")

print("Finished!")