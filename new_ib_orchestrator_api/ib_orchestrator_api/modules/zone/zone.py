import json
from ib_orchestrator_api.core.core import Core
from ib_orchestrator_api.core.errors import ZoneError
from ib_orchestrator_api.core.utils import *
from ib_orchestrator_api.modules.controller import Controller
from ib_orchestrator_api.modules.domain import Domain


class Zone(Core):
    def __init__(self, url, session, name=None, cga_prefix=None, controller_pri=None, controller_sec=None,
                 description=None, ipsec_enable=None, tunnel_switch_name=None, tunnel_switch=None,
                 tunnel_switch_id=None, tunnel_switch_domain_id=None, tunnel_switch_domain=None, tunnel_ip_type=None):
        self.id = None
        self.url = url
        self.session = session
        self.name = name
        self.cga_prefix = cga_prefix
        self.description = description
        self.ipsec_enable = ipsec_enable
        self.tunnel_switch_name = tunnel_switch_name
        self.tunnel_switch = tunnel_switch
        self.tunnel_switch_id = tunnel_switch_id
        self.tunnel_ip_type = tunnel_ip_type
        self.tunnel_switch_domain = self._get_tunnel_switch_domain(tunnel_switch_domain)
        self.tunnel_switch_domain_id = self._get_tunnel_switch_domain_id(tunnel_switch_domain_id)
        self.controller_pri = self._get_controller(controller_pri)
        self.controller_sec = self._get_controller(controller_sec)
        if not self.controller_pri:
            self.controller_pri_id = ""
        else:
            self.controller_pri_id = self.controller_pri.id
        if not self.controller_sec:
            self.controller_sec_id = ""
        else:
            self.controller_sec_id = self.controller_sec.id

    def _get_zone_url(self):
        """Internal class method: return url which is used for get, create, update, delete zone"""
        return self.url + URL_ZONE

    def _get_controller(self, controller):
        if not controller:
            return None
        else:
            if not isinstance(controller, Controller):
                controller = Controller(url=self.url, session=self.session).get_contrroler(controller)
                return controller
            else:
                return controller

    def _get_dict_zone(self, name=None):
        if not name:
            name = self.name
        all_zones = self.get_all_zones()
        result_zone = ''
        for zone in all_zones['result']:
            if zone['name'] == name:
                result_zone = zone
                break
        return result_zone

    def _get_tunnel_switch_domain(self, tunnel_switch_domain):
        if not tunnel_switch_domain:
            return None
        else:
            if not isinstance(tunnel_switch_domain, Domain):
                return Domain(url=self.url, session=self.session).get_domain(tunnel_switch_domain)
            else:
                return tunnel_switch_domain

    def _get_tunnel_switch_domain_id(self, tunnel_switch_domain_id):
        if not tunnel_switch_domain_id:
            if not self.tunnel_switch_domain:
                return None
            else:
                # print(self.tunnel_switch_domain)
                return self.tunnel_switch_domain.id
        else:
            if isinstance(tunnel_switch_domain_id, int):
                return tunnel_switch_domain_id
            if tunnel_switch_domain_id.isnumeric():
                return int(tunnel_switch_domain_id)
            else:
                # print(tunnel_switch_domain_id)
                # print(type(tunnel_switch_domain_id))
                message = "Wrong Value tunnel_switch_domain_id"
                raise ZoneError(error_message=message)

    def _check_self_zone(self):
        """Internal class method, checks if such an zone exists on the server"""
        result_zone = self._get_dict_zone()
        if not result_zone:
            return False
        else:
            self.id = result_zone.get('id')
            return True

    def _make_json(self):
        """
        Example JSON
        {
            'cga_prefix': 'fd32:10d7:b78f:9fc6', 
            'controller_pri_id': '1', 
            'controller_sec_id': '', 
            'description': 'AWS Zone us-west-1', 
            'name': 'AWS Zone-1'
        }
        """
        data = self.to_dict()
        if "id" in data.keys():
            del data['id']
        # for key, value in data.items():
        # if key == 'controller_sec_id' or key == 'controller_sec':
        # continue
        # if value is None or value == '':
        # message = "Field '%s' can't be None" % str(key)
        # raise ZoneError(error_message=message)
        del data['controller_pri']
        del data['controller_sec']
        return data

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

    def get_zone(self, name=None):
        if not name:
            name = self.name
        result_zone = self._get_dict_zone(name)
        if not result_zone:
            message = "Zone not found"
            raise ZoneError(error_message=message)

        zone = Zone(url=self.url, session=self.session)
        for field in result_zone.keys():
            if field == 'id':
                setattr(zone, 'id', result_zone[field])
            if field in vars(zone).keys():
                setattr(zone, field, result_zone[field])
        return zone

    def get_all_zones(self):
        url = self._get_zone_url()
        print(url)
        result = self.session.get(url, verify=False)
        print(result)
        all_zone = json.loads(result.text)
        return all_zone

    def get_zone_id(self, name):
        result_zone = self._get_dict_zone(name)
        if not result_zone:
            message = "Zone not found"
            raise ZoneError(error_message=message)
        else:
            return result_zone.get('id')

    def create_zone(self):
        url = self._get_zone_url()
        if not self._check_self_zone():
            zone_json = self._make_json()
            response = self.session.put(url, json=zone_json, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                self.id = (json.loads(response.text)).get('id')
                return True
            else:
                message = "Error add zone '%s'" % zone_json['name']
                raise ZoneError(error_message=message)
        else:
            return False

    def update_zone(self):
        if not self._check_self_zone():
            message = "Zone '%s' not created" % self.name
            # print(message)
            raise ZoneError(error_message=message)
        else:
            url = self._get_zone_url() + '/' + str(self.id)
            zone_json = self._make_json()
            response = self.session.patch(url, json=zone_json, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                return True
            else:
                message = "Error update zone"
                # print(message)
                raise ZoneError(error_message=message)

    def delete_zone(self, name=None):
        zone_id = ''
        if not name:
            if self.id:
                zone_id = self.id
            else:
                zone_id = self.get_zone_id(self.name)
        else:
            zone_id = self.get_zone_id(name)
        delete_url = self._get_zone_url() + '/' + str(zone_id)
        response = self.session.delete(delete_url, verify=False)
        if response.status_code == 200:
            return True
        else:
            return False
