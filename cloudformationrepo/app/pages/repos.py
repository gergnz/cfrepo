"""Build the index page"""
from flask import render_template
from boto3.dynamodb.conditions import Key
from app.dynamodbscan import dynoscan

class Repos():
    """Index Page"""
    #pylint: disable=too-few-public-methods,too-many-arguments
    def __init__(self, ReposTable, dynamodb_table):
        """Initialisation"""
        self.repostable = ReposTable
        self.dynamodb_table = dynamodb_table

    def display(self):
        """Display And Add Repos"""

        scan_kwargs = {
            'FilterExpression': Key('TemplatePATH').eq('.'),
            'ProjectionExpression': 'RepositoryURI'
        }

        allitems = dynoscan(self.dynamodb_table, scan_kwargs)

        for item in allitems:
            item['delete'] = 'delete'

        table = self.repostable(allitems)
        return render_template('repos.html', allitems=table.__html__())
