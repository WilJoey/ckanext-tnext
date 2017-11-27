# -*- coding: utf-8 -*-
import ckan.plugins as p
from ckan.lib.base import BaseController, config
import ckan.lib.helpers as h
import ckan.model as model
import collections
import sqlalchemy
from ckan.common import response, request, json
import ckan.lib.base as base
import logging

log = logging.getLogger(__name__)

class TnStatsController(BaseController):

    def index (self):
        c = p.toolkit.c

        ## Used by the Tracking class
        _ViewCount = collections.namedtuple("ViewCount", "id title name org_name dataset_views resource_views resource_downloads")

        engine = model.meta.engine
        sql = '''
SELECT p.id, p.title, p.name,
    (SELECT title FROM "group" WHERE id=p.owner_org) AS org_name,
    COALESCE(SUM(s.count), 0) AS dataset_views, 
    COALESCE((SELECT SUM(resource_count) FROM v_dataset_count WHERE dataset_id=p.id), 0) AS resource_views,
    COALESCE((SELECT SUM(resource_count) FROM v_dataset_download WHERE dataset_id=p.id), 0) AS resource_downloads
FROM package AS p
    LEFT OUTER JOIN tracking_summary AS s ON s.package_id = p.id
WHERE p.state='active'
GROUP BY p.id, p.title
ORDER BY org_name ASC; '''
        c.datasets_count =  [_ViewCount(*t) for t in engine.execute(sql).fetchall()]

        return p.toolkit.render('tnstats/index.html')

    def group (self):
        c = p.toolkit.c
        
        ## Used by the Tracking class
        _ViewCount = collections.namedtuple("ViewCount", "id title name group_name dataset_views resource_views resource_downloads")

        engine = model.meta.engine
        sql = '''
SELECT p.id, p.title, p.name, g.title as group_name, 
  COALESCE(SUM(s.count), 0) AS dataset_views,
  COALESCE((SELECT SUM(resource_count) FROM v_dataset_count WHERE dataset_id=p.id), 0) AS resource_views,
  COALESCE((SELECT SUM(resource_count) FROM v_dataset_download WHERE dataset_id=p.id), 0) AS resource_downloads
FROM 
  public."package" p LEFT OUTER JOIN tracking_summary AS s ON s.package_id = p.id, 
  public.member m, 
  public."group" g
WHERE 
  m.table_id = p.id AND g.id = m.group_id AND 'active' = p.state AND false = g.is_organization
GROUP BY
  p.id, g.id
ORDER BY
  g.title ASC, 
  p.title ASC; '''
        c.datasets_count =  [_ViewCount(*t) for t in engine.execute(sql).fetchall()]

        return p.toolkit.render('tnstats/group.html')

    def keyword (self):
        c = p.toolkit.c

        ## Used by the Tracking class
        _ViewCount = collections.namedtuple("ViewCount", "content count")

        engine = model.meta.engine
        sql = '''
SELECT content, COUNT(content) as count
FROM v_keyword_filtered
GROUP BY content ORDER BY count DESC, content ASC; '''
        c.keyword_count =  [_ViewCount(*t) for t in engine.execute(sql).fetchall()]
        return p.toolkit.render('tnstats/keyword.html')

    def org (self):
        c = p.toolkit.c

        ## Used by the Tracking class
        _ViewCount = collections.namedtuple("ViewCount", "id org_name dataset_counts suggest_counts comment_counts outdate_counts")

        engine = model.meta.engine
        sql = '''
SELECT g.id,g.title AS org_name,
    (SELECT count(*) FROM package where owner_org=g.id and state='active') AS dataset_counts,
    (SELECT count(sg.*)||'('||count(cm.*)||')' FROM suggests as sg left join suggests_comments as cm on sg.id=cm.suggest_id where sg.org_id=g.id and sg.closed<>'t') AS suggest_counts,
    (SELECT count(*) FROM dataset_comments where org_id=g.id) AS comment_counts,
    (SELECT count(*) FROM outdate_datasets where org_id=g.id) AS outdate_counts
FROM public.group as g where type='organization' and state='active'
ORDER BY org_name ASC; '''
        c.orgstats =  [_ViewCount(*t) for t in engine.execute(sql).fetchall()]

        return p.toolkit.render('tnstats/org.html')       
 

    def kwfilter(self):
        c = p.toolkit.c
        result = {}
        result['status']=True
        result['message']= ''
        sql = '''
SELECT content, COUNT(content) as count
FROM v_keyword_filtered
WHERE created between %s and  %s
GROUP BY content ORDER BY count DESC, content ASC; '''

        if(request.params.get('all',False)):
            sql ='''
SELECT content, COUNT(content) as count
FROM v_keyword_filtered
GROUP BY content ORDER BY count DESC, content ASC; '''
        
        try:
            result['strat']=request.params.get('start',None)
            result['end']=request.params.get('end',None)
            ## Used by the Tracking class
            _ViewCount = collections.namedtuple("ViewCount", "content count")

            engine = model.meta.engine
            result['data'] = [_ViewCount(*t) for t in engine.execute(sql, result['strat'], result['end']).fetchall()]

        except sqlalchemy.exc.DataError as e:
            result['status']=False
            result['message']= 'Error: Start or end parameter format incorrect!'
            result['data']=[]

        response.headers['Content-Type'] = 'application/json;charset=utf-8'
        return h.json.dumps(result)

    def orgApi (self):
        _ViewCount = collections.namedtuple("ViewCount", "id title name org_name dataset_views resource_views resource_downloads")

        engine = model.meta.engine
        sql = '''
SELECT p.id, p.title, p.name,
    (SELECT title FROM "group" WHERE id=p.owner_org) AS org_name,
    COALESCE(SUM(s.count), 0) AS dataset_views, 
    COALESCE((SELECT SUM(resource_count) FROM v_dataset_count WHERE dataset_id=p.id), 0) AS resource_views,
    COALESCE((SELECT SUM(resource_count) FROM v_dataset_download WHERE dataset_id=p.id), 0) AS resource_downloads
FROM package AS p
    LEFT OUTER JOIN tracking_summary AS s ON s.package_id = p.id
WHERE p.state='active'
GROUP BY p.id, p.title
ORDER BY org_name ASC; '''
        result = [_ViewCount(*t) for t in engine.execute(sql).fetchall()]
        
        response.headers['Content-Type'] = 'application/json;charset=utf-8'
        return h.json.dumps(result)

    def groupApi (self):
        _ViewCount = collections.namedtuple("ViewCount", "id title name group_name dataset_views resource_views resource_downloads")

        engine = model.meta.engine
        sql = '''
SELECT p.id, p.title, p.name, g.title as group_name, 
  COALESCE(SUM(s.count), 0) AS dataset_views,
  COALESCE((SELECT SUM(resource_count) FROM v_dataset_count WHERE dataset_id=p.id), 0) AS resource_views,
  COALESCE((SELECT SUM(resource_count) FROM v_dataset_download WHERE dataset_id=p.id), 0) AS resource_downloads
FROM 
  public."package" p LEFT OUTER JOIN tracking_summary AS s ON s.package_id = p.id, 
  public.member m, 
  public."group" g
WHERE 
  m.table_id = p.id AND g.id = m.group_id AND 'active' = p.state AND false = g.is_organization
GROUP BY
  p.id, g.id
ORDER BY
  g.title ASC, 
  p.title ASC; '''
        result =  [_ViewCount(*t) for t in engine.execute(sql).fetchall()]

        response.headers['Content-Type'] = 'application/json;charset=utf-8'
        return h.json.dumps(result)

    def _orgApiResult(self):
        log.info("orgCsv _orgApiResult 1")
        engine = model.meta.engine
        sql = '''
SELECT g.id,g.title AS org_name,
    (SELECT count(*) FROM package where owner_org=g.id and state='active') AS dataset_counts,
    (SELECT count(sg.*)||'('||count(cm.*)||')' FROM suggests as sg left join suggests_comments as cm on sg.id=cm.suggest_id where sg.org_id=g.id and sg.closed<>'t') AS suggest_counts,
    (SELECT count(*) FROM dataset_comments where org_id=g.id) AS comment_counts,
    (SELECT count(*) FROM outdate_datasets where org_id=g.id) AS outdate_counts
FROM public.group as g where type='organization' and state='active'
ORDER BY org_name ASC; '''
        result = engine.execute(sql).fetchall()
        log.info('orgCsv _orgApiResult2 %s' % type(result))
        return result        
 
    def orgCsv(self):
        log.info("orgCsv start")
        head = u'\ufeff組織,資料集數量,資料集建議則數(回覆數),資料集意見回饋則數,資料集逾期未更新\r\n'
        data = self._orgApiResult()
        log.info('orgCsv %s' % type(data))
        return self._csv(head, data)

    def _csv(self, head, data):
        log.info("orgCsv _csv")
        base.response.headers['Content-type'] ='text/csv; charset=utf-8'
        base.response.headers['Content-disposition'] ='attachment;filename=statistics.csv'
        
        csvFormatter = u'"{0}",{1},{2},{3},{4}\r\n'
        for item in data:
            #data += csvFormatter.format(*item)
            log.info('orgCsv _csv1 %s' % item[1])
            head += csvFormatter.format(item[1],item[2],item[3],item[4],item[5])
        return head 
    def show(self):
        return base.render('home/show.html')

    def specification(self):
        return base.render('home/specification.html')
    def specification_old(self):
        return base.render('home/specification_old.html')

    def guide(self):
        return base.render('home/guide.html')

    def manual(self):
        return base.render('home/manual.html')
    
    def faq(self):
        return base.render('home/faq.html')
    
    def privacy(self):
        return base.render('home/privacy.html')

    def webdataopen(self):
        return base.render('home/webdataopen.html')
