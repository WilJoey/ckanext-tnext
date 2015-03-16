'''plugin.py

'''
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import action as a


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



class TnextPlugin(plugins.SingletonPlugin):
    '''tnod plugin.'''
    
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)

    '''
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IActions, inherit=True)
    '''
    

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

        map.connect('home_guide','/guide', 
            controller = 'ckanext.tnext.controllers.TnStats:TnStatsController', action='guide')

    	return map

    def before_map(self, map):
        
        return map

    def get_actions(self):
        return {
            'tnstats_dataset_count': a.tnstats_dataset_count
        }

    def get_helpers(self):
        return {
            'tnexthots': tnext_hots
        } 
