from HyperAPI.sessionClass import Session
from HyperAPI.utils.version import Version

from HyperAPI.hdp_api.routes.alerts import Alerts
from HyperAPI.hdp_api.routes.analytics import Analytics
from HyperAPI.hdp_api.routes.auxdata import AuxData
from HyperAPI.hdp_api.routes.color import Color
from HyperAPI.hdp_api.routes.correlations import Correlations
from HyperAPI.hdp_api.routes.dashboards import Dashboards
from HyperAPI.hdp_api.routes.datasets import Datasets
from HyperAPI.hdp_api.routes.datasetReshapes import DatasetReshapes
from HyperAPI.hdp_api.routes.datasetResources import DatasetResources
from HyperAPI.hdp_api.routes.docapi import DocApi
from HyperAPI.hdp_api.routes.exports import Exports
from HyperAPI.hdp_api.routes.hyperEngines import HyperEngines
from HyperAPI.hdp_api.routes.joinDatasets import JoinDatasets
from HyperAPI.hdp_api.routes.kpi import Kpi
from HyperAPI.hdp_api.routes.map import Map
from HyperAPI.hdp_api.routes.nitro import Nitro
from HyperAPI.hdp_api.routes.notebooks import Notebooks
from HyperAPI.hdp_api.routes.optimProcess import OptimProcess
from HyperAPI.hdp_api.routes.prediction import Prediction
from HyperAPI.hdp_api.routes.product import Product
from HyperAPI.hdp_api.routes.projects import Projects
from HyperAPI.hdp_api.routes.projectResources import ProjectResources
from HyperAPI.hdp_api.routes.query import Query
from HyperAPI.hdp_api.routes.reports import Reports
from HyperAPI.hdp_api.routes.rules import Rules
from HyperAPI.hdp_api.routes.rulesetViz import RulesetViz
from HyperAPI.hdp_api.routes.schedulerDashboard import SchedulerDashboard
from HyperAPI.hdp_api.routes.simpleLift import SimpleLift
from HyperAPI.hdp_api.routes.smartViz import SmartDataViz
from HyperAPI.hdp_api.routes.swpMatchmaking import SWPMatchmaking
from HyperAPI.hdp_api.routes.system import System
from HyperAPI.hdp_api.routes.tags import Tags
from HyperAPI.hdp_api.routes.task import Task
from HyperAPI.hdp_api.routes.tempData import TempData
from HyperAPI.hdp_api.routes.textProcessing import TextProcessing
from HyperAPI.hdp_api.routes.timeSeriesAnalysis import TimeSeriesAnalysis
from HyperAPI.hdp_api.routes.timeSeriesQuery import TimeSeriesQuery
from HyperAPI.hdp_api.routes.timeSeriesViz import TimeSeriesViz
from HyperAPI.hdp_api.routes.identities import Identities
from HyperAPI.hdp_api.routes.variable import Variable
from HyperAPI.hdp_api.routes.visualization import Visualization
from HyperAPI.hdp_api.routes.workalendar import Workalendar
from HyperAPI.hdp_api.routes.workflows import Workflows
from HyperAPI.hdp_api.routes.settings import Settings
from HyperAPI.hdp_api.routes.monitoring import Monitoring
from HyperAPI.hdp_api.routes.authentication import Authentication
from HyperAPI.hdp_api.routes.thirdParties import ThirdParties
from HyperAPI.hdp_api.routes.realTime import RealTime
from HyperAPI.hdp_api.routes.iot import IotEtlApi
from HyperAPI.hdp_api.routes.admin import Admin
from HyperAPI.hdp_api.routes.anaplan import Anaplan

from HyperAPI.utils.timeoutSettings import TimeOutSettings
from HyperAPI.utils.validation import compare_schema_resources, compare_schema_routes

from collections import namedtuple

SessionDetails = namedtuple('SessionDetails', ['url', 'name', 'product', 'version', 'build_date', 'hdp_version'])


class Router(object):
    _resources = [
        Admin,
        Alerts,
        Analytics,
        AuxData,
        Anaplan,
        Color,
        Correlations,
        Dashboards,
        Datasets,
        DatasetReshapes,
        DatasetResources,
        DocApi,
        Exports,
        HyperEngines,
        JoinDatasets,
        Kpi,
        Map,
        Monitoring,
        Nitro,
        Notebooks,
        OptimProcess,
        Prediction,
        Product,
        Projects,
        ProjectResources,
        Query,
        Reports,
        Rules,
        RulesetViz,
        SchedulerDashboard,
        SimpleLift,
        SmartDataViz,
        SWPMatchmaking,
        System,
        Tags,
        Task,
        TempData,
        TextProcessing,
        TimeSeriesAnalysis,
        TimeSeriesQuery,
        TimeSeriesViz,
        Identities,
        Variable,
        Visualization,
        Workalendar,
        Workflows,
        Settings,
        ThirdParties,
        RealTime,
        Authentication,
        IotEtlApi
    ]

    def __init__(self, username=None, password=None, url=None, token=None, watcher=None):
        # Initiate session with HyperCube server
        self.session = Session(username=username, password=password, token=token, url=url)
        try:
            # We must fetch the System version BEFORE creating route, so this call is hard coded
            _system_details = self.session.request('GET', System._About.path)
            self.session_details = SessionDetails(url=self.session.url,
                                                  name=_system_details.get('name', 'N/A'),
                                                  product=_system_details.get('product', 'N/A'),
                                                  version=_system_details.get('version', 'N/A'),
                                                  hdp_version=_system_details.get('hdpVersion', 0),
                                                  build_date=_system_details.get('buildDate', 'N/A'),
                                                  )
        except Exception:
            self.session_details = SessionDetails(url=url,
                                                  name=None,
                                                  product=None,
                                                  version=None,
                                                  hdp_version=None,
                                                  build_date=None,
                                                  )
        self.session.version = Version(self.session_details.hdp_version)

        # Creating Resources
        self._create_resources(self._resources, watcher=None)
        self._default_timeout_settings = TimeOutSettings()

    def _create_resources(self, resources_list, watcher=None):
        for resourceCls in resources_list:
            if resourceCls.is_available(self.session.version):
                self.__setattr__(resourceCls.__name__, resourceCls(self.session, watcher=watcher))

    def refresh_session(self, username=None, password=None, token=None):
        self.session.refresh(username, password, token)

    def __iter__(self):
        for resourceCls in self._resources:
            if resourceCls.is_available(self.session.version):
                yield self.__getattribute__(resourceCls.__name__)

    # Work Management Specific Code ---------------------------------------------------------------------

    def handle_work_states(self, project_id, work_type=None, work_id=None, query=None, timeout_settings=None):
        if timeout_settings is None:
            timeout_settings = self._default_timeout_settings

        def _getStatus(work):
            if work is None:
                return None
            return work.get('_status', {}).get('kind', None)
        work_data = {'projectId': project_id}
        if work_type is not None and query is not None:
            work_data['type'] = work_type
            work_data.update(query)
        elif work_id is not None:
            work_data['_id'] = work_id
        else:
            raise ValueError('Missing conditions for works')

        _works = self.Task.task.wait_until(project_ID=project_id, json=work_data, condition=lambda x: len(x) > 0)  # noqa: E1101
        if not _works:
            # List empty, the work has not been created
            if work_id:
                raise ValueError('The work <{}> could not be found'.format(work_id))
            raise ValueError('The corresponding work could not be found')

        _work = next(iter(_works))

        while _getStatus(_work) != 'done':
            if _getStatus(_work) is None:
                raise ValueError('Missing Status on work <{}>'.format(work_id))

            if _getStatus(_work) == 'error':
                raise ValueError('Work "{}" <{}> has failed'.format(_work.get("type", "Unknown type"), work_id))

            if _getStatus(_work) == 'starting':
                _works = self.Task.task.wait_until(condition=lambda x: _getStatus(x[-1]) != 'starting',
                                                   timeout=timeout_settings.get_starting_timeout(),
                                                   project_ID=project_id, json=work_data)

            elif _getStatus(_work) == 'creating':
                _works = self.Task.task.wait_until(condition=lambda x: _getStatus(x[-1]) != 'creating' and _getStatus(x[-1]) != 'pending',
                                                   timeout=timeout_settings.get_pending_timeout(),
                                                   project_ID=project_id, json=work_data)

            elif _getStatus(_work) == 'pending':
                _works = self.Task.task.wait_until(condition=lambda x: _getStatus(x[-1]) != 'pending',
                                                   timeout=timeout_settings.get_pending_timeout(),
                                                   project_ID=project_id, json=work_data)

            elif _getStatus(_work) == 'inprogress':
                _works = self.Task.task.wait_until(condition=lambda x: _getStatus(x[-1]) != 'inprogress',
                                                   timeout=timeout_settings.get_progress_timeout(),
                                                   project_ID=project_id, json=work_data)

            if _works is None:
                if work_type:
                    msg = 'Timeout reached on work "{}" <{}>'.format(work_type, work_id)
                else:
                    msg = 'Timeout reached on work <{}>'.format(work_id)
                raise ValueError(msg)

            _work = next(iter(_works))
        return _work

    # Work Management Specific Code ---------------------------------------------------------------------

    @classmethod
    def validate_schema(self, schema, version):
        results = dict()

        unexpected_resources, missing_resources, match_resources = compare_schema_resources(self._resources, schema.get('resources'), version)

        results['unexpected_resources'] = unexpected_resources
        results['missing_resources'] = missing_resources
        results['different_resources'] = {}

        for _resource in self._resources:
            if _resource.name not in match_resources:
                continue

            _resource_schema = schema.get('resources').get(_resource.name, {}).get('methods', {})
            _routes = list(_resource._iter_routes_classes(version))
            unexpected_routes, missing_routes, match_routes = compare_schema_routes(_routes, _resource_schema, version)
            if unexpected_routes or missing_routes:
                results['different_resources'][_resource.name] = {
                    'unexpected_routes': unexpected_routes,
                    'missing_routes': missing_routes,
                }

        return results
