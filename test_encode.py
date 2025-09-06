import base64

with open('MST-images/graph0.png', 'rb') as f:
    image_data = f.read()
    b64 = base64.b64encode(image_data).decode('utf-8')
    data = [{"image": b64}]
    import json
    print(json.dumps(data))
