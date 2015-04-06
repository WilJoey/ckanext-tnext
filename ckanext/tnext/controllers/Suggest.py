import logging

import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as plugins
import ckan.lib.helpers as helpers
import ckanext.tnext.constants as constants
import functools


from ckan.common import request
from urllib import urlencode






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

            state = request.GET.get('state', None)
            if state:
                data_dict['closed'] = True if state == 'closed' else False


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
    
            if action == constants.SUGGEST_UPDATE:
                data_dict['id'] = request.POST.get('id', '')

            try:
                result = tk.get_action(action)(context, data_dict)
                tk.response.status_int = 302
                tk.response.location = '/%s/%s' % (constants.SUGGESTS_MAIN_PATH,
                                                   result['id'])

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
            tk.check_access(constants.SUGGEST_SHOW, context, data_dict)
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

    def suggest_comment(self, id):
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
      