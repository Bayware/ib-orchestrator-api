#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json
import re
import socket
import warnings
import hashlib
import itertools

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

warnings.filterwarnings('ignore')
# logging.basicConfig(filename='example.log', level=logging.DEBUG)

URL_USER = "api/v1/webpanel/identity/api/user"
URL_USER_ROLE = "api/v1/webpanel/identity/api/client_role_allocate"
URL_DOMAIN = "api/v1/webpanel/identity/api/domain"
URL_CONTROLLER = "api/v1/webpanel/controller"
URL_CONTRACTS = "api/v1/webpanel/topic"
URL_CONTRACT_ROLE = "api/v1/webpanel/topicrole"
URL_ZONE = "api/v1/webpanel/subnet"
URL_TEMPLATE = "api/v1/webpanel/servicetempl"
URL_TEMPLATE_ROLE = "api/v1/webpanel/servicetemplaterole"
URL_CONFIGURE_LINK = "api/v1/webpanel/configured_link"
URL_RESOURCE_USER = "api/v1/webpanel/resource_user"
URL_RESOURCE_ROLE = "api/v1/webpanel/resource_role"



def get_ip_address(hostname):
    regex = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    result = regex.match(hostname)
    address = ''
    if not result:
        address = socket.gethostbyname(hostname)
    else:
        address = hostname
    return address

