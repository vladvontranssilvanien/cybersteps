signals = [0, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0]
count_of_ones = signals.count(1)
if 1 in signals:
    first_index = signals.index(1)
    last_index = len(signals) - 1 - signals[::-1].index(1)
else:
    first_index = -1
    last_index = -1

print("count_of_ones:", count_of_ones)
print("first_index:", first_index)
print("last_index:", last_index)