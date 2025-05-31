def perfect_num(num):
    for i in range(1,num+1):
        if (i%2==0):
            total = 0
            for j in range(1,i):
                if (i%j==0):      
                    total+=j       
            if (total == i):
                print(i)

perfect_num(1000)