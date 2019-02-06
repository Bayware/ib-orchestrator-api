from ib_orchestrator_api.core.core import Core
from ib_orchestrator_api.core.errors import ServiceTemplateRoleError
from ib_orchestrator_api.core.utils import *
from .template import Template



class TemplateRole(Core):
    def __init__(self, url, session, id=None,service_templ_id=None, role_name=None, description=None, permission=None,
                 code_binary=None,code_map=None, path_binary=None, path_params=None, endpoint_rules=None, program_data_params=None):
        self.id = id
        self.url = url
        self.session = session
        self.service_templ_id = self._get_service_templ_id(service_templ_id)
        self.role_name = role_name
        self.description = description
        self.permission = permission
        self.code_binary = code_binary
        self.code_map = code_map
        self.path_binary = path_binary 
        self.path_params = path_params
        self.endpoint_rules = endpoint_rules
        self.program_data_params = program_data_params

    def _get_templaterole_url(self):
        return self.url + URL_TEMPLATE_ROLE

    def _get_service_templ_id(self, service_templ_id):
        if not service_templ_id:
            return None
        else:
            if not isinstance(service_templ_id, Template):
                if isinstance(service_templ_id, int):
                    return service_templ_id
                if service_templ_id.isnumeric():
                    return int(service_templ_id)
                else:
                    message = "Wrong Value"
                    raise ServiceTemplateRoleError(error_message=message)
            else:
                service_templ_id = Template(url=self.url, session=self.session).get_template_id(service_templ_id)
                return int(service_templ_id)
            

    def _make_json(self):
        template_role_json = self.to_dict()
        del template_role_json['id']
        return template_role_json 

    def _get_template_role_dict(self, template_role_name=None):
        if not template_role_name:
            template_role_name = self.role_name
        all_template_role = self.get_all_template_role()
        result_template_role = ''
        for role in all_template_role['result']:
            if role['role_name'] == template_role_name:
                result_template_role = role
                break
        return result_template_role

    def _check_template_role(self):
        if self.id is None:
            template_role = self._get_template_role_dict()
            if not template_role:
                return False
            else:
                self.id = template_role.get('id')
                return True
        else:
            return True       


    def get_all_template_role(self):
        url = self._get_templaterole_url()
        result = self.session.get(url, verify=False)
        all_template_role = json.loads(result.text)
        return all_template_role

    def create_template_role(self):
        url = self._get_templaterole_url()
        if not self._check_template_role():
            template_role_json = self._make_json()
            response = self.session.put(url, json=template_role_json, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                result = json.loads(response.text)
                self.id = result.get("id")
                return True
            else:
                raise ServiceTemplateRoleError()
            

    def update_template_role(self):
        if not self._check_template_role():
            message = "template role can't modify, template role not created"
            raise ServiceTemplateRoleError(error_message=message)
        else:
            url = self._get_templaterole_url() + "/" + str(self.id)
            template_json = self._make_json()
            response = self.session.post(url, json=template_json, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                raise ServiceTemplateRoleError()

    def delete_template_role(self, template_role_name=None):
        pass