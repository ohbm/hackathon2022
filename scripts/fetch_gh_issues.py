#!/bin/env python
from multiprocessing.sharedctypes import Value
import requests
import re
import yaml

url = 'https://api.github.com/repos/ohbm/hackathon2022/issues'

resp = requests.get(url)
issues = resp.json()

issues_list = []
for issue in issues:
    if "Hacktrack: Good to go" not in [i['name'] for i in issue["labels"]]:
        continue

    if issue["state"] != "open":
        continue

    body = issue["body"]

    fields = [
        'Title',
        'Project leaders with Mattermost handle and GitHub login',
        '[In-person/online]',
        'Description',
        'Link to project',
        'Goals for the OHBM Brainhack',
        'Skills',
        'List of recommended tutorials',
        'Good first issues',
        'Chat channel',
        'Image for the OHBM brainhack website'
    ]

    field_mapping = dict(zip(fields, [
        'title',
        'project_leaders',
        'project_type',
        'description',
        'project_link',
        'hackathon_goals',
        'skills',
        'tutorials',
        'good_first_issues',
        'chat_channel',
        'image'
    ]))

    lines = body.split('\r\n')
    issue_dict = {}

    for field in fields:
        field_start, field_end = None, None
        for li, line in enumerate(lines):
            if field_start is None and line.startswith(f'**{field}**'):
                field_start = li

            elif field_start is not None and field_end is None and (line.startswith('**') or line.startswith('##')):
                field_end = li
                break

        if field_start is None or field_end is None:
            raise ValueError(f'Missing field "{field}" for issue {issue["html_url"]}')
            # TODO make bot add comment to issue about the missing field
            break

        field_value = '\n'.join(lines[field_start+1:field_end])
        field_value = re.sub(r'<!--.*?-->', '', field_value, flags=re.DOTALL)
        field_value = field_value.strip()

        if field_mapping[field] == 'project_type':
            if field_value.lower().startswith('online'):
                field_value = [
                    x.strip() for x in re.split('[,\n\r]', field_value)
                    if x.strip() != ''
                ]
                issue_dict['timeslot'] = re.sub(r'[^\w]', '', field_value[1].lower())
                field_value = 'online'

        if field_mapping[field] == 'project_leaders':
            field_value = [
                x.strip() for x in re.split(r'[,\n\r]', field_value)
                if x.strip() != ''
            ]

        if field_mapping[field] == 'image':
            if field_value == '':
                field_value = None

        if field_mapping[field] == 'skills':
            field_value = [
                x.strip() for x in re.split(r'[,\n\r]', field_value)
                if x.strip() != ''
            ]

        issue_dict[field_mapping[field]] = field_value

    issue_dict['issue_link'] = issue["html_url"]
    issue_dict['issue_number'] = issue["number"]

    issues_list.append(issue_dict)

with open('./_data/projects.yml', 'w') as f:
    yaml.dump(issues_list, f, default_flow_style=False)