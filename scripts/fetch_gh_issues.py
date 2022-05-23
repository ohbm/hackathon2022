#!/bin/env python
from multiprocessing.sharedctypes import Value
import requests
import re
import yaml

issue_form = yaml.safe_load(open('.github/ISSUE_TEMPLATE/hackathon-project-form.yml'))
fields = issue_form['body']
fields = [f for f in fields if f['type'] != 'markdown']

url = 'https://api.github.com/repos/ohbm/hackathon2022/issues?labels=Hackathon Project'

issues = requests.get(url).json()
issues_list = []
for issue in issues:
    if "Hacktrack: Good to go" not in [i['name'] for i in issue["labels"]]:
         continue

    if issue["state"] != "open":
        continue

    body = issue["body"]
    lines = [l.strip() for l in body.replace('\r\n', '\n').split('\n')]

    field_ordering = []
    for field in fields:
        field_start = None
        field_label = field['attributes']['label']
        
        for li, line in enumerate(lines):
            if field_start is None and line.startswith(f'### {field_label}'):
                field_start = li

        field_ordering += [(field, field_start)]
    field_ordering = list(sorted(field_ordering, key=lambda f: f[1]))

    issue_info = {}

    for (field, i), (_, ni) in zip(field_ordering, field_ordering[1:] + [(None, None)]):
        field_id = field['id']
        field_label = field['attributes']['label']

        if i is None:
            issue_info[field_id] = None
            continue

        field_value = '\n'.join(filter(None, lines[i+1:ni]))
        field_value = re.sub(r'<!--.*?-->', '', field_value, flags=re.DOTALL)
        field_value = field_value.strip()

        if field_value == '_No response_':
            field_value = None

        if field['type'] == 'checkboxes':
            field_options_labels = [o['label'].strip() for o in field['attributes']['options']]
            field_selected_options = []
            field_options_value = field_value.split('\n')
            for l in field_options_value:
                if l[6:] not in field_options_labels:
                    continue
                if l.startswith('- [X] '):
                    field_selected_options.append(l[6:])
                if l.startswith('- [x] '):
                    field_selected_options.append(l[6:])

            field_value = field_selected_options

        issue_info[field_id] = field_value

    if issue_info['hub'] in issue_info['otherhub']:
        issue_info['otherhub'].remove(issue_info['hub'])

    issue_info['issue_link'] = issue["html_url"]
    issue_info['issue_number'] = issue["number"]

    from pprint import pprint
    pprint(issue_info)

    issues_list.append(issue_info)

with open('./_data/projects.yml', 'w') as f:
    yaml.dump(issues_list, f, default_flow_style=False)
