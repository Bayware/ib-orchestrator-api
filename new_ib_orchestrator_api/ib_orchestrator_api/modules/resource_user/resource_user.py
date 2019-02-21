import json
from ib_orchestrator_api.core.core import Core
from ib_orchestrator_api.core.errors import UserError
from ib_orchestrator_api.modules.domain import Domain
from ib_orchestrator_api.modules.resource_user_role.resource_role import ResourceRole
from ib_orchestrator_api.core.utils import *


class ResourceUser(Core):
    def __init__(self, url, session, id=None, username=None, user_domain=None, role=None, role_id=None, password=None,
                 is_active=None):
        self.id = id
        self.username = username
        self.password = password
        self.is_active = is_active
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
        """Internal class method: return url which is used for get, create, update, delete resource user"""
        return self.url + URL_RESOURCE_USER

    def _get_resource_user_role(self, user_role=None):
        if not user_role:
            return None
        else:
            if not isinstance(user_role, ResourceRole):
                user_role = ResourceRole(url=self.url, session=self.session).get_resource_role(user_role)
                return user_role
            else:
                return user_role

    def _get_resource_user_role_id(self):
        if not self.role:
            return None
        else:
            return self.role.id

    def _get_dict_resource_user(self, username=None, domain=None):
        if not domain:
            domain = self.user_domain
        if not username:
            username = self.username

        tmp_users = self.get_all_resource_user()
        result_user = ''
        for user in tmp_users['result']:
            if user["username"] == username and user["domain_id"] == domain.id:
                result_user = user
                break

        return result_user

    def _check_self_resource_user(self):
        """Internal class method, checks if such an resource user exists on the server"""
        result_user = self._get_dict_resource_user()
        if not result_user:
            return False
        else:
            self.id = result_user.get('id')
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
        if "id" in data.keys():
            del data['id']
        for key, value in data.items():
            if value is None or value == '':
                message = "Field '%s' can't be None" % str(key)
                # print(message)
                # print(str(key), value)
                raise UserError(error_message=message)
        # print(self.user_domain)
        if "user_domain" in data.keys():
            del data['user_domain']
        if "role" in data.keys():
            del data['role']
        data.update({'domain_id': self.user_domain.id})
        return data

    def to_dict(self):
        """Base class override method. Representation of class attributes as dict"""
        data = (vars(self)).copy()
        if 'url' in data.keys():
            del data['url']
        if 'session' in data.keys():
            del data['session']

        for key, value in data.items():
            if isinstance(getattr(self, key), Core):
                data.update({key: value.to_dict()})
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
            if r_user["username"] == username and r_user["domain_id"] == domain.id:
                result_resource_user = r_user
                break

        if not result_resource_user:
            message = "There is no such resource_user '%s' in the domain '%s'" % username, domain.domain
            raise UserError(error_message=message)

        resource_user = ResourceUser(url=self.url, session=self.session)
        for field in result_resource_user.keys():
            if field == 'id':
                setattr(resource_user, 'id', result_resource_user[field])
            if field in vars(resource_user).keys():
                setattr(resource_user, field, result_resource_user[field])
        return resource_user

    def get_all_resource_user(self):
        url = self._get_resource_user_url()
        result = self.session.get(url, verify=False)
        resource_users = json.loads(result.text)
        return resource_users

    def get_all_in_domain(self, domain_name):
        url = self._get_resource_user_url()
        payload = {'domain.domain_name': domain_name}
        result = self.session.get(url, params=payload, verify=False)
        response = json.loads(result.text)
        return response

    def get_resource_user_id(self, username, domain_name):
        url = self._get_resource_user_url()
        payload = {"username": username, 'domain.domain_name': domain_name}
        result = self.session.get(url, params=payload, verify=False)
        response = json.loads(result.text)
        # print(response)
        if response['count_all'] == 0:
            raise UserError()
        else:
            return response['result'][0].get('id')

    def create_resource_user(self):
        """
        Example resource user jeson
        {
            "is_active": true,
            "password": "test",
            "role": "host",
            "role_id":1,
            "user_domain":"test-app",
            "username":	"test"
        },
        """
        resource_user_json = self._make_json()
        url = self._get_resource_user_url()
        if not self._check_self_resource_user():
            response = self.session.put(url, json=resource_user_json, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                self.id = (json.loads(response.text)).get('id')
                return response.text
            else:
                message = "Error add  resource_user '%s' " % (resource_user_json['username'])
                raise UserError(error_message=message)

    def update_resource_user(self):
        update_data=''
        if update_data:
            pass
        # else:
            user_json = dict([(vkey, vdata) for vkey, vdata in self.to_dict().items() if vdata])
        #print(user_json)
        # url = self._get_resource_user_url() + "/" + str(self.id)
        # response = self.session.patch(url, json=user_json, verify=False)
        # if response.status_code == 200 or response.status_code == 201:
        # return True
        # else:
        # print(response.text)

    def delete_resource_user(self, username, domain_name):
        resource_user_id = self.get_resource_user_id(username=username, domain_name=domain_name)
        # print(resource_user_id)
        url = self._get_resource_user_url() + "/" + str(resource_user_id)
        # print(url)
        response = self.session.delete(url, verify=False)
        return response