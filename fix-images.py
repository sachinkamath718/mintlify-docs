import os
import re
from urllib.parse import unquote

def fix_images(content):
    # Match image paths that contain gitbook CDN encoded paths
    pattern = r'(/images/[^\s"\']+files%2Fv0%2Fb%2Fgitbook-x-prod\.appspot\.com%2Fo%2F[^\s"\')\]]+)'
    
    def replace_url(match):
        encoded = match.group(1)
        # Extract the gitbook path part
        gitbook_part = re.search(r'files%2Fv0%2Fb%2Fgitbook-x-prod\.appspot\.com%2Fo%2F(.+)', encoded)
        if gitbook_part:
            decoded = unquote(gitbook_part.group(1))
            return f'https://files.gitbook.com/v0/b/{decoded}'
        return encoded
    
    return re.sub(pattern, replace_url, content)

# Walk all MDX files
for root, dirs, files in os.walk('condense'):
    for file in files:
        if file.endswith('.mdx'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = fix_images(content)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Fixed: {filepath}')

print('Done!')
