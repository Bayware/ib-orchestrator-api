import re
import socket
import requests
import json
from .core import Core
from .ib_api import IB_API
from ib_orchestrator_api.modules.utils import *
from ib_orchestrator_api.modules import *

class IBOrchestratorAPI(Core):
    def __init__(self, hostname, login, password, base_url, domain='default'):
        self.hostname = hostname
        self.domain_server = domain
        self.login = login
        self.password = password
        self.base_url = base_url
        self.session = None
        self.ip_address = self.get_ip_address(hostname)

    def domain(self, **kwargs):
        domain = Domain(url=self.base_url, session=self.session, **kwargs)
        return domain
    
    def user(self, **kwargs):
        user = User(url=self.base_url, session=self.session, **kwargs)
        return user

    def user_role(self, **kwargs):
        user_role = UserRole(url=self.base_url, session=self.session, **kwargs)
        return user_role

    def resource_user(self, **kwargs):
        resource_user = ResourceUser(url=self.base_url, session=self.session, **kwargs)
        return resource_user

    def resource_role(self, **kwargs):
        resource_role = ResourceRole(url=self.base_url, session=self.session, **kwargs)
        return resource_role

    def new_authorization(self):
        session = requests.session()
        token_url = self.base_url + "api/v1/webpanel/token"
        response = session.post(
            token_url,
            json={'domain': self.domain_server, 'username': self.login, 'password': self.password},
            verify=False)
        if response.status_code == 200 or response.status_code == 201:
            tmp_token = json.loads(response.text)
            token = "Bearer " + tmp_token.get("token")
            session.headers.update({"Authorization": token,
                                    'Content-Type': 'application/json'})
            self.session = session
        else:
            raise LoginError()
    
    """
    def domain(self, **kwargs):
        domain = Domain(url=self.base_url, headers=self.headers, **kwargs)
        return domain
    
    def controller(self, **kwargs):
        domain = Domain(url=self.base_url, headers=self.headers, **kwargs)
        return domain

    def user(self, **kwargs):
        domain = Domain(url=self.base_url, headers=self.headers, **kwargs)
        return domain  

    def resource_user(self, **kwargs):
        resource_user = Resource_User(url=self.base_url, headers=self.headers, **kwargs)
        return resource_user
    """
    @staticmethod
    def read_from_json(filename):
        with open(filename, 'r') as f:
            json_dict = json.loads(f.read())
        return json_dict

    @staticmethod
    def get_ip_address(hostname):
        regex = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        result = regex.match(hostname)
        address = ''
        if not result:
            address = socket.gethostbyname(hostname)
        else:
            address = hostname
        return address

    def authorization(self):
        token_url = self.base_url + "api/v1/webpanel/token"
        response = requests.post(
            token_url,
            json={'domain': self.domain_server, 'username': self.login, 'password': self.password},
            verify=False)
        if response.status_code == 200 or response.status_code == 201:
            tmp_token = json.loads(response.text)
            token = "Bearer " + tmp_token.get("token")
            self.headers.update({"Authorization": token})
        else:
            raise LoginError()