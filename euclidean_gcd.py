def euclidean_gcd(a,b):
    greater = 0
    smaller = 0
    if a>b:
        a=greater
    else:
        a=smaller
    if b>a:
        b=greater
    else:
        b=smaller
    
    res = greater/smaller
    print(res)

euclidean_gcd(5,10)