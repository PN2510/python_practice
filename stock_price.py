price_array=[{"name":"stock9", "price":10},
            {"name": "stock5", "price": 30},
            {"name": "stock4", "price": 45},
            {"name": "stock3", "price": 60},
            {"name": "stock2", "price": 80},
            {"name": "stock7", "price": 100},
            {"name": "stock6", "price": 120},
            {"name": "stock10", "price": 130},
            {"name": "stock1", "price": 160},
            {"name": "stock8", "price": 200}]
sorted_price_array=sorted(price_array, key=lambda x: x["price"], reverse=True)
print(sorted_price_array)
percentage_differences = []
for i in range(len(sorted_price_array) - 1):
    high_price = sorted_price_array[i]["price"]
    low_price = sorted_price_array[i + 1]["price"]

    
    percentage_diff = ((high_price - low_price) / high_price) * 100
    percentage_differences.append((sorted_price_array[i]["name"], sorted_price_array[i+1]["name"], round(percentage_diff, 2)))

# for stock1, stock2, diff in percentage_differences:
#     print(f"Percentage difference between {stock1} and {stock2}: {diff}%")

top_3_differences = sorted(percentage_differences, key=lambda x: x[2], reverse=True)[:3]

print("Top 3 percentage differences:")
for stock1, stock2, diff in top_3_differences:
    print(f"Percentage difference between {stock1} and {stock2}: {diff}%")