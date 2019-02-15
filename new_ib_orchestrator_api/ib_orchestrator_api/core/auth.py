
import requests
import json
from .errors import LoginError


def authorization(base_url):
    domain = 'default'
    login = 'admin'
    password = 'bayware1'
    session = requests.session()
    token_url = base_url + "api/v1/webpanel/token"
    response = session.post(
        token_url,
        json={'domain': domain, 'username': login, 'password': password},
        verify=False)
    if response.status_code == 200 or response.status_code == 201:
        tmp_token = json.loads(response.text)
        token = "Bearer " + tmp_token.get("token")
        # headers.update({"Authorization": token})
        session.headers.update({"Authorization": token,
                                'Content-Type': 'application/json'})
        return session
    else:
        print(response)
        print(response.text)
        raise LoginError()
