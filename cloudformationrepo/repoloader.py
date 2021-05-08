#!/usr/bin/env python3
"""
Read a list of repositories from DynamoDB and for each checkout and load the metadata into DynamoDB
"""

import json
import logging
import os
import tempfile
import boto3
from boto3.dynamodb.conditions import Key
import git
import yaml

logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO'))

dynamodb = boto3.resource('dynamodb')
dynamodb_table = os.environ.get('DYNAMODB_TABLE', 'cfrepo-CfrTable1A89E739-1ZY9KC03VF18')
table = dynamodb.Table(dynamodb_table)
s3_bucket = os.environ.get('S3_BUCKET', 'cfrepo-cfrbucket9fd76711-prrb50pqbm31')

s3 = boto3.client('s3')

scan_kwargs = {
        'FilterExpression': Key('TemplatePATH').eq('.')
        }

allitems = []

DONE = False
START_KEY = None
while not DONE:
    if START_KEY:
        scan_kwargs['ExclusiveStartKey'] = START_KEY
    response = table.scan(**scan_kwargs)
    allitems = allitems + response.get('Items', [])
    START_KEY = response.get('LastEvaluatedKey', None)
    DONE = START_KEY is None

allrepos = []
for item in allitems:
    allrepos = allrepos + [item['RepositoryURI']]

allrepos = list(dict.fromkeys(allrepos))

for repo in allrepos:
    logging.info("Working on Repository: %s", repo)
    with tempfile.TemporaryDirectory() as tmpdirname:
        try:
            git.Git(tmpdirname).clone(repo)
        except git.CommandError as error:
            logging.error("Error cloning repository: %s", error)
            continue

        for dirName, subdirList, fileList in os.walk(tmpdirname):
            subdirList[:] = [d for d in subdirList if d not in ['.git']]
            logging.info('Found directory: %s', dirName)
            for fname in fileList:
                try:
                    with open(os.path.join(dirName, fname)) as f:
                        template = json.load(f)
                except json.JSONDecodeError:
                    try:
                        with open(os.path.join(dirName, fname)) as f:
                            template = yaml.load(f, Loader=yaml.BaseLoader)
                    except yaml.scanner.ScannerError:
                        logging.error("File: %s, doesn't appear to be a json or yaml file.", fname)
                        continue
                if 'AWSTemplateFormatVersion' not in template:
                    logging.error("File: %s, doesn't appear to be a CloudFormation template", fname)
                    continue

                DESCRIPTION = ''
                PARAMETERS = []
                if 'Description' in template:
                    DESCRIPTION = template['Description']
                if 'Parameters' in template:
                    PARAMETERS = set(template['Parameters'].keys())
                item = {
                    'RepositoryURI': repo,
                    'TemplateDescription': DESCRIPTION,
                    'TemplatePATH': os.path.join(dirName.replace(tmpdirname, ''), fname),
                    'TemplateParameters': PARAMETERS
                }
                response = table.put_item(Item=item)
                logging.debug(response)
                response = s3.upload_file(
                    os.path.join(dirName, fname),
                    s3_bucket, os.path.join(dirName.replace(tmpdirname, ''),
                    fname)[1:],
                    ExtraArgs={'ACL': 'public-read'})
                logging.debug(response)
