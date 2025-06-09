def  is_prime(n):
    if n<=1:
        return False
    if n==2:
        return True
    for i in range(2, int(n**0.5)+1):
        if n%i==0:
            return False
    return True

def num_expressed_as_sum_of_primes(n):
    for i in range(2, (n//2)+1):
        if is_prime(i) and is_prime(n-i):
            print(f"{n} = {i} + {n-i}")
            return True
    return False
    
print(num_expressed_as_sum_of_primes(9))