import json
from ib_orchestrator_api.core.core import Core
from ib_orchestrator_api.core.utils import *
from ib_orchestrator_api.modules import Service

class ServiceToken(Core):
    def __init__(self, url, session, service_name, domain_name, expire_date):
        self.url = url
        self.session = session
        self.service_name = service_name
        self.domain_name = domain_name
        self.expire_data = expire_date







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