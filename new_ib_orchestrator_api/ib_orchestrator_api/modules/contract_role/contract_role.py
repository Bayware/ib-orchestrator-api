import json
from ib_orchestrator_api.core.core import Core
from ib_orchestrator_api.core.errors import ContractError, ContractRoleError
from ib_orchestrator_api.core.utils import *
from ib_orchestrator_api.modules import Contract

class ContractRole(Core):
    def __init__(self, url, session, id=None, ):
        self.url = url
        self.session = session
        self.id = id










    def get_all_contracts_role(self):
        url = self.base_url + URL_CONTRACT_ROLE
        result = self.session.get(url, verify=False)
        all_contracts_role = json.loads(result.text)
        return all_contracts_role['result']







    def get_contracts_role_id(self, all_conract_role, contract_id, role_name):
        contract_role_id = ''
        for role in all_conract_role:
            if role['topic_id'] == contract_id and role['role_name'] == role_name:
                contract_role_id = role['id']
                break
        return contract_role_id



    def add_contracts_role(self, contract_role=None,
                           domain_name=None, domain_id=None, service_id=None):
        url = self.base_url + URL_CONTRACT_ROLE
        url_user = self.base_url + URL_USER
        url_service = "%sapi/v1/webpanel/servicetempl/%s/servicetemplrole" \
                      % (self.base_url, str(service_id))
        tmp_contract_role = contract_role.copy()
        result = self.session.get(url, verify=False)
        tmp_roles = json.loads(result.text)
        if not any(d["role_name"] == contract_role["role_name"] and
                   d["topic_id"] == contract_role["topic_id"] for d in tmp_roles['result']):
            response_roles = self.session.get(url_service, verify=False)
            service_roles = json.loads(response_roles.text)
            for service_role in service_roles["result"]:

                if contract_role["service_role"] == service_role["role_name"]:
                    contract_role["service_role_id"] = service_role["id"]
                    contract_role.update({
                        "description": service_role.get("description", ""),
                        "path_binary": service_role.get("path_binary", ""),
                        "path_params": service_role.get("path_params", ""),
                        "endpoint_rules": service_role.get("endpoint_rules", ""),
                        "program_data_params": service_role.get("program_data_params", ""),
                        "endpoint_params": service_role.get("endpoint_params", ""),
                        "token_params": service_role.get("token_params", "")})

            tmp_dict = {key: value for key, value in tmp_contract_role.items()
                        if value is None or value == '' or value == []}

            for key, value in tmp_dict.items():
                del tmp_contract_role[key]

            contract_role.update(tmp_contract_role)
            result = self.session.get(url_user, verify=False)
            domain_users = json.loads(result.text)
            for user in contract_role["users"]:
                for domain_user in domain_users["result"]:
                    if domain_user["username"] == user["user_name"] and domain_user["user_domain"] == domain_name:
                        user_id = domain_user["id"]
                        user["domain"].update({"domain_name": domain_name,
                                               "id": domain_id})
                        user.update({'domain_id': domain_id, 'id': user_id})

            response = self.session.put(url, json=contract_role, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                raise ContractError()
        else:
            return False




    def modify_contract_role(self, contract_role_name=None, contract_name=None, domain_name=None, data=None):
        url = self.base_url + URL_CONTRACT_ROLE
        result = self.session.get(url, verify=False)
        tmp_roles = json.loads(result.text)
        dict_domain = self.get_domain_list()
        # print(dict_domain)
        domain_id = self.get_domain_id(dict_domain['result'], domain_name)
        # print(domain_id)
        url_contracts = self.base_url + URL_CONTRACTS
        result = self.session.get(url_contracts, verify=False)
        topics = json.loads(result.text)
        # print(json.loads(result.text))
        topic_id = ''
        for topic in topics['result']:
            if topic['name'] == contract_name and topic['domain_id'] == domain_id:
                topic_id = topic['id']
                break

        if not topic_id:
            message = "wrong modify contract_role - contract '%s' in domain '%s' does not exist" % (
                contract_name, domain_name)
            raise ContractError(error_message=message)
        # print(topic_id)
        modify_role = {}
        for role in tmp_roles['result']:
            if role['role_name'] == contract_role_name and role['topic_id'] == topic_id:
                modify_role = role
                break

        if not modify_role:
            message = "wrong modify contract_role -  contract role '%s' in domain '%s' does not exist" % (
                contract_role_name, domain_name)
            raise ContractError(error_message=message)

        topic_role_id = modify_role['id']
        modify_url = url + '/' + str(topic_role_id)
        # print(modify_url)

        modify_role.update(data)
        response = self.session.post(modify_url, json=modify_role, verify=False)
        if response.status_code == 200 or response.status_code == 201:
            return True
        else:
            raise ContractError()




    def delete_contract_role(self, contract_role_name=None, contract_name=None, domain_name=None):
        url = self.base_url + URL_CONTRACT_ROLE
        result = self.session.get(url, verify=False)
        tmp_roles = json.loads(result.text)
        dict_domain = self.get_domain_list()
        # print(dict_domain)
        domain_id = self.get_domain_id(dict_domain['result'], domain_name)
        # print(domain_id)
        url_contracts = self.base_url + URL_CONTRACTS
        result = self.session.get(url_contracts, verify=False)
        topics = json.loads(result.text)

        topic_id = ''
        for topic in topics['result']:
            if topic['name'] == contract_name and topic['domain_id'] == domain_id:
                topic_id = topic['id']
                break

        if not topic_id:
            message = "wrong delete contract_role - contract '%s' in domain '%s' does not exist" % (
                contract_name, domain_name)
            raise ContractError(error_message=message)

        topic_role_id = ''
        for role in tmp_roles['result']:
            if role['role_name'] == contract_role_name and role['topic_id'] == topic_id:
                topic_role_id = role['id']
                break

        if not topic_role_id:
            message = "wrong delete contract_role -  contract role '%s' in domain '%s' does not exist" % (
                contract_role_name, domain_name)
            raise ContractError(error_message=message)

        delete_url = url + '/' + str(topic_role_id)
        response = self.session.delete(delete_url, verify=False)
        if response.status_code == 200 or response.status_code == 201:
            return True
        else:
            raise ContractError()