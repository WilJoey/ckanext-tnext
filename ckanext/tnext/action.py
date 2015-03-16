import ckan.plugins as p
import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.model as model
import collections
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
