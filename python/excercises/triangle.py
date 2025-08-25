# Input
a = int(input("Enter length of side 1: "))
b = int(input("Enter length of side 2: "))
c = int(input("Enter length of side 3: "))

# Checking if the sides have a positive value
if (a <= 0) or (b <= 0) or (c <= 0):
    print("Cannot form a triangle.")

# Checking if the sum of two sides is greater than the third
elif (a + b > c) and (a + c > b) and (b + c > a):

    # Clasification
    if (a == b) and (b == c):
        print("Equilateral triangle")
    elif (a == b) or (a == c) or (b == c):
        print("Isosceles triangle")
    else:
        print("Scalene triangle")
else:
    print("Cannot form a triangle.")
