from ib_orchestrator_api.core.core import Core
from ib_orchestrator_api.core.errors import DomainError, DomainNameError, DomainIDError, DomainInControllerError
from ib_orchestrator_api.core.utils import *



class Domain(Core):
    def __init__(self, domain=None, domain_description=None, domain_type=None, auth_method=None, url=None, session=None):
        self._id = None
        self.domain = domain
        self.domain_description = domain_description 
        self.domain_type = domain_type
        self.auth_method = auth_method
        self.url = url
        self.session = session

    def _get_domain_url(self):
        return self.url + URL_DOMAIN
    
    def _make_json(self):
        """
        Example json
        {'auth_method': ['testAuth'], 
         'domain': 'test-app',
         'domain_description': 'testing app', 
         'domain_type': 'Application'}

        """
       
        domain_json = self.to_dict()
        del domain_json['_id']
        for key,value in domain_json.items():
            if not value:
                message = "Field '%s' can't be None" % str(key)
                print(message)
        

        return domain_json


    def _check_domain(self):
        if self._id is None:
            result_domain = self._get_domain_dict(self.domain)
            if not result_domain:
                return False
            else:
                self._id = result_domain.get('id')
                return True
        else:
            return True

    def _get_domain_dict(self, domain_name):
        #if not domain_name:
            #domain_name = self.domain
        domain_list = self.get_all_domains()
        result_domain = ''
        for domain in domain_list['result']:
            if domain['domain'] == domain_name:
                result_domain = domain
                break
        return result_domain

    def to_dict(self):
        data = (vars(self)).copy()
        if 'url' in data.keys():
            del data['url']
        if 'session' in data.keys():
            del data['session']
        return data

    
    def get_domain_id(self,  domain_name=None):
        if not domain_name:
            if self._id is None:
                domain_name = self.domain
            else:
                return self._id
        result_domain = self._get_domain_dict(domain_name)

        domain_id = ''
        if not result_domain:
            return ERORO
        else:
            domain_id = result_domain.get('id')
        
        return domain_id

    def get_all_domains(self):
        url = self._get_domain_url()
        result = self.session.get(url, verify=False)
        all_domain = json.loads(result.text)
        return all_domain

    def get_domain(self, domain_name=None):
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
                setattr(domain, '_id', result_domain[field])
            if field in vars(domain).keys():
                setattr(domain, field, result_domain[field])
        return domain

    def create_domain(self):
        url = self._get_domain_url()
        domain_json = self._make_json()
        if not self._check_domain():
            response = self.session.post(url, json=domain_json, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                self._id = (json.loads(response.text)).get('id')
                # print(self._id)
                return True
            else:
                message = "Error add domain: " + self.domain
                raise DomainError(error_message=message)
        else:

            message = "Domain '%s' already created" % self.domain
            #print(message)
            #print(self)
            #raise DomainError(error_message=message)

    def update_domain(self):
        if not self._check_domain():
            message = "Domain '%s' not created" % self.domain
            # print(message)
            raise DomainError(error_message=message)
        else:
            domain_json = self.to_dict()
            url = self._get_domain_url()
            patch_url = url + "/" + str(self._id)
            response = self.session.patch(patch_url, json=domain_json, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                message = "Error add domain:"
                # print(message)
                raise DomainError(error_message=message)
    
    def delete_domain(self, domain_name=None):
        if not domain_name:
            domain_name = self.domain
        if not self._check_domain():
            message = "Domain '%s' not created" % self.domain
            #print(message)
            # raise DomainError(error_message=message)
        else:
            url = self._get_domain_url()
            delete_url = url + "/" + str(self._id)
            response = self.session.delete(delete_url, verify=False)
            #print(response)
            #print(response.text)
        
        
        

        