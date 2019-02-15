import json
from ib_orchestrator_api.core.core import Core
from ib_orchestrator_api.core.errors import DomainError, DomainNameError, DomainIDError, DomainInControllerError
from ib_orchestrator_api.core.utils import *


class Domain(Core):
    def __init__(self, url, session, id=None, domain=None, domain_description=None, domain_type=None, auth_method=None):
        self.id = id
        self.domain = domain
        self.domain_description = domain_description
        self.domain_type = domain_type
        self.auth_method = auth_method
        self.url = url
        self.session = session

    def _get_domain_url(self):
        """Internal class method: return url which is used for get, create, update, delete domain"""
        return self.url + URL_DOMAIN

    def __make_json(self):
        """
        Private class method, method make json object, which is used to upload to the server.

        Example json
        {'auth_method': ['testAuth'], 
         'domain': 'test-app',
         'domain_description': 'testing app', 
         'domain_type': 'Application'}

        """

        domain_json = self.to_dict()
        del domain_json['id']
        for key, value in domain_json.items():
            if not value:
                message = "Field '%s' can't be None" % str(key)
                print(message)

        return domain_json

    def _check_domain(self):
        """Internal class method, checks if such an domain exists on the server"""
        if self.id is None:
            result_domain = self._get_domain_dict(self.domain)
            if not result_domain:
                return False
            else:
                self.id = result_domain.get('id')
                return True
        else:
            return True

    def _get_domain_dict(self, domain_name):
        """Internal class method: accept list with all domains, check if such domain in this list, and return domain dict
        or return empty dict"""
        # if not domain_name:
        # domain_name = self.domain
        domain_list = self.get_all_domains()
        result_domain = ''
        for domain in domain_list['result']:
            if domain['domain'] == domain_name:
                result_domain = domain
                break
        return result_domain

    def to_dict(self):
        """Base class override method. Representation of class attributes as dict"""
        data = (vars(self)).copy()
        if 'url' in data.keys():
            del data['url']
        if 'session' in data.keys():
            del data['session']
        return data

    def get_domain_id(self, domain_name=None):
        """Method return domain id by name, if domain exists"""
        if not domain_name:
            if self.id is None:
                domain_name = self.domain
            else:
                return self.id
        result_domain = self._get_domain_dict(domain_name)

        domain_id = ''
        if not result_domain:
            raise DomainIDError()
        else:
            domain_id = result_domain.get('id')

        return domain_id

    def get_all_domains(self):
        """Method retruns all domains that exist"""
        url = self._get_domain_url()
        result = self.session.get(url, verify=False)
        all_domain = json.loads(result.text)
        return all_domain

    def get_domain(self, domain_name=None):
        """Method return object domain by name, if domain exists"""
        if not domain_name:
            domain_name = self.domain
        result_domain = self._get_domain_dict(domain_name)

        if not result_domain:
            message = "Domain '%s' not found " % domain_name
            # print(message)
            # return None
            raise DomainNameError(error_message=message)
        # print(result_domain)
        domain = Domain(url=self.url, session=self.session)
        for field in result_domain.keys():
            if field == 'id':
                setattr(domain, 'id', result_domain[field])
            if field in vars(domain).keys():
                setattr(domain, field, result_domain[field])
        return domain

    def create_domain(self):
        """Create domain on server"""
        url = self._get_domain_url()
        domain_json = self.__make_json()
        if not self._check_domain():
            response = self.session.post(url, json=domain_json, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                self.id = (json.loads(response.text)).get('id')
                # print(self.id)
                return response.text
            else:
                message = "Error add domain: " + self.domain
                raise DomainError(error_message=message)
        else:

            message = "Domain '%s' already created" % self.domain
            return message

    def update_domain(self):
        """Update domain on server"""
        if not self._check_domain():
            message = "Domain '%s' not created" % self.domain
            # print(message)
            raise DomainError(error_message=message)
        else:
            domain_json = self.to_dict()
            url = self._get_domain_url()
            patch_url = url + "/" + str(self.id)
            response = self.session.patch(patch_url, json=domain_json, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                message = "Error update domain:"
                # print(message)
                raise DomainError(error_message=message)

    def delete_domain(self, domain_name=None):
        """Delete domain from server"""
        if not domain_name:
            domain_name = self.domain

        domain_id = self.get_domain_id(domain_name=domain_name)
        if not domain_id:
            message = "Wrong domain"
            raise DomainError(error_message=message)
        else:
            url = self._get_domain_url()
            delete_url = url + "/" + str(domain_id)
            response = self.session.delete(delete_url, verify=False)
            if response.status_code == 204:
                message = "Domain has been delete"
                return message
