def count_odd_even(num):
    even_count = 0
    odd_count = 0
    while(num>0):
        rem = num % 10
        if (rem % 2 == 0):
            even_count+=1
        else:
            odd_count+=1
        num//=10
    print(even_count)
    print(odd_count)

count_odd_even(2121)