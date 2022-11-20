# Раз в час: https://ru.stackoverflow.com/questions/1173308/

import copy

a = ["a", "b", "c", "d", "e\n"]

b = copy.copy(a)

for item in a:
    print(item)
    if '\n' not in item:
        b.remove(item)
a = copy.copy(b)
print(a)