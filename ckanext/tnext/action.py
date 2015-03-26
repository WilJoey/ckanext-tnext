import ckan.plugins as p
import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.model as model
import collections
import suggestentity as db

from ckan.common import response, request, json

def tnstats_dataset_count(self, id):
    c = p.toolkit.c

    _ViewCount = collections.namedtuple("ViewCount", "views downloads")

    engine = model.meta.engine
    sql = '''
SELECT 
    COALESCE(SUM(s.count), 0) AS views,
    --COALESCE((SELECT SUM(resource_count) FROM v_dataset_count WHERE dataset_id=p.id), 0) AS views,
    COALESCE((SELECT SUM(resource_count) FROM v_dataset_download WHERE dataset_id=p.id), 0) AS downloads
FROM package AS p LEFT OUTER JOIN tracking_summary AS s ON s.package_id = p.id
WHERE p.id = %s GROUP BY p.id ; '''
    result = [_ViewCount(*t) for t in engine.execute(sql, id).fetchall()]
    
    return result[0]


''' SUGGEST '''
def tnext_suggest_pagesShow(context, data_dict):
    search = {}
    search['is_enabled'] = True
    #search['limit'] = 1
    #search['id']= "9dcfef91-e960-4778-b94e-5d390ceb52ab"

    if db.suggest_table is None:
        db.init_db(context['model'])
    out = db.Suggest.suggests(data_dict['limit'],data_dict['offset'])
    '''
    content, suggester, suggest_name, suggest_columns, 
            created, upper, user_id
    '''
    '''
    if out:
        out = db.table_dictize(out, context)
    return out
    '''
    return [{
        'id' : sg.id,
        'title': sg.title,
        'suggester': sg.suggester,
        'suggest_name' : sg.suggest_name,
        'suggest_columns': sg.suggest_columns,
        'views': sg.views,
        'created': sg.created
    } for sg in out]
    
