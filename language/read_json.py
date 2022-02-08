import json

with open('language/fr.json') as json_file:
    data = json.load(json_file)
shop = data["SHOP"]

print(data)
print(type(data))
# data = json.dumps(data, ensure_ascii=False, indent=4)

# print(data)
