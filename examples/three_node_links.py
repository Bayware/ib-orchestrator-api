# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from ib_orchestrator_api import IBOrchestratorAPI, IceBreakerError

def main():
    parser = ArgumentParser( description = 'Uses NBI to add Links to sandbox.' );
    parser.add_argument( 'sandbox_name', help = 'six-letter sandbox e.g., turtle', type = str )
    parser.add_argument( '--group', help = 'type 1 for main deployment and type 2 after final GCP proc dep', type = int, choices = range( 1,3 ) )
    options = parser.parse_args()

    print( 'Working with sandbox %s' % options.sandbox_name )

    hostname = 'c1' + options.sandbox_name + '.sb.bayware.io'
    domain = 'default'
    login = 'admin'
    password = 'greencowsdrive13'
    base_url = 'https://' + hostname + '/'

    print( 'base_url: %s' % base_url )

    ib_api = IBOrchestratorAPI( hostname = hostname, domain = domain, login = login,
                                password = password, base_url = base_url )

    ib_api.authorization()
    domain_name = 'cloud-net'
    dict_domain = ib_api.get_domain_list()
    domain_id_a = ib_api.get_domain_id(dict_domain['result'], domain_name)
    domain_id_z = ib_api.get_domain_id(dict_domain['result'], domain_name)
    link = {
        "node_a": "host_a",
        "domain_id_a": domain_id_a,
        "node_z": "host_b",
        "domain_id_z": domain_id_z,
        "admin_status": True,
        "ipsec_enable": True,
        "tunnel_ip_type": 2
    }

    if options.group == 1:
        endpoints = [ ( 'aws-p1-' + options.sandbox_name, 'aws-p2-' + options.sandbox_name ),
                      ( 'aws-p1-' + options.sandbox_name, 'azr-p1-' + options.sandbox_name ),
                      ( 'aws-p2-' + options.sandbox_name, 'azr-p1-' + options.sandbox_name ) ]
    elif options.group == 2:
        endpoints = [ ( 'aws-p1-' + options.sandbox_name, 'gcp-p1-' + options.sandbox_name ),
                      ( 'aws-p2-' + options.sandbox_name, 'gcp-p1-' + options.sandbox_name ),
                      ( 'azr-p1-' + options.sandbox_name, 'gcp-p1-' + options.sandbox_name ) ]
    else:
        print( 'bad group specified:  %d' % options.group )
        return

    for ( node_a, node_z ) in endpoints:
        print( 'Link endpoints a <--> z: %s <--> %s' % ( node_a, node_z ) )

        link[ 'node_a' ] = node_a;
        link[ 'node_z' ] = node_z;

        try:
            result = ib_api.configured_link(link)
            if result:
                print("Link from  '%s' to '%s' - add" % (link["node_a"], link["node_z"]))
            else:
                print("Link from  '%s' to '%s' - already created" % (link["node_a"], link["node_z"]))
        except IceBreakerError as error:
            print(error.error_message)

    return

if __name__ == '__main__':
    main()
