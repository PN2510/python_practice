# def prime_num(num):
#     if num == 0 or num == 1:
#         print(num, "is not a prime number")
#     elif num > 1:
num = int(input("Enter a number: "))
for i in range(2,num+1):
    for j in range(2,num+1):
        if i%j == 0:
            break
    if i == j:
        print(i,end=',')
# prime_num(100)