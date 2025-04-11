from tabulate import tabulate

data = [
    {'Name': 'Alice', 'Age': 25, 'Job': 'Engineer'},
    {'Name': 'Bob', 'Age': 30, 'Job': 'Designer'},
    {'Name': 'Charlie', 'Age': 35, 'Job': 'Teacher'},
]

md = tabulate(data, headers="keys", tablefmt="github")
print(md)
