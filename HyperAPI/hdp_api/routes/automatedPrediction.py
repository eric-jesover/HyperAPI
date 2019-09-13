from HyperAPI.hdp_api.base.resource import Resource
from HyperAPI.hdp_api.base.route import Route


class AutomatedPrediction(Resource):
    name = "automatedPrediction"
    available_since = "4.2.6"
    removed_since = None

    class _getAutomatedModel(Route):
        name = "getAutomatedModel"
        httpMethod = Route.GET
        path = "/projects/{project_ID}/automodels/{model_ID}"
        _path_keys = {
            'project_ID': Route.VALIDATOR_OBJECTID,
            'model_ID': Route.VALIDATOR_OBJECTID,
        }

    class _getAutomatedModels(Route):
        name = "getAutomatedModels"
        httpMethod = Route.GET
        path = "/projects/{project_ID}/automodels"
        _path_keys = {
            'project_ID': Route.VALIDATOR_OBJECTID,
        }
    
    class _getGeneratedModels(Route):
        name = "getGeneratedModels"
        httpMethod = Route.GET
        path = "/projects/{project_ID}/automodels/{model_ID}/generatedmodels"
        _path_keys = {
            'project_ID': Route.VALIDATOR_OBJECTID,
            'model_ID': Route.VALIDATOR_OBJECTID
        }

    class _createAutomatedModel(Route):
        name = "createAutomatedModel"
        httpMethod = Route.POST
        path = "/projects/{project_ID}/automodels/create"
        _path_keys = {
            'project_ID': Route.VALIDATOR_OBJECTID,
        }

    class _publishAutomatedModel(Route):
        name = "publishAutomatedModel"
        httpMethod = Route.POST
        path = "/projects/{project_ID}/automodels/{model_ID}/generatedmodels/{generatedmodel_ID}/publish"
        _path_keys = {
            'project_ID': Route.VALIDATOR_OBJECTID,
            'model_ID': Route.VALIDATOR_OBJECTID,
            'generatedmodel_ID': Route.VALIDATOR_OBJECTID,
        }