from ib_orchestrator_api.core.core import Core
from ib_orchestrator_api.core.errors import ServiceTemplateError
from ib_orchestrator_api.core.utils import *





class Template(Core):
    def __init__(self, url, session, id=None, domains=None, service_name=None, description=None, enable=None):
        self.id = id
        self.url = url
        self.session = session
        self.domains = self._get_template_domains(domains)
        self.service_name = service_name
        self.description = description
        self.enable = enable
    
    def _get_template_url(self):
        return self.url + URL_TEMPLATE

    def _get_template_domains(self, domains):
        """Method called when creating an instance of a class, initializes domains attribute """
        if not domains:
            return None
        else:
            if isinstance(domains, list):
                return domains
            else:
                message = "domains must be list"
                raise ServiceTemplateError(error_message=message)

    def _make_json(self):
        """
        Example JSON
        {'domains': [{'domain_name': 'getaway-app', 'id': 2}, {'domain_name': 'voting-app', 'id': 3}], 
        'service_name': 'client-server',
        'description': 'Point-to-point with Dijkstra path'}

        """
        template_json = self.to_dict()
        del template_json['id']
        for key,value in template_json .items():
            if not value:
                message = "Field '%s' can't be None" % str(key)
                print(message)
        return template_json        


    def _get_template_dict(self, template_name=None):
        if not template_name:
            template_name = self.service_name
        all_template = self.get_all_templates()
        result_template = ''
        for template in all_template['result']:
            if template['service_name'] == template_name:
                result_template = template
                break
        return result_template

    def _check_template(self):
        if self.id is None:
            template = self._get_template_dict()
            if not template:
                return False
            else:
                self.id = template.get('id')
                return True
        else:
            return True
        

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
    
    def get_all_templates(self):
        url = self._get_template_url()
        result = self.session.get(url, verify=False)
        all_template = json.loads(result.text)
        return all_template
    
    def get_template(self, template_name):
        template_dict = self._get_template_dict(template_name)
        if not template_dict:
            raise ServiceTemplateError()
        
        template = Template(url=self.url, session=self.session)
        for field in template_dict.keys():
            if field == 'id':
                setattr(template, 'id', template_dict[field])
            if field in vars(template).keys():
                setattr(template, field, template_dict[field])
        return template

    def get_template_id(self, template_name):
        all_templates = self.get_all_templates()
        template_id = ''
        for template in all_templates['result']:
            if template['service_name'] == template_name:
                template_id = template['id']
                break

        return template_id

    def create_template(self):
        url = self._get_template_url()
        template_json = self._make_json()
        if not self._check_template():
            response = self.session.put(url, json=template_json, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                result = json.loads(response.text)
                self.id = result.get("id")
            else:
                print(response)
                print(response.text)
                raise ServiceTemplateError()
        else:
            message = "template '%s' already created" % self.service_name
            print(message)
    
    def update_template(self):
        if not self._check_template():
            message = "template can't modify, template not created"
            raise ServiceTemplateError(error_message=message)
        else:
            url = self._get_template_url() + "/" + str(self.id)
            template_json = self._make_json()
            response = self.session.post(url, json=template_json, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                raise ServiceTemplateError()
    
    def delete_template(self, service_name=None):
        if not service_name:
            service_name = self.service_name
        template_id = self.get_template_id(service_name)
        if not template_id:
            message = "wrong template name"
            raise ServiceTemplateError(error_message=message)
        else:
            url = self._get_template_url() + "/" + str(template_id)
            response = self.session.delete(url, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                raise ServiceTemplateError()