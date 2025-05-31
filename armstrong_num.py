def armstrong_num(num):
    num_len = str(num)
    digits = len(num_len)
    total = 0
    num_copy = num
    for i in range(1, digits+1):
        new_num = num%10
        result = new_num**digits
        num//=10
        total+=result
    print(total)
    return total==num_copy

print(armstrong_num(153))