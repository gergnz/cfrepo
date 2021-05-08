"""Table Stuff"""
from flask_table import Table, Col, LinkCol

class NoEscCol(Col):
    """Override Col Class to not escape"""
    def td_format(self, content):
        return content

class TemplateTable(Table):
    #pylint: disable=W0223
    """Template Table"""
    Launch = NoEscCol('Launch')
    TemplatePATH = Col('Template Path')
    TemplateDescription = Col('Template Description')
    RepositoryURI = Col('Repository URI')
    TemplateParameters = NoEscCol('Template Parameters')
    classes = ['table', 'table-display', 'table-compact', 'table-hover', 'table-nowrap']
    html_attrs = dict(cellspacing='0', width='100%')
    table_id = 'table'

class ReposTable(Table):
    #pylint: disable=W0223
    """Repos Table"""
    RepositoryURI = Col('Repository URI')
    delete = LinkCol('Delete', 'deleterepos', url_kwargs=dict(repouri='RepositoryURI'))
    classes = ['table', 'table-display', 'table-compact', 'table-hover', 'table-nowrap']
    html_attrs = dict(cellspacing='0', width='100%')
    table_id = 'table'
