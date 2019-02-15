import json
from ib_orchestrator_api.core.core import Core
from ib_orchestrator_api.core.utils import *
from ib_orchestrator_api.modules import Domain
from ib_orchestrator_api.core.errors import ServiceError


class Service(Core):
    def __init__(self, url, session, id=None, topic_roles=None, description=None, name=None,
                 enable=None, domain_name=None, domain_id=None):
        self.url = url
        self.session = session
        self.id = id
        self.topic_roles = topic_roles
        self.description = description
        self.name = name
        self.enable = enable
        self.domain_name = domain_name
        if not domain_id:
            self.domain_id = self.__domain_id(domain_name)
        else:
            self.domain_id = domain_id

    def _get_service_url(self):
        return self.url + URL_SERVICE

    def __domain_id(self, domain_name):
        if not domain_name:
            return None
        else:
            return Domain(url=self.url, session=self.session).get_domain_id(domain_name)

    def get_service_id(self, service_name, domain_name):
        url = self._get_service_url()
        payload = {'name': service_name, 'domain.domain_name': domain_name}
        result = self.session.get(url, params=payload, verify=False)
        response = json.loads(result.text)
        if not response['result']:
            raise ServiceError()
        else:
            service_id = response['result'][0].get('id')
            return service_id

    def get_all_service(self):
        url = self._get_service_url()
        result = self.session.get(url, verify=False)
        all_service = json.loads(result.text)
        return all_service

    """
    def add_service(self, service):

        url = self._get_service_url()
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
        if not any(s["name"] == service["name"] for s in all_service):
            print(service)
            response = self.session.put(url, json=service, verify=False)
            print(response)
            print(response.text)
        else:
            print("service already create")


    """


"""
Example
    topic_roles: [
                     {"topic_name":"frontend", "topic_role_name":"client"}
                 ]
    description: "frontend-client"
    name : "client"
    enable: true
    domain_name: "getaway-app"
    domain_id: ""
"""
