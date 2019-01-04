
class IceBreakerError(Exception):

    #: short-string error 
    error_message = ''
    #: int error status code
    err_code = None

    def __init__(self, err_code=None, error_message=None):
        if error_message is not None:
            self.error_message = error_message
     
        if err_code is not None:
            self.err_code = err_code

    def get_err_code(self):
        return self.err_code

    def get_error(self):
        return self.error_message
    
    def error_responce(self):
        return {'err_code': self.err_code, 'error_message': self.error_message}


class LoginError(IceBreakerError):
    err_code = 401
    error_message = 'Login Failed'


class DomainIDError(IceBreakerError):
    err_code = 400
    error_message = 'Emty Domain ID'

class DomainNameError(IceBreakerError):
    err_code = 400
    error_message = 'Wrong domain error'


class DomainError(IceBreakerError):
    err_code = 400
    error_message = 'Domain add error'


class DomainInControllerError(IceBreakerError):
    err_code = 400
    error_message = 'Error add domain in controller'


class UserError(IceBreakerError):
    err_code = 400
    error_message = 'User add error'


class UserInControllerError(IceBreakerError):
    err_code = 400
    error_message = 'Error add user in controller'


class ControllerError(IceBreakerError):
    err_code = 400
    error_message = 'Controller add error'


class ZoneError(IceBreakerError):
    err_code = 400
    error_message = 'Zone add error'


class ManagedNetworkError(IceBreakerError):
    err_code = 400
    error_message = 'Managed network add error'


class ServiceTemplateError(IceBreakerError):
    err_code = 404
    error_message = 'Service template add error'


class ServiceTemplateRoleError(IceBreakerError):
    err_code = 400
    error_message = 'Service template role add error'


class ContractError(IceBreakerError):
    err_code = 404
    error_message = 'Contract add error'


class ContractRoleError(IceBreakerError):
    err_code = 400
    error_message = 'Contract role add error'


class ConfigureLinkError(IceBreakerError):
    err_code = 400
    error_message = 'Configure link add error'
