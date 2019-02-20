import json
from ib_orchestrator_api.core.core import Core
from ib_orchestrator_api.core.errors import ContractError
from ib_orchestrator_api.core.utils import *
from ib_orchestrator_api.modules.template import Template
from ib_orchestrator_api.modules import Domain


class Contract(Core):
    def __init__(self, url, session, id=None, name=None, domain=None, domain_id=None, description=None, enable=None,
                 service=None, service_id=None):
        self.url = url
        self.session = session
        self._id = id
        self.name = name
        self.domain = domain
        self.description = description
        self.enable = enable
        self.service = service
        if not service_id:
            self.service_id = self.__get_service_id(service)
        else:
            self.service_id = service_id
        if not domain_id:
            self.domain_id = self.__get_domain_id(domain)
        else:
            self.domain_id = domain_id


    def __get_service_id(self, service):
        """"SERVICE IS TEMPLATE(TOPIC)"""
        if not service:
            return None
        else:
            return Template(url=self.url, session=self.session).get_template_id(service)

    def __get_domain_id(self, domain):
        if not domain:
            return None
        else:
            if isinstance(domain, Domain):
                return Domain.id
            else:
                return Domain(url=self.url, session=self.session).get_domain_id(domain)

    def __make_json(self):
        data = self.to_dict()
        if "id" in data.keys():
            del data['id']
        for key, value in data.items():
            if value is None or value == '':
                message = "Field '%s' can't be None" % str(key)
                # print(message)
                # print(str(key), value)
                raise ContractError(error_message=message)
        return data

    def _get_contract_url(self):
        return self.url + URL_CONTRACTS

    def get_contract(self, contract_name, domain_name):
        url = self._get_contract_url()
        payload = {'name': contract_name, 'domain.domain_name': domain_name}
        result = self.session.get(url, params=payload, verify=False)
        response = json.loads(result.text)
        print(response)
        if response['count_all'] == 0:
            raise ContractError()

        tmp_contact = response['result'][0]
        contract = Contract(url=self.url, session=self.session)
        for field in tmp_contact.keys():
            if field == 'id':
                setattr(contract, 'id', tmp_contact[field])
            if field in vars(contract).keys():
                setattr(contract, field, tmp_contact[field])
        return contract

    def get_all_contracts(self):
        url = self._get_contract_url()
        result = self.session.get(url, verify=False)
        all_contracts = json.loads(result.text)
        return all_contracts

    def get_all_contacts_in_domain(self, domain_name):
        url = self._get_contract_url()
        payload = {'domain.domain_name': domain_name}
        result = self.session.get(url, params=payload, verify=False)
        response = json.loads(result.text)
        return response

    def get_contract_id(self, contract_name, domain_name):
        url = self._get_contract_url()
        payload = {'name': contract_name, 'domain.domain_name': domain_name}
        result = self.session.get(url, params=payload, verify=False)
        response = json.loads(result.text)
        if not response['result']:
            raise ContractError()
        else:
            return response['result'][0].get('id')

    def create_contract(self):
        url = self._get_contract_url()
        contract = self.__make_json()
        tmp = self.get_all_contracts()
        if not any((d['name'] == contract['name']) for d in tmp['result']):
            response = self.session.put(url, json=contract, verify=False)
            print(response)
            if response.status_code == 200 or response.status_code == 201:
                self.id = (json.loads(response.text)).get('id')
                return response.text
            else:
                raise ContractError()

    def update_contract(self):
        pass

    def delete_contract(self, contract_name, domain_name):
        contract_id = self.get_contract_id(contract_name, domain_name)
        url = self._get_contract_url() + "/" + str(contract_id)
        response = self.session.delete(url, verify=False)
        print(response)
        print(response.text)


"""
EXAMPLE

{'domain': 'voting-app', 
'domain_id': 3, 
'description': 'Dispatch user result requests', 
'enable': True, 
'name': 'result-frontend', 
'serviceName': 'client-server', 
'service_id': 1}


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
"""
