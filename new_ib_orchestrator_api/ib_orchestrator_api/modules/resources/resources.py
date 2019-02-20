import json
from ib_orchestrator_api.core import Core
from ib_orchestrator_api.core.utils import URL_RESOURCES

class Resources(Core):
    def __init__(self, url, session):
        self.url = url
        self.session = session

    def _get_resources_url(self):
        return self.url + URL_RESOURCES

    def get_all_resources(self):
        url = self._get_resources_url()
        response = self.session.get(url, verify=False)
        result = json.loads(response.text)
        response_data = {'count_all': result.get('count_all')}
        resources = []
        for resource in result['result']:
            tmp_res = {'name': resource.get('name'),
                       'status': resource.get('status').get('name'),
                       'domain': resource.get('domain').get('domain_name')}
            resources.append(tmp_res)
        response_data.update({'resources': resources})
        return response_data

    def get_rescources(self, name, domain):
        url = self._get_resources_url()
        payload = {'name':name, 'domain.domain_name':domain}
        response = self.session.get(url, params=payload, verify=False)
        result = json.loads(response.text)
        return result
