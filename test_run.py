import json
from main import process_image

with open('test.json', 'r') as f:
    data = json.load(f)

results = []
for item in data:
    image_b64 = item['image']
    value = process_image(image_b64)
    results.append({'value': value})

print(json.dumps(results))
