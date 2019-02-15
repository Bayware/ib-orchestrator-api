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
from .utils import *

try:
    from ib_orchestrator_api.modules import *  # for Python 3
except ImportError:
    from ..modules import *  # for Python 2

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

warnings.filterwarnings('ignore')


# logging.basicConfig(filename='example.log', level=logging.DEBUG)


class IBOrchestratorAPI(Core):
    def __init__(self, hostname, login, password, base_url, domain='default'):
        self.hostname = hostname
        self.domain_server = domain
        self.login = login
        self.password = password
        self.base_url = base_url
        self.headers = {'Content-Type': 'application/json'}
        self.ip_address = self.get_ip_address(hostname)
        self.session = None

    def domain(self, **kwargs):
        domain = Domain(url=self.base_url, session=self.session, **kwargs)
        return domain

    def controller(self, **kwargs):
        controller = Controller(url=self.base_url, session=self.session, **kwargs)
        return controller

    def user(self, **kwargs):
        user = User(url=self.base_url, session=self.session, **kwargs)
        return user

    def resource_user(self, **kwargs):
        resource_user = ResourceUser(url=self.base_url, session=self.session, **kwargs)
        return resource_user

    def resource_role(self, **kwargs):
        resource_role = ResourceRole(url=self.base_url, session=self.session, **kwargs)
        return resource_role

    def zone(self, **kwargs):
        zone = Zone(url=self.base_url, session=self.session, **kwargs)
        return zone

    def subnet(self, **kwargs):
        subnet = Subnet(url=self.base_url, session=self.session, **kwargs)
        return subnet

    def template(self, **kwargs):
        template = Template(url=self.base_url, session=self.session, **kwargs)
        return template

    def service(self, **kwargs):
        service = Service(url=self.base_url, session=self.session, **kwargs)
        return service

    def contract(self, **kwargs):
        contract = Contract(url=self.base_url, session=self.session, **kwargs)
        return contract

    def contract_role(self, **kwargs):
        contract_role = ContractRole(url=self.base_url, session=self.session, **kwargs)
        return contract_role

    def link(self, **kwargs):
        link = Link(url=self.base_url, session=self.session, **kwargs)
        return link


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
        result = self.session.get(url_domain, verify=False)
        domain_list = json.loads(result.text)
        return domain_list

    def get_service_list(self):
        url_service = self.base_url + URL_TEMPLATE
        result = self.session.get(url_service, verify=False)
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

    def old_authorization(self):
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

    def authorization(self):
        session = requests.session()
        token_url = self.base_url + "api/v1/webpanel/token"
        response = session.post(
            token_url,
            json={'domain': self.domain_server, 'username': self.login, 'password': self.password},
            verify=False)
        if response.status_code == 200 or response.status_code == 201:
            tmp_token = json.loads(response.text)
            token = "Bearer " + tmp_token.get("token")
            self.headers.update({"Authorization": token})
            session.headers.update({"Authorization": token,
                                    'Content-Type': 'application/json'})
            self.session = session
        else:
            print(response)
            print(response.text)
            raise LoginError()

    def add_domain(self, domain_json):
        url_domain = self.base_url + URL_DOMAIN
        result = self.session.get(url_domain, verify=False)
        tmp_domain = json.loads(result.text)
        if not any(d['domain'] == domain_json['domain'] for d in tmp_domain['result']):
            response = self.session.post(url_domain, json=domain_json, verify=False)

            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                message = "Error add domain: " + domain_json['domain']
                raise DomainError(error_message=message)
        else:
            return False

    def add_user(self, user_json):
        url_user = self.base_url + URL_USER
        result = self.session.get(url_user, verify=False)
        tmp_users = json.loads(result.text)
        if not any((d['username'] == user_json['username'] and
                    d['user_domain'] == user_json['user_domain']) for d in tmp_users['result']):
            response = self.session.post(url_user, json=user_json, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                message = "Error add user '%s' in domain '%s' " % (user_json['username'], user_json['user_domain'])
                raise UserError(error_message=message)
        else:
            return False

    def add_resource_user(self, resource_user_json):
        url_resource_user = self.base_url + URL_RESOURCE_USER
        result = self.session.get(url_resource_user, verify=False)
        tmp_users = json.loads(result.text)
        url_resource_role = self.base_url + URL_RESOURCE_ROLE
        result = self.session.get(url_resource_role, verify=False)
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
            response = self.session.put(url_resource_user, json=resource_user_json, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                message = "Error add  resource_user '%s' " % (resource_user_json['username'])
                raise UserError(error_message=message)
        else:
            return False

    def patch_resource_user(self, resource_user_json):
        url_resource_user = self.base_url + URL_RESOURCE_USER
        # print(url_resource_user)
        result = self.session.get(url_resource_user, verify=False)
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

    def add_zone(self, zone_json):
        url = self.base_url + URL_CONTROLLER
        controller_result = self.session.get(url, verify=False)
        tmp_controllers = json.loads(controller_result.text)
        controller_pri_id = ""
        controller_sec_id = ""
        for controller in tmp_controllers['result']:
            if controller['name'] == zone_json["controller_pri_id"]:
                controller_pri_id = str(controller['id'])
            if controller['name'] == zone_json["controller_sec_id"]:
                controller_sec_id = str(controller['id'])

        domain_name = zone_json.get("tunnel_switch_domain_id")
        all_domains = self.get_domain_list()
        domain_id = self.get_domain_id(all_domains['result'], domain_name)

        zone_json.update({"controller_pri_id": controller_pri_id,
                          "controller_sec_id": controller_sec_id,
                          "tunnel_switch_domain_id": domain_id})
        url_zone = self.base_url + "api/v1/webpanel/subnet"
        result = self.session.get(url_zone, verify=False)
        tmp_zone = json.loads(result.text)
        if not any(d['name'] == zone_json['name'] for d in tmp_zone['result']):
            response = self.session.put(url_zone, json=zone_json, verify=False)
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
                result = self.session.get(url_zone, verify=False)
                tmp_zone = json.loads(result.text)
                for subnet in tmp_zone['result']:
                    if subnet['name'] == zone:
                        zone_id = str(subnet['id'])
                    else:
                        return "you input invalid zone"

        url = self.base_url + "api/v1/webpanel/subnet/" + zone_id + "/managed"
        managed_network.update({"subnet_id": int(zone_id)})
        result = self.session.get(url, verify=False)
        tmp_managed = json.loads(result.text)
        #print(managed_network)
        if 'network_files' in managed_network.keys():
            del managed_network['network_files']
        #print(managed_network)
        #response = self.session.put(url, json=managed_network, verify=False)
        # print(managed_network)

        #if response.status_code == 200 or response.status_code == 201:
            #return True
       # else:
            #raise ManagedNetworkError()

        if not any(d["network_prefix"] == managed_network["network_prefix"] for d in tmp_managed['result']):
            response = self.session.put(url, json=managed_network, verify=False)
            # print(managed_network)
            # print(response)
            #print(response.text)
            if response.status_code == 200 or response.status_code == 201:

                return True
            else:
                raise ManagedNetworkError()
        else:
            return False


    def add_zone_managed_network(self, managed_network):
        url_subnet = self.base_url + URL_ZONE
        response_subnet = self.session.get(url_subnet, verify=False)

        dict_domain = self.get_domain_list()
        # domain_id = ""
        # for domain in dict_domain['result']:
        # if domain['domain'] == managed_network["tunnel_switch_domain_id"]:
        # domain_id = str(domain['id'])

        # if domain_id == "":
        # return DomainIDError()

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
                # network["tunnel_switch_domain_id"] = domain_id
                if self.add_managed_network(managed_network=network, zone_id=zone_id):
                    cnt += 1

        if "network_files" in managed_network:
            for network_file in managed_network["network_files"]:
                tmp_network = self.read_from_json(network_file)
                for prefix in tmp_network["networks"]:
                    network = managed_network
                    network["subnet_id"] = zone_id
                    network["network_prefix"] = prefix
                    # network["tunnel_switch_domain_id"] = domain_id
                    if self.add_managed_network(managed_network=network, zone_id=zone_id):
                        cnt += 1

        return cnt

    def add_controller(self, controller_json):
        controller_json.update({"host_fqdn": self.hostname,
                                "ip_management": self.ip_address})

        url = self.base_url + URL_CONTROLLER

        result = self.session.get(url, verify=False)
        tmp_controllers = json.loads(result.text)
        if not any(d['name'] == controller_json['name'] for d in tmp_controllers['result']):
            response = self.session.put(url, json=controller_json, verify=False)
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
        result = self.session.get(url, params=data, verify=False)
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

                    response = self.session.post(url, json=modify_role, verify=False)
                    if response.status_code == 200 or response.status_code == 201:
                        return True
                    else:
                        return False

    def add_template_roles(self, template_roles):
        url = self.base_url + URL_TEMPLATE_ROLE
        url_service = self.base_url + "api/v1/webpanel/servicetempl/" + str(
            template_roles["service_templ_id"]) + "/servicetemplrole"

        response = self.session.get(url_service, verify=False)
        tmp_template_roles = json.loads(response.text)
        if not any(d['role_name'] == template_roles['role_name'] for d in tmp_template_roles['result']):
            response = self.session.put(url, json=template_roles, verify=False)
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
                    response = self.session.post(url, json=service_template, verify=False)
                    if response.status_code == 200 or response.status_code == 201:
                        return True
                    else:
                        return False
                else:
                    return False

    def add_service_template(self, service_template):
        url = self.base_url + URL_TEMPLATE
        url_domain = self.base_url + URL_DOMAIN
        response_domain = self.session.get(url_domain, verify=False)
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
        tmp_result = self.session.get(url, verify=False)
        tmp_templates = json.loads(tmp_result.text)
        template_id = ''
        if not any(tmp_template['service_name'] == service_template['service_name'] for tmp_template in
                   tmp_templates['result']):
            response = self.session.put(url, json=service_template, verify=False)
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

    def get_all_contracts(self):
        url = self.base_url + URL_CONTRACTS
        result = self.session.get(url, verify=False)
        all_contracts = json.loads(result.text)
        return all_contracts['result']

    def get_all_contracts_role(self):
        url = self.base_url + URL_CONTRACT_ROLE
        result = self.session.get(url, verify=False)
        all_contracts_role = json.loads(result.text)
        return all_contracts_role['result']

    def get_contract_id(self, all_contracts, contract_name):
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

    def get_all_service(self):
        url = self.base_url + "api/v1/webpanel/service"
        result = self.session.get(url, verify=False)
        all_service = json.loads(result.text)
        return all_service['result']

    def add_service(self, service):

        url = self.base_url + "api/v1/webpanel/service"
        all_contracts = self.get_all_contracts()
        # print(all_contracts)
        all_contracts_role = self.get_all_contracts_role()
        dict_domain = self.get_domain_list()
        domain_name = service.get("domain_name")
        domain_id = self.get_domain_id(dict_domain['result'], domain_name)
        # print("DOMAIN ID: ", domain_id)

        topic_role_id = []
        topics = service.get("topic_roles")
        for topic in topics:
            topic_name = topic.get('topic_name')
            contract_id = self.get_contract_id(all_contracts, topic_name)
            # print(contract_id)
            topic_role_name = topic.get('topic_role_name')
            contract_role_id = self.get_contracts_role_id(all_contracts_role, contract_id, topic_role_name)
            topic_role_id.append(int(contract_role_id))

        del service["domain_name"]
        service.update({"topic_roles": topic_role_id,
                        "domain_id": domain_id})

        all_service = self.get_all_service()

        print("SERVICE")
        print(service)
        if not any(s["name"] == service["name"] for s in all_service):
            print(service)
            response = self.session.put(url, json=service, verify=False)
            print(response)
            print(response.text)
        else:
            print("service already create")


    def get_all_service_token(self, service_id=None):
        url = self.base_url + "api/v1/webpanel/service/" + str(service_id) + "/token"
        result = self.session.get(url, verify=False)
        # print(result)
        all_service_token = json.loads(result.text)
        # print(all_service_token)
        return all_service_token['result']

    def add_service_token(self, service_token):
        all_service = self.get_all_service()
        dict_domain = self.get_domain_list()
        domain_name = service_token.get("domain_name")
        domain_id = self.get_domain_id(dict_domain['result'], domain_name)

        service_id = ''
        for service in all_service:
            if service['domain_id'] == domain_id and service['name'] == service_token["service_name"]:
                service_id = service['id']
                break
        service_token.update({"service_id": service_id})
        del service_token['service_name']
        del service_token['domain_name']
        del service_token['service_id']
        print(service_token)
        url = self.base_url + "api/v1/webpanel/service/" + str(service_id) + "/token"
        # print(url)
        all_service_token = self.get_all_service_token(service_id)

        # url = self.base_url + "api/v1/webpanel/token"
        # response = self.session.put(url, json=service_token, verify=False)
        # print(response)
        # print(response.text)
        print("SERVICE_TOKEN")
        print(service_token)
        if not any(t["token_ident"] == service_token["token_ident"] for t in all_service_token):
            response = self.session.put(url, json=service_token, verify=False)
            print(response)
            print(response.text)
        else:
            print("token already create")

    def delete_service_token(self, service_id, token_id):
        url = "https://dev.bayware.net/api/v1/webpanel/service/" + str(service_id) + "/token/" + str(token_id)
        response = self.session.delete(url, verify=False)
        print(response)
        print(response.text)

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
        result = self.session.get(url, verify=False)
        tmp = json.loads(result.text)
        contract_id = ""
        contract_add = False
        if not any((d['name'] == contract['name']) for d in tmp['result']):
            response = self.session.put(url, json=contract, verify=False)
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
        result = self.session.get(url, verify=False)
        tmp = json.loads(result.text)
        if not any(
                ((d["node_a"] == link_json["node_a"]) and (d["node_z"] == link_json["node_z"])) for d in tmp['result']):

            response = self.session.put(url, json=link_json, verify=False)
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
        result = self.session.get(url_zone, verify=False)
        tmp_zone = json.loads(result.text)

        for zone in tmp_zone['result']:
            zone_id = str(zone['id'])
            url_managed_network = self.base_url + "api/v1/webpanel/subnet/" + zone_id + "/managed"
            result = self.session.get(url_managed_network, verify=False)
            tmp_managed = json.loads(result.text)
            for subnet in tmp_managed['result']:
                all_subnets.append(subnet)
        return all_subnets

    def get_all_zones(self):
        """GET all zones from controller"""
        url_zones = self.base_url + URL_ZONE
        result = self.session.get(url_zones, verify=False)
        all_zones = json.loads(result.text)
        return all_zones

    def add_missing_managed_network(self, zone_id, network):
        """ADD missing managed network into appropriate zone"""
        zone_url = self.base_url + "api/v1/webpanel/subnet/%s/managed?limit=1&offset=0" % zone_id
        result = self.session.get(zone_url, verify=False)
        list_zone_settings = json.loads(result.text)
        list_zone_settings = list_zone_settings['result']
        del list_zone_settings[0]['id']
        del list_zone_settings[0]['tunnel_switch_domain']
        list_zone_settings[0]['network_prefix'] = network
        managed_network_json = list_zone_settings[0]
        add_managed_network_url = self.base_url + "api/v1/webpanel/subnet/%s/managed" % zone_id
        self.session.put(add_managed_network_url,
                         json=managed_network_json, verify=False)
        return True
