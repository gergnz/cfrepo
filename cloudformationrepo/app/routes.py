"""CloudFormation Repository Flask App"""
import os
from flask_restful import Api
from app import app
from app.repos import NewRepos, DeleteRepos
from app.table import ReposTable, TemplateTable
from app.pages import Index
from app.pages import Repos

api = Api(app)

s3_bucket = os.environ.get('S3_BUCKET', 'cfrepo-cfrbucket9fd76711-prrb50pqbm31')
dynamodb_table = os.environ.get('DYNAMODB_TABLE', 'cfrepo-CfrTable1A89E739-1ZY9KC03VF18')
region = os.environ.get('AWS_DEFAULT_REGION')

if region is None:
    region = os.environ.get('AWS_REGION', 'ap-southeast-2')

api.add_resource(NewRepos, '/newrepo', resource_class_args={dynamodb_table})
api.add_resource(DeleteRepos, '/delrepo', resource_class_kwargs={
    's3_bucket': s3_bucket,
    'dynamodb_table': dynamodb_table})

@app.route('/')
def index():
    """Display the Templates"""
    page = Index(TemplateTable, dynamodb_table, region, s3_bucket)
    return page.display()

@app.route('/repos')
def repos():
    """Display And Add Repos"""
    page = Repos(ReposTable, dynamodb_table)
    return page.display()
