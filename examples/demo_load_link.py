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
        domain_name = "cloud-net"
        dict_domain = ib_api.get_domain_list()
        domain_id_a = ib_api.get_domain_id(dict_domain['result'], domain_name)
        domain_id_z = ib_api.get_domain_id(dict_domain['result'], domain_name)
        link = {
            "node_a": "aws-p3",
            "domain_id_a": domain_id_a,
            "node_z": "aws-p1",
            "domain_id_z": domain_id_z,
            "admin_status": True,
            "ipsec_enable": True,
            "tunnel_ip_type": 1
        }
        result = ib_api.configured_link(link)
        if result:
            print("Link from  '%s' to '%s' - add" % (link["node_a"], link["node_z"]))
        else:
            print("Link from  '%s' to '%s' - already created" % (link["node_a"], link["node_z"]))
    except IceBreakerError as error:
        print(error.error_message)
