import json

with open('language/fr.json') as json_file:
    data = json.load(json_file)
SHOP = data["SHOP"]

print(SHOP)
print(type(SHOP))
print("\n\n")
print(SHOP[0])
print(SHOP[0]["name"])
# data = json.dumps(data, ensure_ascii=False, indent=4)

# print(data)
