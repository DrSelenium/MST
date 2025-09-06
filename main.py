from flask import Flask, request, jsonify
import cv2
import numpy as np
import pytesseract
import base64
from PIL import Image
import io

app = Flask(__name__)

# Set the tesseract_cmd to the installed location of Tesseract-OCR on your machine
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def process_image(image_b64):
    # Decode base64
    image_data = base64.b64decode(image_b64)
    image = Image.open(io.BytesIO(image_data))
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect nodes (black circles)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=10, maxRadius=30)
    nodes = []
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            nodes.append((x, y))
    
    # Detect edges using HoughLinesP
    edges = cv2.HoughLinesP(gray, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
    graph_edges = []
    if edges is not None:
        for line in edges:
            x1, y1, x2, y2 = line[0]
            # Find closest nodes to line ends
            n1 = min(nodes, key=lambda n: (n[0]-x1)**2 + (n[1]-y1)**2)
            n2 = min(nodes, key=lambda n: (n[0]-x2)**2 + (n[1]-y2)**2)
            if n1 != n2:
                # Midpoint for OCR
                mx = (x1 + x2) // 2
                my = (y1 + y2) // 2
                # Crop around midpoint
                crop = image[max(0, my-10):my+10, max(0, mx-20):mx+20]
                if crop.size > 0:
                    text = pytesseract.image_to_string(crop, config='--psm 8 -c tessedit_char_whitelist=0123456789')
                    try:
                        weight = int(text.strip())
                        graph_edges.append((n1, n2, weight))
                    except ValueError:
                        pass  # Skip if not a number
    
    # Map nodes to indices
    node_dict = {node: i for i, node in enumerate(nodes)}
    edges_list = []
    for n1, n2, w in graph_edges:
        if n1 in node_dict and n2 in node_dict:
            i1 = node_dict[n1]
            i2 = node_dict[n2]
            edges_list.append((w, i1, i2))
    
    # Kruskal's algorithm
    edges_list.sort()
    parent = list(range(len(nodes)))
    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    def union(x, y):
        px = find(x)
        py = find(y)
        if px != py:
            parent[px] = py
            return True
        return False
    mst_weight = 0
    for w, u, v in edges_list:
        if union(u, v):
            mst_weight += w
    return mst_weight

@app.route('/mst-calculation', methods=['POST'])
def mst_calculation():
    data = request.get_json()
    results = []
    for item in data:
        image_b64 = item['image']
        value = process_image(image_b64)
        results.append({'value': value})
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)