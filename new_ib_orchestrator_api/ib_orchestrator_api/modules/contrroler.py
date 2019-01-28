import requests
from ib_orchestrator_api.core.core import Core
from ib_orchestrator_api.core.errors import DomainError, DomainNameError, DomainIDError, DomainInControllerError
from .utils import *

"""
"controller":[
        {
            "descr":"Main controller",
            "enable":true,
            "name":"controller"
        }
"""
class Controller(Core):
    def __init__(self, name=None, description=None, enable=None, url=None, headers=None):
        self.name = name 
        self.descr = description
        self.enable = enable
        self.url = url + URL_CONTROLLER
        self.headers = headers
