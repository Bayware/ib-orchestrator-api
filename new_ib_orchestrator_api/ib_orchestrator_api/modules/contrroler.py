from ib_orchestrator_api.core.core import Core
from ib_orchestrator_api.core.errors import DomainError, DomainNameError, DomainIDError, DomainInControllerError
from ib_orchestrator_api.core.utils import *

"""
"controller":[
        {
            "descr":"Main controller",
            "enable":true,
            "name":"controller"
        }
"""
class Controller(Core):
    def __init__(self, name=None, description=None, enable=None, url=None, session=None):
        self._id = None
        self.name = name 
        self.descr = description
        self.enable = enable
        self.url = url 
        self.session = session
    
    def _get_controller_url(self):
        return self.url + URL_CONTROLLER

    def _make_json(self):
        pass

    def get_all_controllers(self):
        url = self._get_controller_url()

    def add_controller(self, controller_json):
        controller_json.update({"host_fqdn": self.hostname,
                                "ip_management": self.ip_address})

        url = self._get_controller_url()

        result = self.session.get(url, verify=False)
        tmp_controllers = json.loads(result.text)
        if not any(d['name'] == controller_json['name'] for d in tmp_controllers['result']):
            response = self.session.put(url, json=controller_json, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                message = "Error add controller '%s'" % controller_json['name']
                raise ControllerError(error_message=message)
        else:
            return False

    def get_contrroler(self, controller_name=None):
        url = self._get_controller_url()
        if not controller_name:
            controller_name = self.name
        