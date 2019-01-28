from ib_orchestrator_api.core.core import Core
from .utils import *

class ResourceRole(Core):
    def __init__(self, name=None, url=None, session=None):
        self._id = None
        self.name = name
        self.url = url
        self.session = session

    def _get_resource_role_url(self):
        return self.url + URL_RESOURCE_ROLE
    
    def get_all_resource_role(self):
        url = self._get_resource_role_url()
        result = self.session.get(url, verify=False)
        tmp_role = json.loads(result.text)
        return tmp_role

    def get_resource_role(self, name=None):
        if not name:
            name = self.name
        
        all_resource_role = self.get_all_resource_role()
        resource_role = ''
        for role in all_resource_role['result']:
            if role['name'] == name:
                resource_role = role
                break

        if not resource_role:
            message = 'not resource_role'
            print(message)
        
        role = ResourceRole()
        for field in resource_role.keys():
            if field == 'id':
                setattr(role, '_id', resource_role[field])
            if field in vars(role).keys():
                setattr(role, field, resource_role[field])
        return role
