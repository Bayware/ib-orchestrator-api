from ib_orchestrator_api.core.core import Core
from ib_orchestrator_api.core.utils import *

class UserRole(Core):
    def __init__(self, name=None, url=None, session=None):
        self._id = None
        self.name = name
        self.url = url
        self.session = session
 
    def _get_user_role_url(self):
        return self.url + URL_USER

    def _get_user_role_name(self, name=None):
        if not name:
            return None
        else:
            pass

    
    def get_all_user_role(self):
        url = self._get_user_role_url()
        result = self.session.get(url, verify=False)
        tmp_role = json.loads(result.text)
        return tmp_role

    def get_user_role(self, name=None):
        if not name:
            name = self.name
        
        all_resource_role = self.get_all_resource_role()
        resource_role = ''
        for role in all_resource_role['result']:
            if role['name'] == name:
                resource_role = role
                break

        if not resource_role:
            message = 'not user_role'
            print(message)

        for field in resource_role.keys():
            if field == 'id':
                setattr(self, '_id', resource_role[field])
            if field in vars(self).keys():
                setattr(self, field, resource_role[field])
        return self

