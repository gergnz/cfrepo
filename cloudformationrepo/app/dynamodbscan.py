"""A DynamoDB Scan Wrapper"""
import boto3

def dynoscan(dynamodb_table, scan_kwargs):
    """DynamoDB Scan Wrapper"""

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(dynamodb_table)

    allitems = []

    done = False
    start_key = None

    while not done:
        if start_key:
            scan_kwargs['ExclusiveStartKey'] = start_key
        response = table.scan(**scan_kwargs)
        allitems = allitems + response.get('Items', [])
        start_key = response.get('LastEvaluatedKey', None)
        done = start_key is None
    return allitems
