import json
import requests
from ib_orchestrator_api.core.core import Core
from ib_orchestrator_api.core.errors import UserError, UserInControllerError
from .domain import Domain
from ib_orchestrator_api.core.utils import *

class User(Core):
    def __init__(self, url, session, id=None, first_name=None, is_active=None, password=None, repeat_password=None, roles=None, 
                        user_auth_method=None, user_domain=None, username=None):

        self._id = id
        self.first_name = first_name
        self.is_active = is_active 
        self.password = password
        self.repeat_password = repeat_password
        self.user_auth_method = user_auth_method
        self.username = username
        self.url = url 
        self.session = session
        self.user_domain = self._get_user_domain(user_domain)
        self.roles = self._get_user_roles(roles)

    def _get_user_domain(self, user_domain=None):
        """Method called when creating an instance of a class, initializes user domain attribute """
        if not user_domain:
            return None
        else:
            if not isinstance(user_domain, Domain):
                user_domain = Domain(url=self.url, session=self.session).get_domain(user_domain)
                return user_domain
            else:
                return user_domain

    def _get_user_roles(self, role=None):
        """Method called when creating an instance of a class, initializes user role attribute """
        if not role:
            return None
        else:
            if isinstance(role, list):
                return role
            else:
                message = "roles must be list"
                raise UserError(error_message=message)


    def _get_user_url(self):
        """Internal class method: return url which is used for get, create, update, delete user"""
        return self.url + URL_USER
    
    def _get_dict_user(self, username=None, domain=None):
        if not domain:
            domain = self.user_domain
        if not username:
            username = self.username

        tmp_users = self.get_all_user()
        result_user = ''
        for user in tmp_users['result']:
            if user["username"] == username and user["user_domain"] == domain.domain:
                result_user = user
                break
        
        return result_user
    
    def _check_self_user(self):
        """Internal class method, checks if such an user exists on the server"""
        result_user = self._get_dict_user()
        if not result_user:
            return False
        else:
            self._id = result_user.get('id')
            return True
            
    def _check_user_role(self):
        url = self.url + URL_USER_ROLE
        #print(self.user_domain)
        #print("user domain: ", self.user_domain)
        payload = {"domain": self.user_domain.domain}
        result = self.session.get(url, params=payload, verify=False)
        roles = json.loads(result.text)
        #print(result)
        #print(roles['results'])
        #print(self.roles[0])
        for role in self.roles:            
            if not any(r['role_name'] == role for r in roles['results']):
                return False
            else:
                return True
            

    def _make_json(self):
        """
        Example JSON
        {'first_name': 'User for tests', 
        'is_active': 'True', 
        'password': '12345', 
        'repeat_password': '12345', 
        'roles': ['testAdmin'], 
        'user_auth_method': 'Local', 
        'user_domain': 'default', 
        'username': 'test'}


        """

        data = self.to_dict()
        if "_id" in data.keys():
            del data['_id']
        for key, value in data.items():
            if value is None or value == '':
                message = "Field '%s' can't be None" % str(key)

                # print(message)
                # print(str(key), value)
                raise UserError(error_message=message)
        # print(self.user_domain)
        data.update({'user_domain':self.user_domain.domain})
        return data

    def to_dict(self):
        """Base class override method. Representation of class attributes as dict"""
        data = (vars(self)).copy()
        if 'url' in data.keys():
            del data['url']
        if 'session' in data.keys():
            del data['session']

        for key, value in data.items():
            if isinstance(getattr(self,key), Core):
                data.update({key:value.to_dict()})
        return data

    def get_all_user(self):
        url = self._get_user_url()
        result = self.session.get(url, verify=False)
        all_users = json.loads(result.text)
        return all_users

    def get_user(self, username=None, domain=None):
        if domain is None:
            domain = self.user_domain
        else:
            if not isinstance(domain, Domain):
                domain = Domain(url=self.url, session=self.session).get_domain(domain)
        if not username:
            username = self.username
            
        result_user = self._get_dict_user(username=username, domain=domain)
        
        if not result_user:
            #print(domain.domain)
            message = "There is no such user '%s' in the domain '%s'" % (str(username), str(domain.domain))
            return None
            #raise UserError(error_message=message)

        user = User(url=self.url, session=self.session)    
        for field in result_user.keys():
            if field == 'id':
                setattr(user, '_id', result_user[field])
            if field in vars(user).keys():
                setattr(user, field, result_user[field])
        return user
    
    
        
    def create_user(self):
        
        if self._check_user_role():
            user_json = self._make_json() 
        else:
            print("wrong user error")
        
        if not self._check_self_user():
            url = self._get_user_url()
            response = self.session.post(url, json=user_json, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                self._id = (json.loads(response.text)).get('id')
                return True
            else:
                print(response.text)
                #message = "Error add user '%s' in domain '%s' " % (user_json['username'], user_json['user_domain'] )
                #raise UserError(error_message=message)
        else:
            return False
        
    def update_user(self):
        if not self._check_self_user():
            message = "User dont created"
            print(message)
        else:
            if self._check_user_role():
                user_json = self._make_json() 
            else:
                print("wrong user error")

            url = self._get_user_url() + "/" + str(self._id)
            response = self.session.patch(url, json=user_json, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                print(response.text)

    
    def delete_user(self, username=None, domain_name=None):
        if not username:
            username = self.username
        if not domain_name:
            domain_name = self.user_domain
        else:
            if not isinstance(domain_name, Domain):
                domain_name = Domain(url=self.url, session=self.session).get_domain(domain_name)
                return domain_name
            else:
                return domain_name
        result = self._get_dict_user(username=username, domain=domain_name)
        user_id = ''
        if not result:
            print("netu usera")
        else:
            user_id = result.get('id')
        
        delete_url = self._get_user_url() + '/' + str(user_id)
        response = self.session.delete(delete_url, verify=False)
        if response.status_code == 204:
            return True
        else:
            return False

