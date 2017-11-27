import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import action as a
import constants
import auth
from ckanext.tnext import helpers

log = logging.getLogger(__name__)

def tnext_hots(*args):
    '''
    result = {}
    result['arg1'] = args[0] or 'Nothing'
    result['status'] = 'success'
    return result
    '''
    data_dict = {
        'rows': 6,
        'sort': args[0] or 'metadata_modified desc'
    }
    query = plugins.toolkit.get_action('package_search')(None, data_dict)
    return query


# Joe Tnext Plug setup init #
class TnextPlugin(plugins.SingletonPlugin):
    '''tnod plugin.'''
    
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)
    plugins.implements(plugins.IAuthFunctions)


    ######################################################################
    ############################## IACTIONS ##############################
    ######################################################################
    def get_actions(self):
        return {
            'tnstats_dataset_count': a.tnstats_dataset_count,

            constants.SUGGEST_INDEX: a.suggest_index,
            constants.SUGGEST_CREATE: a.suggest_create,
            constants.SUGGEST_SHOW: a.suggest_show,
            constants.SUGGEST_VIEWS: a.suggest_views,
            # constants.SUGGEST_UPDATE: abc.suggest_update,
            # constants.SUGGEST_DELETE: a.suggest_delete,
            # constants.SUGGEST_CLOSE: a.suggest_close,
            constants.SUGGEST_COMMENT: a.suggest_comment,
            # constants.SUGGEST_COMMENT_LIST: a.suggest_comment_list,
            # constants.SUGGEST_COMMENT_SHOW: a.suggest_comment_show,
            # constants.SUGGEST_COMMENT_UPDATE: a.suggest_comment_update,
            # constants.SUGGEST_COMMENT_DELETE: a.suggest_comment_delete
            'get_domail_content': a.get_domail_content
        }

    ######################################################################
    ########################### AUTH FUNCTIONS ###########################
    ######################################################################
    def get_auth_functions(self):
        return {
            constants.SUGGEST_INDEX: auth.suggest_index,
            constants.SUGGEST_CREATE: auth.suggest_create,
            constants.SUGGEST_SHOW: auth.suggest_show,
            # constants.SUGGEST_UPDATE: auth.suggest_update,
            # constants.SUGGEST_DELETE: auth.suggest_delete,
            # constants.SUGGEST_CLOSE: auth.suggest_close,
            constants.SUGGEST_COMMENT: auth.suggest_comment,
            # constants.SUGGEST_COMMENT_LIST: auth.suggest_comment_list,
            # constants.SUGGEST_COMMENT_SHOW: auth.suggest_comment_show,
            constants.SUGGEST_COMMENT_UPDATE: auth.suggest_comment_update,
            # constants.SUGGEST_COMMENT_DELETE: auth.suggest_comment_delete
        }

    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_resource('fanstatic', 'tnext_jscss')
        toolkit.add_public_directory(config, 'public')



    def after_map(self, map):
        map.connect('tnstats', '/tnstats', 
            controller = 'ckanext.tnext.controllers.TnStats:TnStatsController',
            action='index')
    	map.connect('tnstats', '/tnstats/{action}', 
    		controller = 'ckanext.tnext.controllers.TnStats:TnStatsController',
    		action='index')

        map.connect('resource_download','/rsdl/{id}', 
            controller = 'ckanext.tnext.controllers.ResourceDownload:ResourceDownloadController',
            action='create')

        map.connect('muser', '/muser/{action}',
            controller = 'ckanext.tnext.controllers.MUser:MUserController',
            action='index')
        map.connect('muser', '/muser',
            controller = 'ckanext.tnext.controllers.MUser:MUserController',
            action='index')
        map.connect('muser_edit', '/muser/edit/{id:.*}', 
            controller = 'ckanext.tnext.controllers.MUser:MUserController',
            action='edit')
        map.connect('muser_delete', '/muser/delete/{id}', 
            controller = 'ckanext.tnext.controllers.MUser:MUserController',
            action='delete')

        map.connect('datasetlist','/datasetlist', 
            controller = 'ckanext.tnext.controllers.Datasets:DatasetsController',
            action='index')

        map.connect('home_show','/show', 
            controller = 'ckanext.tnext.controllers.TnStats:TnStatsController', action='show')
        
        map.connect('home_specification','/specification', 
            controller = 'ckanext.tnext.controllers.TnStats:TnStatsController', action='specification')
        map.connect('home_specification_old','/specification_old',
            controller = 'ckanext.tnext.controllers.TnStats:TnStatsController', action='specification_old')

        map.connect('home_guide','/guide', 
            controller = 'ckanext.tnext.controllers.TnStats:TnStatsController', action='guide')
        map.connect('home_faq','/faq', 
            controller = 'ckanext.tnext.controllers.TnStats:TnStatsController', action='faq')
        map.connect('home_manual','/manual', 
            controller = 'ckanext.tnext.controllers.TnStats:TnStatsController', action='manual')
        map.connect('home_privacy','/privacy',
            controller = 'ckanext.tnext.controllers.TnStats:TnStatsController', action='privacy')
        map.connect('home_webdataopen','/webdataopen',
            controller = 'ckanext.tnext.controllers.TnStats:TnStatsController', action='webdataopen')

        ## suggests ##
        # Data Requests index
        map.connect('suggests_index', "/suggest",
                  controller='ckanext.tnext.controllers.Suggest:SuggestsController',
                  action='index', conditions=dict(method=['GET']))
        # Create a Data Request
        map.connect('/%s/new' % constants.SUGGESTS_MAIN_PATH,
                  controller='ckanext.tnext.controllers.Suggest:SuggestsController',
                  action='new', conditions=dict(method=['GET', 'POST']))
        # Show a Data Request
        map.connect('suggest_show', '/%s/{id}' % constants.SUGGESTS_MAIN_PATH,
                  controller='ckanext.tnext.controllers.Suggest:SuggestsController',
                  action='show', conditions=dict(method=['GET']), ckan_icon='question-sign')
        map.connect('suggest_view', '/%s/view/{id}' % constants.SUGGESTS_MAIN_PATH,
                  controller='ckanext.tnext.controllers.Suggest:SuggestsController',
                  action='views', conditions=dict(method=['POST']), ckan_icon='question-sign')
       # Comment, update and view comments (of) a Data Request
        map.connect('suggest_comment', '/%s/{id}/comment' % constants.SUGGESTS_MAIN_PATH,
                  controller='ckanext.tnext.controllers.Suggest:SuggestsController',
                  action='suggest_comment', conditions=dict(method=['GET', 'POST']), ckan_icon='comment')

    	return map

    def before_map(self, map):
        
        return map

    def get_helpers(self):
        return {
            'tnexthots': tnext_hots,
            'get_org_list': helpers.get_org_list
        } 
