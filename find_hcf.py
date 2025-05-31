def find_hcf(a,b):
    if a>b:
        smaller = b
    else:
        smaller = a
    
    for i in range(1, smaller + 1):
        if (a % i == 0) and (b % i == 0):
            hcf_num = i

    return hcf_num

x = 3
y = 21

print(find_hcf(x,y))