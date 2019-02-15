import json
from ib_orchestrator_api.core.core import Core
from ib_orchestrator_api.core.utils import URL_CONFIGURE_LINK
from ib_orchestrator_api.core.errors import ConfigureLinkError
from ib_orchestrator_api.modules import Domain


class Link(Core):
    def __init__(self, url, session, id=None, node_a=None, node_z=None, domain_a=None, domain_id_a=None,
                 domain_z=None, domain_id_z=None, admin_status=None, ipsec_enable=None, tunnel_ip_type=None):
        self.url = url
        self.session = session
        self.id = id
        self.node_a = node_a
        self.node_z = node_z
        self.domain_a = domain_a
        self.domain_z = domain_z
        self.admin_status = admin_status
        self.ipsec_enable = ipsec_enable
        self.tunnel_ip_type = tunnel_ip_type
        if not domain_id_a:
            self.domain_id_a = self._get_domain_id(domain_a)
        else:
            self.domain_id_a = domain_id_a
        if not domain_id_z:
            self.domain_id_z = self._get_domain_id(domain_z)
        else:
            self.domain_id_z = domain_id_z

    def _get_link_url(self):
        return self.url + URL_CONFIGURE_LINK

    def _get_domain_id(self, domain):
        if not domain:
            return None
        else:
            if isinstance(domain, Domain):
                return domain.id
            else:
                return Domain(url=self.url, session=self.session).get_domain_id(domain)

    def get_all_links(self):
        url = self._get_link_url()
        result = self.session.get(url, verify=False)
        response = json.loads(result.text)
        return response

    def configured_link(self, link_json):
        url = self._get_link_url()
        all_links = self.get_all_links()
        if not any(((d["node_a"] == link_json["node_a"])
                    and (d["node_z"] == link_json["node_z"])) for d in all_links['result']):

            response = self.session.put(url, json=link_json, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                return response.text
            else:
                raise ConfigureLinkError()
        else:
            return False
