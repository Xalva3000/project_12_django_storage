lst = list(range(5, 30000+1))
print(*[num**2 for num in lst])

def pow2(num):
    return num ** 2


# print(*map(pow2, lst))
print(*filter(lambda num: num%2==0, lst))