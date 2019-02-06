import re
from ib_orchestrator_api.core.core import Core
from ib_orchestrator_api.core.errors import ControllerError
from ib_orchestrator_api.core.utils import *

class Controller(Core):
    def __init__(self, url, session, id=None, name=None, description=None, enable=None, host_fqdn=None):
        self._id = id
        self.name = name 
        self.descr = description
        self.enable = enable
        self.url = url 
        self.session = session
        self.host_fqdn = self._get_host_fqdn(host_fqdn)
        self.ip_management = self._get_ip_management()
    
    def _get_controller_url(self):
        """Internal class method: return url which is used for get, create, update, delete controller"""
        return self.url + URL_CONTROLLER
    
    def _get_host_fqdn(self, host_fqdn):
        if not host_fqdn:
            result = (re.sub(r'(http:\/\/|https:\/\/)', '', self.url)).replace('/','')
            return result
        else:
            return host_fqdn

    def _get_ip_management(self):
        ip_management = get_ip_address(self.host_fqdn)
        return ip_management

    def _make_json(self):
        """
        Example JSON
        {
            "descr":"Controller",
            "enable":true,
            "name":"test_controller",
            'host_fqdn': 'test.net', 
            'ip_management': '127.0.0.7'
        }
        """
        
        data = self.to_dict()
        if "_id" in data.keys():
            del data['_id']
        for key, value in data.items():
            if value is None or value == '':
                message = "Field '%s' can't be None" % str(key)

                # print(message)
                # print(str(key), value)
                raise ControllerError(error_message=message)
        return data

    def _get_dict_controller(self, name=None):
        if not name:
            name = self.name
        tmp_controllers = self.get_all_controllers()
        result_controller = ''
        for controller in tmp_controllers['result']:
            if controller['name'] == name:
                result_controller = controller
                break
        
        return result_controller

    def _check_self_controller(self):
        """Internal class method, checks if such an controller exists on the server"""
        result_controller = self._get_dict_controller()
        if not result_controller:
            return False
        else:
            self._id = result_controller.get('id')
            return True
            
    def get_all_controllers(self):
        url = self._get_controller_url()
        result = self.session.get(url, verify=False)
        all_controllers = json.loads(result.text)
        return all_controllers
    
    def get_contrroler(self, controller_name):
        tmp_controllers = self.get_all_controllers()
        result_controller = ''
        for controller in tmp_controllers['result']:
            if controller['name'] == controller_name:
                result_controller = controller
                break
        if not result_controller:
            raise ControllerError(error_message="Controller not found")

        controller = Controller(url=self.url, session=self.session)    
        for field in result_controller.keys():
            if field == 'id':
                setattr(controller, '_id', result_controller[field])
            if field in vars(controller).keys():
                setattr(controller, field, result_controller[field])
        return controller

    def create_controller(self):
        url = self._get_controller_url()
        if not self._check_self_controller():
            controller_json = self._make_json()
            response = self.session.put(url, json=controller_json, verify=False)
            if response.status_code == 200 or response.status_code == 201:
                self._id = (json.loads(response.text)).get('id')
                return True
            else:
                message = "Error add controller '%s'" % controller_json['name']
                raise ControllerError(error_message=message)
        else:
            return False

    def delete_controller(self, name=None):
        if not name:
            name = self.name
        
        result = self._get_dict_controller(name=name)
        controller_id = ''
        if not result:
            print("netu usera")
        else:
            controller_id = result.get('id')
        
        delete_url = self._get_controller_url() + '/' + str(controller_id)
        response = self.session.delete(delete_url, verify=False)
        if response.status_code == 200 or response == 204:
            return True
        else:
            return False