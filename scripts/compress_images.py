import glob
import hashlib
import os
import re
import shutil

import traceback
import requests
import yaml
from PIL import Image
from cairosvg import svg2png


IMAGE_SIZE = 400
GH_TOKEN = os.getenv('GH_TOKEN')
REPO = os.getenv('REPO')

os.makedirs('img/projects', exist_ok=True)
already_processed = glob.glob('img/projects/*.png')

with open('_data/projects.yml', 'r') as f:
    projects = yaml.safe_load(f)

    for i, data in enumerate(projects):
        name = data['chatchannel']
        image_url = data['website-image']
        issue_number = data['issue_number']
        issue_link = data['issue_link']

        try:
            # No image for the project
            if image_url is None:
                continue

            # Skip if already processed, running twice is fine
            if image_url.startswith('img/projects'):
                del already_processed[already_processed.index(image_url)]
                continue

            # Let `requests` handle the URL validation
            pattern = r'(https?://[^\s]+)'
            image_url_search = re.search(pattern, image_url)
            if not image_url:
                raise Exception(f'Invalid image "{image_url}"')
            image_url = image_url_search.group(0)
            image_url_pieces = image_url.split('/')

            # Fix Github hosted images
            if image_url_pieces[2] == 'github.com' and image_url_pieces[5] == 'blob':
                image_url_pieces[5] = 'raw'
                image_url = '/'.join(image_url_pieces)

            # Fix Google Drive hosted images
            if image_url_pieces[2] == 'drive.google.com' and image_url_pieces[3] == 'file':
                image_url = 'https://drive.google.com/uc?id=' + image_url_pieces[5]

            url_hash = hashlib.sha1(image_url.encode("utf-8")).hexdigest()
            image_filename = f'img/projects/{url_hash}.png'

            if image_filename in already_processed:
                del already_processed[already_processed.index(image_filename)]
                data['website-image'] = image_filename
                continue

            r = requests.get(image_url, stream = True)
            if r.status_code == 200:
                r.raw.decode_content = True
                filetype = r.headers.get('content-type')
                if filetype == 'image/svg+xml':
                    svg2png(bytestring=r.content, write_to=image_filename)
                else:
                    # No worries about extension, PIL will figure it out
                    with open(image_filename, 'wb') as f:
                        shutil.copyfileobj(r.raw, f)

            image = Image.open(image_filename)
            image.thumbnail(size=(IMAGE_SIZE, IMAGE_SIZE))
            image.save(image_filename, optimize=True, quality=90)

            data['website-image'] = image_filename

            print(f'Processed project {name}')

        except Exception as e:
            # requests.post(
            #     f'https://api.github.com/repos/{REPO}/issues/{issue_number}/comments',
            #     headers={
            #         'Authorization': f'token {GH_TOKEN}',
            #         'Accept': 'application/vnd.github.v3+json',
            #         'Content-Type': 'application/json'
            #     },
            #     json={
            #         'body': f'Failed to process image: {e}'
            #     }
            # )

            print(f'Failed to process image from project {issue_link}:')
            print(f'Image URL: {image_url}')
            traceback.print_exc()
            break

    for old_image in already_processed:
        os.remove(old_image)

    with open('_data/projects.yml', 'w') as f:
        yaml.dump(projects, f, default_flow_style=False)
