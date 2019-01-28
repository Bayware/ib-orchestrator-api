#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json
import re
import socket
import warnings
import hashlib
import itertools
from .errors import *
from .core import Core
from ib_orchestrator_api.modules import *

"""
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


warnings.filterwarnings('ignore')
# logging.basicConfig(filename='example.log', level=logging.DEBUG)

URL_USER = "api/v1/webpanel/identity/api/user"
URL_DOMAIN = "api/v1/webpanel/identity/api/domain"
URL_CONTROLLER = "api/v1/webpanel/controller"
URL_CONTRACTS = "api/v1/webpanel/topic"
URL_CONTRACT_ROLE = "api/v1/webpanel/topicrole"
URL_ZONE = "api/v1/webpanel/subnet"
URL_TEMPLATE = "api/v1/webpanel/servicetempl"
URL_TEMPLATE_ROLE = "api/v1/webpanel/servicetemplaterole"
URL_CONFIGURE_LINK = "api/v1/webpanel/configured_link"
URL_RESOURCE_USER = "api/v1/webpanel/resource_user"
URL_RESOURCE_ROLE = "api/v1/webpanel/resource_role"
"""
class Test():
    def test_method(self):
        print("sjgjskjgjg")

        
class IBOrchestratorAPI(Core):
    def __init__(self, hostname, login, password, base_url, domain='default'):
        self.hostname = hostname
        self.domain_server = domain
        self.login = login
        self.password = password
        self.base_url = base_url
        self.headers = {'Content-Type': 'application/json'}
        self.ip_address = self.get_ip_address(hostname)
        
    
    def domain(self, **kwargs):
        domain = Domain(url=self.base_url, headers=self.headers, **kwargs)
        return domain
    
    def controller(self, **kwargs):
        domain = Domain(url=self.base_url, headers=self.headers, **kwargs)
        return domain

    def user(self, **kwargs):
        domain = Domain(url=self.base_url, headers=self.headers, **kwargs)
        return domain  

    def resource_user(self, **kwargs):
        resource_user = Resource_User(url=self.base_url, headers=self.headers, **kwargs)
        return resource_user

    @staticmethod
    def read_from_json(filename):
        with open(filename, 'r') as f:
            json_dict = json.loads(f.read())
        return json_dict

    @staticmethod
    def get_ip_address(hostname):
        regex = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
        result = regex.match(hostname)
        address = ''
        if not result:
            address = socket.gethostbyname(hostname)
        else:
            address = hostname
        return address


    def get_domain_list(self):
        url_domain = self.base_url + URL_DOMAIN
        result = requests.get(url_domain, verify=False, headers=self.headers)
        domain_list = json.loads(result.text)
        return domain_list

    def get_service_list(self):
        url_service = self.base_url + URL_TEMPLATE
        result = requests.get(url_service, verify=False, headers=self.headers)
        service_list = json.loads(result.text)
        return service_list

    @staticmethod
    def get_domain_id(domain_list, domain_name):
        domain_id = ''
        for domain in domain_list:
            if domain['domain'] == domain_name:
                domain_id = domain['id']
        if domain_id is None or domain_id is '':
            message = "Wrong domain name: " + domain_name
            raise DomainNameError(error_message=message)
        return domain_id

    def authorization(self):
        token_url = self.base_url + "api/v1/webpanel/token"
        response = requests.post(
            token_url,
            json={'domain': self.domain_server, 'username': self.login, 'password': self.password},
            verify=False)
        if response.status_code == 200 or response.status_code == 201:
            tmp_token = json.loads(response.text)
            token = "Bearer " + tmp_token.get("token")
            self.headers.update({"Authorization": token})
        else:
            raise LoginError()
    
    def new_authorization(self):
        session = requests.session()
        token_url = self.base_url + "api/v1/webpanel/token"
        response = session.post(
            token_url,
            json={'domain': self.domain_server, 'username': self.login, 'password': self.password},
            verify=False)
        if response.status_code == 200 or response.status_code == 201:
            tmp_token = json.loads(response.text)
            token = "Bearer " + tmp_token.get("token")
            session.headers.update({"Authorization": token})
        else:
            raise LoginError()

    def add_domain(self, domain_json):
        url_domain = self.base_url + URL_DOMAIN
        result = requests.get(url_domain, verify=False, headers=self.headers)
        tmp_domain = json.loads(result.text)
        if not any(d['domain'] == domain_json['domain'] for d in tmp_domain['result']):
            response = requests.post(url_domain, json=domain_json, headers=self.headers, verify=False)

            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                message = "Error add domain: " + domain_json['domain']
                raise DomainError(error_message=message)
        else:
            return False

    def add_user(self, user_json):
        url_user = self.base_url + URL_USER
        result = requests.get(url_user, verify=False, headers=self.headers)
        tmp_users = json.loads(result.text)
        if not any((d['username'] == user_json['username'] and
                    d['user_domain'] == user_json['user_domain']) for d in tmp_users['result']):
            response = requests.post(url_user, json=user_json, headers=self.headers, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                message = "Error add user '%s' in domain '%s' " % (user_json['username'], user_json['user_domain'] )
                raise UserError(error_message=message)
        else:
            return False

    def add_resource_user(self, resource_user_json):
        url_resource_user = self.base_url + URL_RESOURCE_USER
        result = requests.get(url_resource_user, verify=False, headers=self.headers)
        tmp_users = json.loads(result.text)
        url_resource_role = self.base_url + URL_RESOURCE_ROLE
        result = requests.get(url_resource_role, verify=False, headers=self.headers)
        tmp_role = json.loads(result.text)

        role_id = ''
        for role in tmp_role['result']:
            if resource_user_json['role'] == role['name']:
                role_id = role['id']

        if not role_id:
            message = "wrong role '%s' in resource_user '%s'" % (
                resource_user_json['role'], resource_user_json['username'])
            raise UserError(error_message=message)

        resource_user_json["role_id"] = int(role_id)
        del resource_user_json['role']

        dict_domain = self.get_domain_list()
        domain_id = self.get_domain_id(dict_domain['result'], resource_user_json["user_domain"])

        resource_user_json.update({"domain_id": domain_id})
        del resource_user_json["user_domain"]
        # print(resource_user_json)

        if not any((d['username'] == resource_user_json['username'] and
                    d['domain_id'] == resource_user_json['domain_id']) for d in tmp_users['result']):
            response = requests.put(url_resource_user, json=resource_user_json, headers=self.headers, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                message = "Error add  resource_user '%s' " % (resource_user_json['username'])
                raise UserError(error_message=message)
        else:
            return False

        """
         for d in tmp_users['result']:
                if (d['username'] == resource_user_json['username'] and
                    d['domain_id'] == resource_user_json['domain_id']):
                    url = url_resource_user + "/"+ str(d['id'])
                    response = requests.patch(url, json=resource_user_json, headers=self.headers, verify=False)
                    print(response.text)
        """

    def patch_resource_user(self, resource_user_json):
        url_resource_user = self.base_url + URL_RESOURCE_USER
        # print(url_resource_user)
        result = requests.get(url_resource_user, verify=False, headers=self.headers)
        # print(result.text)

        tmp_users = json.loads(result.text)
        user_id = ''
        for user in tmp_users['result']:
            if user["username"] == resource_user_json["username"]:
                user_id = user['id']

        url_resource_user = self.base_url + URL_RESOURCE_USER + "/" + str(user_id)
        # print(url_resource_user)
        url_resource_role = self.base_url + URL_RESOURCE_ROLE
        result = requests.get(url_resource_role, verify=False, headers=self.headers)
        tmp_role = json.loads(result.text)
        role_id = ''
        for role in tmp_role['result']:
            if resource_user_json['role'] == role['name']:
                role_id = role['id']

        resource_user_json["role_id"] = int(role_id)
        del resource_user_json['role']
        # print(resource_user_json)
        response = requests.patch(url_resource_user, json=resource_user_json, headers=self.headers, verify=False)
        if response.status_code == 200:
            return True
        else:
            raise UserError()

    def add_zone(self, zone_json):
        url = self.base_url + URL_CONTROLLER
        controller_result = requests.get(url, verify=False, headers=self.headers)
        tmp_controllers = json.loads(controller_result.text)
        controller_pri_id = ""
        controller_sec_id = ""
        for controller in tmp_controllers['result']:
            if controller['name'] == zone_json["controller_pri_id"]:
                controller_pri_id = str(controller['id'])
            if controller['name'] == zone_json["controller_sec_id"]:
                controller_sec_id = str(controller['id'])

        zone_json.update({"controller_pri_id": controller_pri_id,
                          "controller_sec_id": controller_sec_id})
        url_zone = self.base_url + "api/v1/webpanel/subnet"
        result = requests.get(url_zone, verify=False, headers=self.headers)
        tmp_zone = json.loads(result.text)
        if not any(d['name'] == zone_json['name'] for d in tmp_zone['result']):
            response = requests.put(url_zone, json=zone_json, headers=self.headers, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                message = "Error add zone '%s'" % zone_json['name']
                raise ZoneError(error_message=message)
        else:
            return False

    def add_managed_network(self, managed_network, zone=None, zone_id=None):
        if zone_id is None:
            if zone is None:
                return "Zone Error"
            else:
                url_zone = self.base_url + URL_ZONE
                result = requests.get(url_zone, verify=False, headers=self.headers)
                tmp_zone = json.loads(result.text)
                for subnet in tmp_zone['result']:
                    if subnet['name'] == zone:
                        zone_id = str(subnet['id'])
                    else:
                        return "you input invalid zone"

        url = self.base_url + "api/v1/webpanel/subnet/" + zone_id + "/managed"
        managed_network.update({"subnet_id": zone_id})
        result = requests.get(url, verify=False, headers=self.headers)
        tmp_managed = json.loads(result.text)

        if not any(d["network_prefix"] == managed_network["network_prefix"] for d in tmp_managed['result']):
            response = requests.put(url, json=managed_network, headers=self.headers, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                raise ManagedNetworkError()
        else:
            return False

    def add_zone_managed_network(self, managed_network):
        url_subnet = self.base_url + URL_ZONE
        response_subnet = requests.get(url_subnet, verify=False, headers=self.headers)

        dict_domain = self.get_domain_list()
        domain_id = ""
        for domain in dict_domain['result']:
            if domain['domain'] == managed_network["tunnel_switch_domain_id"]:
                domain_id = str(domain['id'])

        if domain_id == "":
            return DomainIDError()

        zone_id = ""
        dict_subnet = json.loads(response_subnet.text)
        for subnet in dict_subnet['result']:
            if subnet['name'] == managed_network["subnet_id"]:
                zone_id = str(subnet['id'])

        cnt = 0
        if "networks" in managed_network:
            networks_prefix = managed_network["networks"]
            del managed_network["networks"]
            for prefix in networks_prefix:
                network = managed_network
                network["subnet_id"] = zone_id
                network["network_prefix"] = prefix
                network["tunnel_switch_domain_id"] = domain_id
                if self.add_managed_network(managed_network=network, zone_id=zone_id):
                    cnt += 1

        if "network_files" in managed_network:
            for network_file in managed_network["network_files"]:
                tmp_network = self.read_from_json(network_file)
                for prefix in tmp_network["networks"]:
                    network = managed_network
                    network["subnet_id"] = zone_id
                    network["network_prefix"] = prefix
                    network["tunnel_switch_domain_id"] = domain_id
                    if self.add_managed_network(managed_network=network, zone_id=zone_id):
                        cnt += 1

        return cnt

    def add_controller(self, controller_json):
        controller_json.update({"host_fqdn": self.hostname,
                                "ip_management": self.ip_address})

        url = self.base_url + URL_CONTROLLER

        result = requests.get(url, verify=False, headers=self.headers)
        tmp_controllers = json.loads(result.text)
        if not any(d['name'] == controller_json['name'] for d in tmp_controllers['result']):
            response = requests.put(url, json=controller_json, headers=self.headers, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                message = "Error add controller '%s'" % controller_json['name']
                raise ControllerError(error_message=message)
        else:
            return False

    def get_contrroler(self, **kwargs):
        url = self.base_url + URL_CONTROLLER
        data = {}
        for key in kwargs:
            data.update({key: kwargs.get(key)})
        result = requests.get(url, params=data, headers=self.headers)
        return result

    def modify_service_template_role(self, template_role, tmp_template_roles):
        """
        Modification service template: accept service_template_role
        and tmp_template_roles(contains current templates_roles)
        """
        url = self.base_url + URL_TEMPLATE_ROLE
        for tmp_template_role in tmp_template_roles['result']:
            if tmp_template_role["role_name"] == template_role["role_name"]:
                service_id = str(tmp_template_role['id'])
                url = url + service_id
                modify = False
                modify_role = {}
                for key in ["description", "permission", "code_binary", "endpoint_rules",
                            "code_map", "path_binary", "path_params", "program_data_params"]:
                    if template_role[key] != tmp_template_role[key] or \
                            type(template_role[key]) != type(tmp_template_role[key]):
                        modify_role.update({key: template_role[key]})
                        modify = True
                if modify:
                    for key, value in modify_role.items():
                        if not value:
                            del modify_role[key]

                    response = requests.post(url, json=modify_role, headers=self.headers, verify=False)
                    if response.status_code == 200 or response.status_code == 201:
                        return True
                    else:
                        return False

    def add_template_roles(self, template_roles):
        url = self.base_url + URL_TEMPLATE_ROLE
        url_service = self.base_url + "api/v1/webpanel/servicetempl/" + str(
            template_roles["service_templ_id"]) + "/servicetemplrole"

        response = requests.get(url_service, verify=False, headers=self.headers)
        tmp_template_roles = json.loads(response.text)
        if not any(d['role_name'] == template_roles['role_name'] for d in tmp_template_roles['result']):
            response = requests.put(url, json=template_roles, headers=self.headers, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                raise ServiceTemplateRoleError()
        else:
            self.modify_service_template_role(template_roles, tmp_template_roles)

    def modify_service_template(self, service_template, tmp_templates):
        """
        Modification service template: accept service_template and tmp_templates(contains current templates)
        """
        url = self.base_url + URL_TEMPLATE
        for tmp_template in tmp_templates['result']:
            if tmp_template["service_name"] == service_template["service_name"]:
                service_id = str(tmp_template['id'])
                url = url + service_id
                modify = False
                for key in ["description"]:
                    if service_template[key] != tmp_template[key] or \
                            type(service_template[key]) != type(tmp_template[key]):
                        modify = True
                        break
                if modify:
                    response = requests.post(url, json=service_template,
                                             headers=self.headers, verify=False)
                    if response.status_code == 200 or response.status_code == 201:
                        return True
                    else:
                        return False
                else:
                    return False

    def add_service_template(self, service_template):
        url = self.base_url + URL_TEMPLATE
        url_domain = self.base_url + URL_DOMAIN
        response_domain = requests.get(url_domain, verify=False, headers=self.headers)
        dict_domain = json.loads(response_domain.text)
        filename = service_template["service_tepl_file"]
        template = self.read_from_json(filename)
        service_template.update({"service_name": template["serviceName"],
                                 "description": template["serviceDescription"],
                                 })
        del service_template["service_tepl_file"]
        for template_domain in service_template["domains"]:
            template_domain["id"] = self.get_domain_id(dict_domain['result'],
                                                       template_domain["domain_name"])
        tmp_result = requests.get(url, verify=False, headers=self.headers)
        tmp_templates = json.loads(tmp_result.text)
        template_id = ''
        if not any(tmp_template['service_name'] == service_template['service_name'] for tmp_template in
                   tmp_templates['result']):
            response = requests.put(url, json=service_template, headers=self.headers, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                d = json.loads(response.text)
                template_id = d['id']
            else:
                raise ServiceTemplateError()
        else:
            for tmp_template in tmp_templates['result']:
                if tmp_template['service_name'] == service_template['service_name']:
                    template_id = tmp_template['id']
        self.modify_service_template(service_template, tmp_templates)
        template_role = {}
        for role in template['roles']:
            template_role.update({
                "service_templ_id": template_id,
                "role_name": role.get("roleName", ""),
                "description": role.get("roleDescription", ""),
                "permission": role.get("permission", 0),
                "code_binary": role.get("code", ""),
                "code_map": role.get("codeMap", ""),
                "path_binary": role.get("path", ""),
                "path_params": role.get("pathParams", ""),
                "endpoint_rules": role.get("endpointRules", ""),
                "program_data_params": role.get("variables", "")
            })
            self.add_template_roles(template_role)

    def add_contracts_role(self, contract_role=None,
                           domain_name=None, domain_id=None, service_id=None):
        url = self.base_url + URL_CONTRACT_ROLE
        url_user = self.base_url + URL_USER
        url_service = "%sapi/v1/webpanel/servicetempl/%s/servicetemplrole" \
                      % (self.base_url, str(service_id))
        tmp_contract_role = contract_role.copy()
        result = requests.get(url, verify=False, headers=self.headers)
        tmp_roles = json.loads(result.text)
        if not any(d["role_name"] == contract_role["role_name"] and
                   d["topic_id"] == contract_role["topic_id"] for d in tmp_roles['result']):
            response_roles = requests.get(url_service, verify=False, headers=self.headers)
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
            result = requests.get(url_user, verify=False, headers=self.headers)
            domain_users = json.loads(result.text)
            for user in contract_role["users"]:
                for domain_user in domain_users["result"]:
                    if domain_user["username"] == user["user_name"] and domain_user["user_domain"] == domain_name:
                        user_id = domain_user["id"]
                        user["domain"].update({"domain_name": domain_name,
                                               "id": domain_id})
                        user.update({'domain_id': domain_id, 'id': user_id})

            response = requests.put(url, json=contract_role, headers=self.headers, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                raise ContractError()
        else:
            return False
        
    
    def modify_contract_role(self, contract_role_name=None, contract_name=None, domain_name=None, data=None):
        url = self.base_url + URL_CONTRACT_ROLE
        result = requests.get(url, verify=False, headers=self.headers)
        tmp_roles = json.loads(result.text)
        dict_domain = self.get_domain_list()
        #print(dict_domain)
        domain_id = self.get_domain_id(dict_domain['result'], domain_name)
        #print(domain_id)
        url_contracts = self.base_url + URL_CONTRACTS
        result = requests.get(url_contracts, verify=False, headers=self.headers)
        topics = json.loads(result.text)
        #print(json.loads(result.text))
        topic_id = ''
        for topic in topics['result']:
            if topic['name'] == contract_name and topic['domain_id'] == domain_id:
                topic_id = topic['id']
                break

        if not topic_id:
            message = "wrong modify contract_role - contract '%s' in domain '%s' does not exist" % (
                contract_name, domain_name)
            raise ContractError(error_message=message)
        #print(topic_id)
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
        #print(modify_url)
        
        modify_role.update(data)
        response = requests.post(modify_url, json=modify_role, verify=False, headers=self.headers)
        if response.status_code == 200 or response.status_code == 201:
            return True
        else:
            raise ContractError()
        

    def delete_contract_role(self, contract_role_name=None, contract_name=None, domain_name=None):
        url = self.base_url + URL_CONTRACT_ROLE
        result = requests.get(url, verify=False, headers=self.headers)
        tmp_roles = json.loads(result.text)
        dict_domain = self.get_domain_list()
        #print(dict_domain)
        domain_id = self.get_domain_id(dict_domain['result'], domain_name)
        #print(domain_id)
        url_contracts = self.base_url + URL_CONTRACTS
        result = requests.get(url_contracts, verify=False, headers=self.headers)
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
        response = requests.delete(delete_url, verify=False, headers=self.headers)
        if response.status_code == 200 or response.status_code == 201:
            return True
        else:
            raise ContractError()
    
    def get_all_contracts(self):
        url = self.base_url + URL_CONTRACTS
        result = requests.get(url, verify=False, headers=self.headers)
        all_contracts = json.loads(result.text)
        return all_contracts['result']

    def get_all_contracts_role(self):
        url = self.base_url + URL_CONTRACT_ROLE
        result = requests.get(url, verify=False, headers=self.headers)
        all_contracts_role = json.loads(result.text)
        return all_contracts_role['result']
    
    def get_contact_id(self, all_contracts, contract_name):
        contract_id = ''
        for contract in all_contracts:
            if contract['name'] == contract_name:
                contract_id = contract['id']
                break
        return contract_id

    def get_contracts_role_id(self, all_conract_role, contract_id, role_name):
        contract_role_id = ''
        for role in all_conract_role:
            if role['topic_id'] == contract_id and role['role_name'] == role_name:
                contract_role_id = role['id']
                break
        return contract_role_id

    def add_service(self, service):

        url = self.base_url + "api/v1/webpanel/service"
        all_contracts = self.get_all_contracts()
        all_contracts_role = self.get_all_contracts_role()
        dict_domain = self.get_domain_list()
        domain_name = service.get("domain_name")
        domain_id = self.get_domain_id(dict_domain['result'], domain_name)

        topic_role_id = []
        topics = service.get('topic_role')
        for topic in topics:
            topic_name = service.get('topic_name')
            contract_id = self.get_contact_id(all_contracts['result'], topic_name)

        
            


    def add_contracts(self, contract):
        dict_domain = self.get_domain_list()
        dict_service = self.get_service_list()
        contract_domain_id = ''

        for domain in dict_domain['result']:
            if domain['domain'] == contract['domain']:
                contract_domain_id = domain['id']
        domain_name = contract["domain"]
        contract_service_id = ''
        for service in dict_service['result']:
            if service['service_name'] == contract["serviceName"]:
                contract_service_id = service['id']

        contract.update({"domain_id": contract_domain_id,
                         "service_id": contract_service_id})
        contract_roles = contract["contract_roles"]

        del contract["contract_roles"]
        url = self.base_url + URL_CONTRACTS
        result = requests.get(url, verify=False, headers=self.headers)
        tmp = json.loads(result.text)
        contract_id = ""
        contract_add = False
        if not any((d['name'] == contract['name']) for d in tmp['result']):
            response = requests.put(url, json=contract, headers=self.headers, verify=False)
            resp = json.loads(response.text)
            if response.status_code == 200 or response.status_code == 201:
                contract_id = resp["id"]
                contract_add = True
            else:
                raise ContractRoleError()
        else:
            for d in tmp["result"]:
                if d["name"] == contract["name"]:
                    contract_id = d["id"]
        contract_role_cnt = 0
        for contract_role in contract_roles:
            contract_role['topic_id'] = contract_id
            if self.add_contracts_role(contract_role=contract_role,
                                       domain_name=domain_name, domain_id=contract_domain_id,
                                       service_id=contract_service_id):
                contract_role_cnt += 1
        return contract_add, contract_role_cnt

    def configured_link(self, link_json):
        url = self.base_url + URL_CONFIGURE_LINK
        result = requests.get(url, verify=False, headers=self.headers)
        tmp = json.loads(result.text)
        if not any(
                ((d["node_a"] == link_json["node_a"]) and (d["node_z"] == link_json["node_z"])) for d in tmp['result']):

            response = requests.put(url, json=link_json, headers=self.headers, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                raise ConfigureLinkError()
        else:
            return False

    def get_all_subnet(self):
        """GET all subnets from controller"""
        all_subnets = []
        url_zone = self.base_url + URL_ZONE
        result = requests.get(url_zone, verify=False, headers=self.headers)
        tmp_zone = json.loads(result.text)

        for zone in tmp_zone['result']:
            zone_id = str(zone['id'])
            url_managed_network = self.base_url + "api/v1/webpanel/subnet/" + zone_id + "/managed"
            result = requests.get(url_managed_network, verify=False, headers=self.headers)
            tmp_managed = json.loads(result.text)
            for subnet in tmp_managed['result']:
                all_subnets.append(subnet)
        return all_subnets

    def get_all_zones(self):
        """GET all zones from controller"""
        url_zones = self.base_url + URL_ZONE
        result = requests.get(url_zones, verify=False, headers=self.headers)
        all_zones = json.loads(result.text)
        return all_zones

    def add_missing_managed_network(self, zone_id, network):
        """ADD missing managed network into appropriate zone"""
        zone_url = self.base_url + "api/v1/webpanel/subnet/%s/managed?limit=1&offset=0" % zone_id
        result = requests.get(zone_url, headers=self.headers, verify=False)
        list_zone_settings = json.loads(result.text)
        list_zone_settings = list_zone_settings['result']
        del list_zone_settings[0]['id']
        del list_zone_settings[0]['tunnel_switch_domain']
        list_zone_settings[0]['network_prefix'] = network
        managed_network_json = list_zone_settings[0]
        add_managed_network_url = self.base_url + "api/v1/webpanel/subnet/%s/managed" % zone_id
        requests.put(add_managed_network_url,
                     json=managed_network_json,
                     headers=self.headers, verify=False)
        return True
