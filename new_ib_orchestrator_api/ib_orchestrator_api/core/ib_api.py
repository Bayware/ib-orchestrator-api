import re
import socket
import requests
import json
from .core import Core
from ib_orchestrator_api.modules import *

class IB_API(Core):
    def __init__(self, url, session):
        self.domain = Domain(url=url, session=session)