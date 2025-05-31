def euclidean_gcd(a,b):
    if(a==0):
        return b
    if(b==0):
        return a
    if(a==b):
        return a
    if(a>b):
        return euclidean_gcd(a-b, b)
    else:
        return euclidean_gcd(a, b-a)
    
print(euclidean_gcd(98,56))