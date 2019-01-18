#!/usr/bin/env python
from argparse import ArgumentParser
from ib_orchestrator_api import IBOrchestratorAPI, IceBreakerError

if __name__ == '__main__':
    parser = ArgumentParser(description="HOSTNAME CONFIG")
    parser.add_argument("hostname", help="sandbox hostname", type=str)
    parser.add_argument("-d", "--domain", help="domain", default="default", type=str)
    parser.add_argument("-l", "--login", help="login hostname", type=str)
    parser.add_argument("-p", "--password", help="login password", type=str)
    nargs_plus = "+"

    options = parser.parse_args()

    base_url = "https://%s/" % options.hostname
    print("base_url: %s\n" % base_url)

    ib_api = IBOrchestratorAPI(hostname=options.hostname,
                               domain=options.domain,
                               login=options.login,
                               password=options.password,
                               base_url=base_url)

    try:
        ib_api.authorization()

        contract_role_name = "client"
        contract_name = "frontend" 
        domain_name = "getaway-app"

        result = ib_api.delete_contract_role(contract_role_name=contract_role_name,contract_name=contract_name,domain_name=domain_name)
        if result:
            print("Contract role  '%s' - deleted" % contract_role_name)
        else:
            print("Contract role  '%s' - not deleted" % contract_role_name)

            
    except IceBreakerError as error:
        print(error.error_message)
