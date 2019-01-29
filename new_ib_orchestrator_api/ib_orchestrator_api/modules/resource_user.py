from ib_orchestrator_api.core.core import Core
from ib_orchestrator_api.core.errors import UserError
from .domain import Domain
from .resource_role import ResourceRole
from ib_orchestrator_api.core.utils import *


class ResourceUser(Core):
    def __init__(self, username=None, user_domain=None, role=None, role_id=None, password=None, is_active=False, url=None, session=None):
        self._id = None
        self.username = username
        self.password = password
        self.is_active = False
        self.url = url 
        self.session = session
        self.user_domain = self._get_user_domain(user_domain)
        self.role = self._get_resource_user_role(role)
        self.role_id = self._get_resource_user_role_id()
        
    def _get_user_domain(self, user_domain=None):
        if not user_domain:
            return None
        else:
            if not isinstance(user_domain, Domain):
                user_domain = Domain(url=self.url, session=self.session).get_domain(user_domain)
                return user_domain
            else:
                return user_domain

    def _get_resource_user_url(self):
        return self.url + URL_RESOURCE_USER
    
    def _get_resource_user_role(self, role=None):
        if not role:
            return None
        else:
            if not isinstance(role, ResourceRole):
                user_role = ResourceRole(url=self.url, session=self.session).get_resource_role(role)
                return user_role
            else:
                return user_role
    
    def _get_resource_user_role_id(self):
        if not self.role:
            return None
        else:
            return self.role._id
        
    def _get_dict_resource_user(self, username=None, domain=None):
        if not domain:
            domain = self.user_domain
        if not username:
            username = self.username

        tmp_users = self.get_all_resource_user()
        result_user = ''
        for user in tmp_users['result']:
            if user["username"] == username and user["domain_id"] == domain._id:
                result_user = user
                break
        
        return result_user
    
    def _check_self_resource_user(self):
        result_user = self._get_dict_resource_user()
        if not result_user:
            return False
        else:
            self._id = result_user.get('id')
            return True

    def _make_json(self):
        """
        Example JSON
        {'is_active': True, 
        'password': 'kv-worker1pass', 
        'role_id': 1, 
        'username': 'kv-worker1', 
        'domain_id': 2}
        """
        data = self.to_dict()
        if "_id" in data.keys():
            del data['_id']
        for key, value in data.items():
            if value is None or value == '':
                message = "Field '%s' can't be None" % str(key)

                #print(message)
                #print(str(key), value)
                raise UserError(error_message=message)
        #print(self.user_domain)
        if "user_domain" in data.keys():
            del data['user_domain']
        if "role" in data.keys():
            del data['role']
        data.update({'domain_id':self.user_domain._id})
        return data
    
    def to_dict(self):
        data = (vars(self)).copy()
        if 'url' in data.keys():
            del data['url']
        if 'session' in data.keys():
            del data['session']

        for key, value in data.items():
            if isinstance(getattr(self,key), Core):
                data.update({key:value.to_dict()})
        return data

        

    def get_resource_user(self, username=None, domain=None):
        if domain is None:
            domain = self.user_domain
        else:
            if not isinstance(domain, Core):
                domain = Domain(url=self.url, session=self.session).get_domain(domain)
        if not username:
            username = self.username

        tmp_users = self.get_all_resource_user()
        result_resource_user = ''
        for r_user in tmp_users['result']:
            if r_user["username"] == username and r_user["domain_id"] == domain._id:
                result_resource_user = r_user
                break
        
        if not result_resource_user:
            message = "There is no such resource_user '%s' in the domain '%s'" % username, domain.domain
            raise UserError(error_message=message)

        resource_user = ResourceUser(url=self.url, session=self.session)    
        for field in result_resource_user.keys():
            if field == 'id':
                setattr(resource_user, '_id', result_resource_user[field])
            if field in vars(resource_user).keys():
                setattr(resource_user, field, result_resource_user[field])
        return resource_user


    def get_all_resource_user(self):
        url = self._get_resource_user_url()
        result = self.session.get(url, verify=False)
        resource_users = json.loads(result.text)
        return resource_users  
    
    
    
    def create_resource_user(self):
        """
        Example resource user jeson
        {
            "is_active": true,
            "password": "workerpass",
            "role": "hostOwner",
            "role_id":1,
            "user_domain":"getaway-app",
            "username":	"worker"
        },
        """
        resource_user_json = self._make_json()
        url = self._get_resource_user_url()
        if not self._check_self_resource_user():
            response = self.session.put(url, json=resource_user_json, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                self._id = (json.loads(response.text)).get('id')
                return True
            else:
                message = "Error add  resource_user '%s' " % (resource_user_json['username'])
                raise UserError(error_message=message)


    def update_resource_user(self):
        url = self._get_resource_user_url()
        # print(url_resource_user)
        result = self.session.get(url, verify=False)
        # print(result.text)

        tmp_users = json.loads(result.text)
        user_id = ''
        for user in tmp_users['result']:
            if user["username"] == resource_user_json["username"]:
                user_id = user['id']

        url_resource_user = self.base_url + URL_RESOURCE_USER + "/" + str(user_id)
        # print(url_resource_user)
        url_resource_role = self.base_url + URL_RESOURCE_ROLE
        result = self.session.get(url_resource_role, verify=False)
        tmp_role = json.loads(result.text)
        role_id = ''
        for role in tmp_role['result']:
            if resource_user_json['role'] == role['name']:
                role_id = role['id']

        resource_user_json["role_id"] = int(role_id)
        del resource_user_json['role']
        # print(resource_user_json)
        response = self.session.patch(url_resource_user, json=resource_user_json, verify=False)
        if response.status_code == 200:
            return True
        else:
            raise UserError()

    def delete_resource_user(self, resource_user_name=None, domain_name=None):
        if not resource_user_name:
            resource_user_name = self.username
        if not domain_name:
            domain_name = self.user_domain
        else:
            if not isinstance(domain_name, Domain):
                domain_name = Domain(url=self.url, session=self.session).get_domain(domain_name)
                return domain_name
            else:
                return domain_name
        
        result = self._get_dict_resource_user(username=resource_user_name, domain=domain_name)
        domain_id = ''
        if not result:
            print("netu usera")
        else:
            domain_id = result.get('id')
        
        delete_url = self._get_resource_user_url() + '/' + str(domain_id)
        response = self.session.delete(delete_url, verify=False)
        #print(response)
        #print(response.text)
        if response.status_code == 200 or response.status_code == 204:
            return True
        else:
            return False