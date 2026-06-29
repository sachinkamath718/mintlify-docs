import os
import re

# Load token -> local path mapping
token_map = {}
with open("token-map.txt", "r") as f:
    for line in f:
        line = line.strip()
        if "|" in line:
            token, local = line.split("|", 1)
            token_map[token] = local

print(f"Loaded {len(token_map)} mappings")

# Update all MDX files
updated = 0
for root, dirs, files in os.walk("condense"):
    for file in files:
        if not file.endswith(".mdx"):
            continue
        
        filepath = os.path.join(root, file)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        new_content = content
        for token, local in token_map.items():
            # Match any URL containing this token
            pattern = r'https://[^\s"\')\]]*' + re.escape(token) + r'[^\s"\')\]]*'
            new_content = re.sub(pattern, local, new_content)
        
        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated: {filepath}")
            updated += 1

print(f"\nDone! Updated {updated} files")
