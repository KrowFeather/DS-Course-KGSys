import json

with open('./data/all_desc.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    print(data)

for item in data:
    print(item['name'])