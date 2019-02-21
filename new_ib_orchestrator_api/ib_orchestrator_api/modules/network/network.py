import json
from ib_orchestrator_api.core.core import Core
from ib_orchestrator_api.core.errors import ZoneError, SubnetError
from ib_orchestrator_api.core.utils import *
from ib_orchestrator_api.modules.zone import Zone


class Network(Core):
    def __init__(self, url, session, id=None, network_prefix=None, zone=None):
        self.id = id
        self.url = url
        self.session = session
        self.network_prefix = network_prefix
        self.zone = self._get_subnet(zone)
        self.subnet_id = self._get_subnet_id()

    def _get_subnet_url(self):
        """Internal class method: return url which is used for get, create, update, delete network,
        used attribute id Zone, as part of the url. 
        """
        return self.url + URL_ZONE + '/' + str(self.subnet_id) + "/managed"

    def to_dict(self):
        """Base class override method. Representation of class attributes as dict"""
        data = (vars(self)).copy()
        if 'url' in data.keys():
            del data['url']
        if 'session' in data.keys():
            del data['session']

        for key, value in data.items():
            if isinstance(getattr(self, key), Core):
                data.update({key: value.to_dict()})
        return data

    def _make_json(self):
        """
        Example JSON
        {'network_prefix': '54.241.0.0/16', 'subnet_id': '25'}
        """
        data = self.to_dict()
        if "id" in data.keys():
            del data['id']

        # del data['tunnel_switch_domain']
        # del data['tunnel_switch']

        for key, value in data.items():
            if key == 'tunnel_switch_id' or key == 'tunnel_switch_iface':
                continue
            # if value is None or value == '':
            # message = "Field '%s' can't be None" % str(key)
            # raise ZoneError(error_message=message)
        return data

    def _get_subnet(self, zone):
        if not zone:
            return None
        else:
            if not isinstance(zone, Zone):
                return Zone(url=self.url, session=self.session).get_zone(zone)
            else:
                return zone

    def _get_subnet_id(self):
        if self.zone:
            return self.zone.id
        else:
            return None

    def get_all_subnets(self):
        """GET all subnets from controller"""
        all_subnets = []
        all_zones = Zone(url=self.url, session=self.session).get_all_zones()
        for zone in all_zones['result']:
            zone_id = zone['id']
            url_managed_network = self.url + "api/v1/webpanel/network/" + str(zone_id) + "/managed"
            result = self.session.get(url_managed_network, verify=False)
            tmp_managed = json.loads(result.text)
            for subnet in tmp_managed['result']:
                all_subnets.append(subnet)
        return all_subnets

    def get_all_subnets_in_zone(self, zone_name):
        """Get all subnets, for zone"""
        zone_id = Zone(url=self.url, session=self.session).get_zone_id(zone_name)
        url_managed_network = self.url + "api/v1/webpanel/network/" + str(zone_id) + "/managed"
        result = self.session.get(url_managed_network, verify=False)
        tmp_managed = json.loads(result.text)
        return tmp_managed

    def get_subnet_in_zone(self, zone_name):
        """Get subnets in zone, filtering sunbets by input parametrs"""
        zone_id = Zone(url=self.url, session=self.session).get_zone_id(zone_name)
        url_managed_network = self.url + "api/v1/webpanel/network/" + str(zone_id) + "/managed"
        result = self.session.get(url_managed_network, verify=False)
        tmp_managed = json.loads(result.text)
        return tmp_managed

    def create_subnet(self):
        subnet_json = self._make_json()
        url = self._get_subnet_url()

        response = self.session.put(url, json=subnet_json, verify=False)
        if response.status_code == 200 or response.status_code == 201:
            self.id = (json.loads(response.text)).get('id')
            # print(self.id)
            return True
        else:
            message = response.text
            raise SubnetError(error_message=message)

    def update_subnet(self):

        if not self.id:
            print("network not created")
            raise SubnetError()
        subnet_json = self._make_json()
        url = self._get_subnet_url() + "/" + str(self.id)
        response = self.session.patch(url, json=subnet_json, verify=False)
        if response.status_code == 200 or response.status_code == 201:
            print(response)
            print(response.text)
            # self.id = (json.loads(response.text)).get('id')
            # print(self.id)
            return True
        else:
            message = "Error add network "
            raise SubnetError(error_message=message)

    def delete_subnet(self, zone_name, network_prefix):
        subnet = self.get_all_subnets_in_zone(zone_name)
        delete_url = self.url + URL_ZONE + '/' + str(self.subnet_id) + "/managed" + "/" + str(managed_id)

        print(delete_url)

        response = self.session.delete(delete_url, verify=False)
        print(response)
        print(response.text)
