#!/usr/bin/env python3

import json
import os
import re
import sys

from pathlib import Path

from datetime import datetime, timezone

from notion.client import NotionClient
from notion.block import CollectionViewPageBlock
from notion.block import TextBlock, CodeBlock, DividerBlock
from notion.operations import build_operation

# set this to the token_v2 cookie from an authenticated Notion session
notion_token_v2 = 'YOUR_TOKEN_HERE'

# set this to a page where the journal will be created
archive_page_url = 'https://www.notion.so/XXXXXXXXXXXXXXXXXXXXXXXXX'

# setting this to True will dump the raw journal data to the page
include_raw = False

################################################################################

client = NotionClient(token_v2=notion_token_v2)
source_file = sys.argv[1]
archive_page = client.get_block(archive_page_url)

journal_schema = {
    'title' : { 'slug': 'title', 'name': 'Title', 'type': 'title' },
    'ibAI' : { 'slug': 'date', 'name': 'Date', 'type': 'date' },
    'vFRD' : { 'slug': 'favorite', 'name': 'Favorite', 'type': 'checkbox' },
    'zDBI' : { 'slug': 'location', 'name': 'Location', 'type': 'text' },
    '<eV@' : { 'slug': 'longitude', 'name': 'Longitude', 'type': 'number' },
    '{v;_' : { 'slug': 'latitude', 'name': 'Latitude', 'type': 'number' },
    '%ojF' : { 'slug': 'activity', 'name': 'Activity', 'type': 'text' },
    'K7@f' : { 'slug': 'step_count', 'name': 'Step Count', 'type': 'number' },
    'aMpU' : { 'slug': 'weather', 'name': 'Weather', 'type': 'text' },
    ':OIX' : { 'slug': 'device', 'name': 'Device', 'type': 'text' },
    'Ct_;' : { 'slug': 'id', 'name': 'ID', 'type': 'text' },
    'nOAw' : {
        'slug': 'tags',
        'name': 'Tags',
        'type': 'multi_select',
        "options": [
            { "id": "dd3500bb-eb53-4c74-9c4b-2f84d508acde", "value": "Day One" }
        ]
    }
}

journal_name = Path(source_file).stem
print(f'Importing journal: {journal_name}')
journal_page = archive_page.children.add_new(CollectionViewPageBlock)

journal = client.get_collection(
    client.create_record('collection', parent=journal_page, schema=journal_schema)
)

journal_page.collection = journal
journal_page.views.add_new(view_type='table')
journal_page.title = journal_name

with open(source_file) as fp:
    source_data = json.load(fp)

for entry in source_data['entries']:
    if 'text' not in entry: continue

    text = entry['text'].splitlines(keepends=False)
    title = text[0]
    body = "\n".join(text[1:])
    print(f'Adding entry: {title}')

    row = journal.add_row()
    row.title = title
    row.id = entry['uuid']

    # make the date compliant for python parsing; convert to local timezone
    date_str = entry['creationDate'].rstrip('Z')
    date = datetime.fromisoformat(date_str)
    row.date = date.replace(tzinfo=timezone.utc).astimezone(tz=None)

    row.tags = [ 'Day One' ]
    if 'tags' in entry:
        row.tags += entry['tags']

    if 'starred' in entry and entry['starred']:
        row.favorite = True

    if 'location' in entry:
        place = entry['location']
        row.location = place['placeName']
        row.longitude = place['longitude']
        row.latitude = place['latitude']

    if 'userActivity' in entry:
        activity = entry['userActivity']
        row.activity = activity['activityName']
        if activity['stepCount'] > 0:
            row.step_count = activity['stepCount']

    if 'stepCount' in entry:
        row.step_count = entry['stepCount']

    if 'weather' in entry:
        wx = entry['weather']
        row.weather = wx['conditionsDescription']

    if 'creationDevice' in entry:
        row.device = entry['creationDevice']

    # TODO put photos & videos in the right place
    row.children.add_new(TextBlock, title=body)

    if include_raw:
        row.children.add_new(DividerBlock)
        row.children.add_new(
            CodeBlock,
            language='json',
            wrap=True,
            title=json.dumps(entry)
        )

