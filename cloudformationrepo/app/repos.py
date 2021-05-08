"""Management of repos"""
import os
import boto3
from flask import redirect, url_for
from boto3.dynamodb.conditions import Key
from flask_restful import Resource, reqparse
from app.dynamodbscan import dynoscan

class NewRepos(Resource):
    """Repos class for updating repos"""
    def __init__(self, dynamodb_table):
        super().__init__()
        self.dynamodb_table = dynamodb_table

    def post(self):
        """save a new repo"""
        #pylint: disable=no-self-use
        parser = reqparse.RequestParser()
        parser.add_argument('repouri')
        args = parser.parse_args()

        item = {
            'RepositoryURI': args['repouri'],
            'TemplatePATH': '.'
        }
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(self.dynamodb_table)
        response = table.put_item(Item=item)
        os.system('./repoloader.py')
        return response

class DeleteRepos(Resource):
    """Repos class for delete repos"""
    def __init__(self, s3_bucket, dynamodb_table):
        super().__init__()
        self.dynamodb_table = dynamodb_table
        self.s3_bucket = s3_bucket

    def get(self):
        """delete a repo"""
        #pylint: disable=no-self-use
        parser = reqparse.RequestParser()
        parser.add_argument('repouri')
        args = parser.parse_args()

        dynamodb = boto3.resource('dynamodb')
        s3_client = boto3.client('s3')
        table = dynamodb.Table(self.dynamodb_table)

        scan_kwargs = {
            'FilterExpression': Key('RepositoryURI').eq(args['repouri']),
            'ProjectionExpression': 'RepositoryURI, TemplatePATH'
        }

        allitems = dynoscan(self.dynamodb_table, scan_kwargs)

        with table.batch_writer() as batch:
            for item in allitems:
                batch.delete_item(Key=item)

        s3delete = []
        for item in allitems:
            if item['TemplatePATH'] != '.':
                s3delete = s3delete + [{'Key': item['TemplatePATH'][1:]}]

        if len(s3delete) > 0:
            print(s3delete)
            s3_client.delete_objects(
                Bucket=self.s3_bucket,
                Delete={
                    'Objects': s3delete
                }
            )

        return redirect(url_for('repos'))
