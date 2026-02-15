#!/usr/bin/env python3
import re
import base64
import sys
from pathlib import Path

def parse_chat(chat_file):
    """Parse WhatsApp _chat.txt file"""
    wines = []
    with open(chat_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Find photo attachment
        if '<attached:' in line and '.jpg' in line.lower():
            photo_match = re.search(r'<attached: (.+?)>', line)
            if photo_match:
                photo_name = photo_match.group(1)
                # Next line should be rating + comment
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    # Extract rating (first digit)
                    rating_match = re.search(r'(\d+)', next_line.split(']')[-1])
                    if rating_match:
                        rating = int(rating_match.group(1))
                        if rating > 10:
                            rating = 10
                        # Extract comment (everything after rating)
                        comment = re.sub(r'^\d+\s*', '', next_line.split(']')[-1]).strip()
                        wines.append({
                            'photo': photo_name,
                            'rating': rating,
                            'comment': comment
                        })
        i += 1
    
    return wines

def image_to_base64(image_path):
    """Convert image to base64 string"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def generate_html(wines, export_dir):
    """Generate single HTML file with embedded images (no OCR)"""
    html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wine Ratings</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 10px; background: #f5f5f5; }
        .search { position: sticky; top: 0; background: white; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 10px; z-index: 100; }
        input { width: 100%; padding: 10px; font-size: 16px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .wine { background: white; margin: 10px 0; padding: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .wine img { width: 100%; max-width: 400px; border-radius: 4px; }
        .rating { font-size: 32px; font-weight: bold; color: #d4af37; margin: 10px 0; }
        .comment { color: #666; font-style: italic; margin: 10px 0; font-size: 16px; }
    </style>
</head>
<body>
    <div class="search">
        <input type="text" id="searchInput" placeholder="Cerca vino..." onkeyup="filterWines()">
    </div>
    <div id="wines">
'''
    
    # Sort by rating (highest first)
    wines_sorted = sorted(wines, key=lambda x: x['rating'], reverse=True)
    
    for wine in wines_sorted:
        photo_path = export_dir / wine['photo']
        if photo_path.exists():
            # Base64
            img_base64 = image_to_base64(photo_path)
            
            html += f'''
        <div class="wine" data-search="{wine['comment'].lower()}">
            <img src="data:image/jpeg;base64,{img_base64}">
            <div class="rating">{wine['rating']}/10</div>
            <div class="comment">{wine['comment']}</div>
        </div>
'''
    
    html += '''
    </div>
    <script>
        function filterWines() {
            const input = document.getElementById('searchInput').value.toLowerCase();
            const wines = document.querySelectorAll('.wine');
            wines.forEach(wine => {
                const searchText = wine.getAttribute('data-search');
                wine.style.display = searchText.includes(input) ? 'block' : 'none';
            });
        }
    </script>
</body>
</html>
'''
    return html

def main():
    if len(sys.argv) < 2:
        print("Usage: python wine_ratings.py /path/to/whatsapp/export/")
        sys.exit(1)
    
    export_dir = Path(sys.argv[1])
    chat_file = export_dir / '_chat.txt'
    
    if not chat_file.exists():
        print(f"Error: {chat_file} not found")
        sys.exit(1)
    
    print("Parsing chat...")
    wines = parse_chat(chat_file)
    print(f"Found {len(wines)} wines")
    
    print("Generating HTML...")
    html = generate_html(wines, export_dir)
    
    output_file = export_dir / 'wine_ratings.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Done! Open {output_file}")

if __name__ == '__main__':
    main()
