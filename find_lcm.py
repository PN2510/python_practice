def lcm(a,b):
    if a>b:
        greater = a
    else:
        greater = b

    while(True):
        if (greater%a==0) and (greater%b==0):
            lcm_num=greater
            print(lcm_num)
            break
        greater+=1

    return lcm_num

x = 12
y = 27
lcm(x,y)