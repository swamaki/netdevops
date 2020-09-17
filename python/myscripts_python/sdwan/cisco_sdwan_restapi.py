#! /usr/bin/env python3

"""
Class with REST Api GET and POST libraries

Example: python rest_api_lib.py vmanage_hostname username password

PARAMETERS:
    vmanage_hostname : Ip address of the vmanage or the dns name of the vmanage
    username : Username to login the vmanage
    password : Password to login the vmanage

Note: All the three arguments are manadatory

Dowloaded from:
https://sdwan-docs.cisco.com/Product_Documentation/Command_Reference/Command_Reference/vManage_REST_APIs/vManage_REST_APIs_Overview/Using_the_vManage_REST_APIs
page 4 explains the differences from this on the first 3 pages
"""
import requests
import sys
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class rest_api_lib:
    def __init__(self, vmanage_ip, username, password):
        self.vmanage_ip = vmanage_ip
        self.session = {}
        self.login(self.vmanage_ip, username, password)

    def login(self, vmanage_ip, username, password):
        """Login to vmanage"""
        base_url_str = 'https://%s/' % vmanage_ip
        login_action = '/j_security_check'

        # Format data for loginForm
        login_data = {'j_username': username, 'j_password': password}

        # Url for posting login data
        login_url = base_url_str + login_action
        url = base_url_str + login_url

        login_session = requests.session()

        # If the vmanage has a certificate signed by a trusted authority change verify to True
        login_response = login_session.post(url=login_url, data=login_data, verify=False)

        if '<html>' in login_response.content:
            print("Login Failed")
            sys.exit(0)

        # preserve the session that gets established after we login into the API and use this session in the other methods of the class
        self.session[vmanage_ip] = login_session

    def get_request(self, mount_point):
        """GET request"""
        url = "https://%s:8443/dataservice/%s" % (self.vmanage_ip, mount_point)
        print(url)
        # We do a get request using the sesssion that was opened in the login function.
        response = self.session[self.vmanage_ip].get(url, verify=False)
        data = response.content
        return data

    def post_request(self, mount_point, payload, headers={'Content-Type': 'application/json'}):
        """POST request"""
        url = "https://%s:8443/dataservice/%s" % (self.vmanage_ip, mount_point)
        payload = json.dumps(payload)
        print(payload)
        response = self.session[self.vmanage_ip].post(url=url, data=payload, headers=headers, verify=False)
        data = response.content
        # data = response.json() # in explanation
        return data


def main(args):
    if not len(args) == 3:
        print __doc__
        return
    vmanage_ip, username, password = args[0], args[1], args[2]
    obj = rest_api_lib(vmanage_ip, username, password)
    # Example request to get devices from the vmanage "url=https://vmanage.viptela.com/dataservice/device"
    response = obj.get_request('device')
    print response
    # Example request to make a Post call to the vmanage "url=https://vmanage.viptela.com/dataservice/device/action/rediscover"
    payload = {"action": "rediscover", "devices": [{"deviceIP": "172.16.248.105"}, {"deviceIP": "172.16.248.106"}]}
    response = obj.post_request('device/action/rediscover', payload)
    print response


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
