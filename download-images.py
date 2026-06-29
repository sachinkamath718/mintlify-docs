import os
import re
import requests
from urllib.parse import unquote

# Find all gitbook CDN URLs in MDX files
urls = set()
for root, dirs, files in os.walk('condense'):
    for file in files:
        if file.endswith('.mdx'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            found = re.findall(r'https://files\.gitbook\.com/v0/b/[^\s"\')\]]+', content)
            urls.update(found)

print(f"Found {len(urls)} unique image URLs")

os.makedirs('images/gitbook', exist_ok=True)

url_to_local = {}
for url in urls:
    # Use the last part of the URL as filename
    filename = url.split('%2F')[-1]
    filename = unquote(filename).replace(' ', '-')
    local_path = f'images/gitbook/{filename}'
    
    if not os.path.exists(local_path):
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                with open(local_path, 'wb') as f:
                    f.write(r.content)
                print(f"Downloaded: {filename}")
            else:
                print(f"Failed ({r.status_code}): {url}")
        except Exception as e:
            print(f"Error: {e}")
    
    url_to_local[url] = f'/images/gitbook/{filename}'

# Now replace URLs in all MDX files
for root, dirs, files in os.walk('condense'):
    for file in files:
        if file.endswith('.mdx'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            for url, local in url_to_local.items():
                new_content = new_content.replace(url, local)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated: {filepath}")

print("Done!")
