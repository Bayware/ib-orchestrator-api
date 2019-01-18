# -*- coding: utf-8 -*-

import os
import requests
import re
import json

from ib_orchestrator_api import IBOrchestratorAPI, IceBreakerError
from argparse import ArgumentParser

CONFIG_FILE = 'data/init_data_sandbox.json'

def main():
    parser = ArgumentParser( description = 'Uses NBI to add Links to sandbox.' )
    parser.add_argument( '--user', help = 'user to add', type = str )
    parser.add_argument( '--contract', help = 'user to add', type = str )
    parser.add_argument( 'sandbox_name', help = 'six-letter sandbox e.g., turtle', type = str )
    options = parser.parse_args()

    cfg_file = CONFIG_FILE

    print( 'Working with sandbox %s' % options.sandbox_name )

    hostname = 'c1' + options.sandbox_name + '.sb.bayware.io'
    domain = 'default'
    login = 'admin'
    password = 'greencowsdrive13'
    base_url = 'https://' + hostname + '/'

    print( 'base_url: %s' % base_url )

    ib_api = IBOrchestratorAPI( hostname = hostname, domain = domain, login = login,
                                password = password, base_url = base_url )

    # login to orchestrator
    ib_api.authorization()

    # read local config file
    my_dict = ib_api.read_from_json( cfg_file )

    # add user
    users_info = [ user for user in my_dict[ 'user' ] if user[ 'username' ] == options.user ]

    for user in users_info:
        try:
            ib_api.add_user( user )
            print( 'adding user %s' % user[ 'username' ] )
        except IceBreakerError as error:
            print( error.error_message )

    # add contract
    contracts_info = [ contract for contract in my_dict[ 'contracts' ] if contract[ 'name' ] == options.contract ]

    for contract in contracts_info:
        try:
            ib_api.add_contracts( contract )
            print( 'adding contract %s' % contract[ 'name' ] )
        except IceBreakerError as error:
            print( error.error_message )

    return

if __name__ == '__main__':
    main()
