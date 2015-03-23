import ckan.plugins as p
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.model as model
import ckan.logic as logic
import ckan.logic.schema as schema
import ckan.new_authz as new_authz
import ckan.lib.captcha as captcha
import ckan.lib.navl.dictization_functions as dictization_functions
from pylons import config
from ckan.common import _, c, g, request

c = base.c
request = base.request

class SuggestController(base.BaseController):
    def index (self, page=None):
        LIMIT = 10
        if page:
            page = page[1:]
        _suggest = p.toolkit.get_action('tnext_suggest_pagesShow') (
            data_dict = { 'page': page }
        )
        p.toolkit.c.suggests=_suggest

        #page = int(request.params.get('page', 1))
        #c.q = request.params.get('q', '')
        #c.order_by = request.params.get('order_by', 'name')

        #context = {'return_query': True, 'user': c.user or c.author,
        #           'auth_user_obj': c.userobj}

        #data_dict = {'q': c.q,
        #             'limit': LIMIT,
        #             'offset': (page - 1) * LIMIT,
        #             'order_by': c.order_by}

        #users_list = logic.get_action('user_list')(context, data_dict)
        #c.users = users_list
        #suggest_list=[]

        #c.page = h.Page(
        #    #collection=users_list,
        #    page=page,
        #    #url=h.pager_url,
        #    item_count=0, # suggest_list.count(),
        #    items_per_page=LIMIT
        #)
        return base.render('suggest/index.html')