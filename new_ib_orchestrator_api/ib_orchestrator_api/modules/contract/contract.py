import json
from ib_orchestrator_api.core.core import Core
from ib_orchestrator_api.core.errors import ContractError
from ib_orchestrator_api.core.utils import *
from ib_orchestrator_api.modules.template import Template
from ib_orchestrator_api.modules import Domain


class Contract(Core):
    def __init__(self, url, session, id=None, domain=None, domain_id=None, description=None, enable=None,
                 serviceName=None, service_id=None):
        self.url = url
        self.session = session
        self.id = id
        self.domain = domain
        self.domain_id = domain_id
        self.description = description
        self.enabled = enable
        self.serviceName = serviceName
        if not service_id:
            service_id = self.__get_service_id(serviceName)
        self.service_id = service_id

    def __get_service_id(self, serviceName):
        """"SERVICE IS TEMPLATE(TOPIC)"""
        if not serviceName:
            return None
        else:
            return Template(url=self.url, session=self.session).get_template_id(serviceName)

    def __get_domain_id(self, domain):
        if not domain:
            return None
        else:
            if isinstance(domain, Domain):
                return Domain.id
            else:
                return Domain(url=self.url, session=self.session).get_domain_id(domain)


    def _get_contract_url(self):
        return self.url + URL_CONTRACTS

    def get_all_contracts(self):
        url = self.base_url + URL_CONTRACTS
        result = self.session.get(url, verify=False)
        all_contracts = json.loads(result.text)
        return all_contracts['result']

    def get_contract_id(self, contract_name):
        url = self._get_contract_url()
        payload = {'name':contract_name}
        result = self.session.get(url, params=payload, verify=False)
        response = json.loads(result.text)
        if not response['result']:
            raise ContractError()
        else:
            return response['result'][0].get('id')




"""
EXAMPLE

{'domain': 'voting-app', 
'domain_id': 3, 
'description': 'Dispatch user result requests', 
'enable': True, 
'name': 'result-frontend', 
'serviceName': 'client-server', 
'service_id': 1}



def get_all_contracts(self):
    url = self.base_url + URL_CONTRACTS
    result = self.session.get(url, verify=False)
    all_contracts = json.loads(result.text)
    return all_contracts['result']


def get_contract_id(self, all_contracts, contract_name):
    contract_id = ''
    for contract in all_contracts:
        if contract['name'] == contract_name:
            contract_id = contract['id']
            break
    return contract_id


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
