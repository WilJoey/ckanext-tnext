import urllib
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
    def index (self):
        LIMIT = 2
 
        page = request.params.get('page', 1)
        try:
            page=int(page)
            if page<1:
                page=1
        except ValueError, e:
            page=1

        _suggest = p.toolkit.get_action('tnext_suggest_pagesShow') (
            data_dict = { 'limit': LIMIT,
                        'offset': (page -1) * LIMIT}
        )
        p.toolkit.c.suggests=_suggest

        c.page = h.Page(
            collection=_suggest,
            page=page,
            url=h.pager_url,
            item_count = len(_suggest),
            items_per_page = LIMIT
        )
        return base.render('suggest/index.html')