#!/usr/bin/env python3

import json
import os
import re
import sys
import argparse

from pathlib import Path
from datetime import datetime, timezone
from notion.client import NotionClient

from notion.block import CollectionViewPageBlock, ImageBlock, VideoBlock, PDFBlock
from notion.block import TextBlock, CodeBlock, DividerBlock

from notion.operations import build_operation
from notion.markdown import markdown_to_notion

import md2notion.upload as md2notion

################################################################################
moment_re = re.compile(r'dayone-moment:/(.*)?/([a-fA-F0-9]{32})')
def moment_to_block(entry, block):
    moment = block['source']
    m = moment_re.match(moment)
    if not m: return None

    #TODO use named groups
    moment_type = m.groups()[0]
    moment_id = m.groups()[1]

    if moment_type == '':
        folder = 'photos'
        section = entry['photos']
        block['type'] = ImageBlock
    elif moment_type == 'video':
        folder = 'videos'
        section = entry['videos']
        block['type'] = VideoBlock
    elif moment_type == 'pdfAttachment':
        folder = 'pdfs'
        section = entry['pdfAttachments']
        block['type'] = PDFBlock
    else:
        return None

    item = next(item for item in section if item['identifier'] == moment_id)
    filename = f'{item["md5"]}.{item["type"]}'
    block['source'] = os.path.join(folder, filename)

    return block

################################################################################
argp = argparse.ArgumentParser(description='mycomix')

argp.add_argument('--token', dest='token_v2', required=True)
argp.add_argument('--page', dest='page', required=True)
argp.add_argument('--raw', dest='raw', action='store_true', default=False)
argp.add_argument('files', nargs='+')

args = argp.parse_args()

# TODO custom retry for 50x errors
client = NotionClient(token_v2=args.token_v2)
archive_page = client.get_block(args.page)

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

for source_file in args.files:
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
            if 'activityName' in activity:
                row.activity = activity['activityName']
            if 'stepCount' in activity and activity['stepCount'] > 0:
                row.step_count = activity['stepCount']

        if 'stepCount' in entry:
            row.step_count = entry['stepCount']

        if 'weather' in entry:
            wx = entry['weather']
            if 'conditionsDescription' in wx:
                row.weather = wx['conditionsDescription']

        if 'creationDevice' in entry:
            row.device = entry['creationDevice']

        blocks = md2notion.convert(body)
        for block in blocks:
            if block['type'] is ImageBlock:
                block = moment_to_block(entry, block)
                if block is None: continue

            md2notion.uploadBlock(block, row, source_file)

        if args.raw:
            row.children.add_new(DividerBlock)
            row.children.add_new(
                CodeBlock,
                language='json',
                wrap=True,
                title=json.dumps(entry)
            )

