"""Build the index page"""
import boto3
from flask import render_template
from app.dynamodbscan import dynoscan

class Index():
    """Index Page"""
    #pylint: disable=too-few-public-methods,too-many-arguments
    def __init__(self, ItemTable, dynamodb_table, region, s3_bucket):
        """Initialisation"""
        self.itemtable = ItemTable
        self.dynamodb_table = dynamodb_table
        self.region = region
        self.s3_bucket = s3_bucket

    def display(self):
        """Display the Templates"""

        scan_kwargs = {
            'FilterExpression': 'TemplatePATH <> :path',
            'ExpressionAttributeValues' : {':path' : '.'}

        }

        allitems = dynoscan(self.dynamodb_table, scan_kwargs)

        #pylint: disable=line-too-long
        cfuri_part1 = 'https://console.aws.amazon.com/cloudformation/home?region={0}'.format(self.region)
        #pylint: enable=line-too-long
        cfuri_part2 = '#/stacks/new?stackName='
        cfuri_part3 = '&templateURL=https://s3.{0}'.format(self.region)
        cfuri_part4 = '.amazonaws.com/{0}'.format(self.s3_bucket)

        for item in allitems:
            name = item['TemplatePATH'].split('/')[-1].split('.')[:1][0]
            #pylint: disable=line-too-long
            item['Launch'] = '<a href="{0}{1}{2}{3}{4}{5}"><img src="/static/cloudformation-launch-stack.png"></a>'.format(cfuri_part1,cfuri_part2,name,cfuri_part3,cfuri_part4,item['TemplatePATH'])
            #pylint: enable=line-too-long
            params = ''
            for param in item['TemplateParameters']:
                params = params + '{0}<br>'.format(param)
            item['TemplateParameters'] = params

        table = self.itemtable(allitems)
        return render_template('index.html', allitems=table.__html__())
