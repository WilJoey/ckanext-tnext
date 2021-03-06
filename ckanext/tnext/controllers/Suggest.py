# -*- coding: utf-8 -*-
import logging
import sqlalchemy as sa

import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as plugins
import ckan.lib.helpers as helpers
import ckanext.tnext.constants as constants
import functools
import requests
import smtplib

from ckan.common import response, request, json
from urllib import urlencode
from sqlalchemy import text





log = logging.getLogger(__name__)
tk = plugins.toolkit
c = tk.c


def _get_errors_summary(errors):
    errors_summary = {}

    for key, error in errors.items():
        errors_summary[key] = ', '.join(error)

    return errors_summary


def _encode_params(params):
    return [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v))
            for k, v in params]


def url_with_params(url, params):
    params = _encode_params(params)
    return url + u'?' + urlencode(params)


def search_url(params):
    url = helpers.url_for(controller='ckanext.tnext.controllers.Suggest:SuggestsController',
                          action='index')
    return url_with_params(url, params)




class SuggestsController(base.BaseController):

    def index(self):
        return self._show_index( search_url, 'suggest/index.html')

    def _get_context(self):
        return {'model': model, 'session': model.Session,
                'user': c.user, 'auth_user_obj': c.userobj}

    def _show_index(self, url_func, file_to_render):

        def pager_url(q=None, page=None):
            params = list()
            params.append(('page', page))
            return url_func(params)

        try:
            context = self._get_context()
            page = int(request.GET.get('page', 1))
            limit = constants.SUGGESTS_PER_PAGE
            offset = (page - 1) * constants.SUGGESTS_PER_PAGE
            data_dict = {'offset': offset, 'limit': limit}

            # state = request.GET.get('state', None)
            # if state:
            #     data_dict['closed'] = True if state == 'closed' else False
            data_dict['closed'] = False

            tk.check_access(constants.SUGGEST_INDEX, context, data_dict)
            suggests_list = tk.get_action(constants.SUGGEST_INDEX)(context, data_dict)
            c.suggest_count = suggests_list['count']
            c.suggests = suggests_list['result']
            c.search_facets = suggests_list['facets']
            c.page = helpers.Page(
                collection=suggests_list['result'],
                page=page,
                url=pager_url,
                item_count=suggests_list['count'],
                items_per_page=limit
            )
            c.facet_titles = {
                'state': tk._('State'),
            }
            return tk.render(file_to_render)

        except ValueError as e:
            # This exception should only occur if the page value is not valid
            log.warn(e)
            tk.abort(400, tk._('"page" parameter must be an integer'))

        except tk.NotAuthorized as e:
            log.warn(e)
            tk.abort(403, tk._('Unauthorized to list Data Requests'))


    def new(self):
        context = self._get_context()

        # Basic intialization
        c.suggest = {}
        c.errors = {}
        c.errors_summary = {}

        # Check access
        try:
            tk.check_access(constants.SUGGEST_CREATE, context, None)
            self._process_post(constants.SUGGEST_CREATE, context)
            log.info('Suggest_new')
            # The form is always rendered
            return tk.render('suggest/new.html')

        except tk.NotAuthorized as e:
            log.warn(e)
            tk.abort(403, tk._('Unauthorized to create a Data Request'))


    def _process_post(self, action, context):
        # If the user has submitted the form, the data request must be created
        if request.POST:
            data_dict = {}
            data_dict['title'] = request.POST.get('title', '')
            data_dict['description'] = request.POST.get('description', '')
            data_dict['user_id'] = request.POST.get('user_id', '')
            data_dict['dataset_name'] = request.POST.get('dataset_name', '')
            data_dict['suggest_columns'] = request.POST.get('suggest_columns', '')
            data_dict['org_id'] = request.POST.get('org_id', '')
            data_dict['email'] = request.POST.get('email', '')

            log.info('Suggest_process_post1 %s' % action)
            if action == constants.SUGGEST_UPDATE:
                data_dict['id'] = request.POST.get('id', '')

            try:
                result = tk.get_action(action)(context, data_dict)
                tk.response.status_int = 302
                tk.response.location = '/%s/%s' % (constants.SUGGESTS_MAIN_PATH,
                                                   result['id'])
                #log.info('Suggest_process_post2 %s %s' % (result['id'],result['open_time']))             
                self.sendmail(result['id'])
                log.info('Suggest_process_post3 %s' % result['id'])

            except tk.ValidationError as e:
                log.warn(e)
                # Fill the fields that will display some information in the page
                c.suggest = {
                    'id': data_dict.get('id', ''),
                    'title': data_dict.get('title', ''),
                    'description': data_dict.get('description', ''),
                    'user_id': data_dict.get('user_id', ''),
                    'dataset_name': data_dict.get('dataset_name', ''),
                    'suggest_columns': data_dict.get('suggest_columns', '')
                }
                c.errors = e.error_dict
                c.errors_summary = _get_errors_summary(c.errors)

    def show(self, id):
        data_dict = {'id': id}
        context = self._get_context()

        try:
            #tk.check_access(constants.SUGGEST_SHOW, context, data_dict)
            c.suggest = tk.get_action(constants.SUGGEST_SHOW)(context, data_dict)

            context_ignore_auth = context.copy()
            context_ignore_auth['ignore_auth'] = True

            return tk.render('suggest/show.html')
        except tk.ObjectNotFound as e:
            tk.abort(404, tk._('Data Request %s not found') % id)
        except tk.NotAuthorized as e:
            log.warn(e)
            tk.abort(403, tk._('You are not authorized to view the Data Request %s'
                               % id))

    def views(self, id):
        data_dict = {'id': id}
        context = self._get_context()
        #if request.POST:
        tk.get_action('suggest_views')(context, data_dict)
        return 'abc'
    
    def sendmail(self, id):
        log.info("Suggest_sendmail start: " + id)
        
        context = self._get_context()
        
        log.info("Suggest_sendmail 2")
        mail_content =self._get_mail_content(id)
        mail_recipient=[]
        FROM = 'tainanod@gmail.com'
        engine = sa.create_engine('postgresql://ckan_default:123456@localhost/ckan_tnod')
        user_infos = engine.execute("select * from public.user where id in(select table_id from public.member where group_id=%s and table_name='user' and capacity='admin')",mail_content['org_id'])
        for user_info in user_infos:
            mail_recipient.append(user_info['email'])
        mail_recipient.append("opendata@tainan.gov.tw")
        mail_recipient.append("jungchang71@gmail.com")
        mail_recipient=list(set(mail_recipient)) 
        TO=mail_recipient   
        #TO = 'jungchang71@gmail.com'       
        #SUBJECT = '[資料集建議回饋主動通知][%s][%s]' % (mail_content['id'], mail_content['title'])
        SUBJECT = '[資料集建議回饋主動通知]'
        #TEXT = '依據資料開放平台資料建議專區功能，平台使用者於%s發布資料建議，其資料建議相關單位為%s，敬請長官前往平台%s 進行檢閱並回覆使用者。\n以上通報，敬請檢閱，謝>謝您 \n\n 臺南市政府資料開放平台  敬上 ' % (mail_content['open_time'], mail_content['org'],mail_content['id'])
        TEXT = '依據資料開放平台資料建議專區功能，平台使用者於%s發布資料建議，其資料建議相關單位為%s，敬請長官前往平台%s 進行檢閱並回覆使用者。\n以上通報，敬請檢閱，謝謝您 \n\n 臺南市政府資料開放平台  敬上 '  % (mail_content['open_time'].strftime('%Y/%m/%d'), mail_content['org'].encode('utf-8'),'http://data.tainan.gov.tw/suggest/'+id)
        message = """Subject: %s\n\n%s""" % (SUBJECT, TEXT)
        #log.info('Suggest_sendmail_type: %s' % type(mail_content['org']))
        #log.info('Suggest_sendmail_content: %s' % SUBJECT)
        #server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        #server_ssl.login('tainanod@gmail.com','@tnodtnod')  
        #server_ssl.sendmail(FROM, TO, message)
        #server_ssl.close()
        
        FROM = 'opendata@mail.tainan.gov.tw'
        server = smtplib.SMTP("mail.tainan.gov.tw:25")
        #server.set_debuglevel(1)
        server.ehlo()
        server.login('opendata', 'opendata1234!')
        server.sendmail(FROM, TO, message)
        server.close()
    
    def domail(self, id):
        log.warn("domail start: " + id)

        data_dict = {'id': id}
        context = self._get_context()
        mail_content =self._get_mail_content(id)

        title = u'[OD][%s][代刚戈-%s]' % (mail_content['id'], mail_content['title'])
        '''
        message = {
            "org_no": mail_content['org_id'],
            "org_name": mail_content['org'],
            "name": mail_content['user_name'],
            "email": mail_content['email'],
            "context": mail_content['description']
        }
        '''
        ctx = {
            "Title": title,
            "org_no": mail_content['org_id'],
            "org_name": mail_content['org'],
            "name": mail_content['user_name'],
            "email": mail_content['email'],
            "context": mail_content['description']
        }
        url = u'http://demo2.geo.com.tw/ksod/api/domail/' + id
        resp = requests.post(url, data=ctx)
        
        result = helpers.json.loads(resp.text)
        if result['Success']:
            sql = 'UPDATE suggests SET send_mail=1 WHERE id= :id;'
            model.meta.engine.execute(text(sql), id=id)
            model.Session.commit()
            sql = 'UPDATE suggests SET mail_time=CURRENT_TIMESTAMP WHERE id=:id AND mail_time is null AND send_mail=1;'
            model.Session.execute(sql, {'id': id})
            model.Session.commit()

        response.headers['Content-Type'] = 'application/json;charset=utf-8'
        return helpers.json.dumps(result)


    def _get_mail_content(self,id):
        context = self._get_context()
        data_dict = {'closed': False, 'id': id}
        mail_content = tk.get_action('get_domail_content')(context, data_dict)
        return mail_content


    def suggest_comment(self, id):
        if request.GET:
            return self.show(id)

        try:
            context = self._get_context()
            #data_dict_comment_list = {'suggest_id': id}
            data_dict_dr_show = {'id': id}
            #tk.check_access(constants.SUGGEST_COMMENT_LIST, context, data_dict_comment_list)
            tk.check_access(constants.SUGGEST_COMMENT_UPDATE, context, None)
            

            comment = request.POST.get('comment', '')
            comment_id = request.POST.get('comment-id', '')

            if request.POST:
                try:
                    comment_data_dict = {'suggest_id': id, 'comment': comment, 'id': comment_id}
                    #action = constants.SUGGEST_COMMENT if not comment_id else constants.SUGGEST_COMMENT_UPDATE
                    comment = tk.get_action(constants.SUGGEST_COMMENT)(context, comment_data_dict)
                except tk.NotAuthorized as e:
                    log.warn(e)
                    tk.abort(403, tk._('You are not authorized to create/edit the comment'))
                except tk.ValidationError as e:
                    log.warn(e)
                    c.errors = e.error_dict
                    c.errors_summary = _get_errors_summary(c.errors)
                    c.comment = comment
                except tk.ObjectNotFound as e:
                    log.warn(e)
                    tk.abort(404, tk._('Data Request %s not found') % id)

        except tk.ObjectNotFound as e:
            log.warn(e)
            tk.abort(404, tk._('Data Request %s not found' % id))

        except tk.NotAuthorized as e:
            log.warn(e)
            tk.abort(403, tk._('You are not authorized to comment the Data Request %s'
                               % id))

        #return tk.render('suggests/comment.html')
        return self.show(id)
      
