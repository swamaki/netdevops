#! /usr/bin/env python3

import requests
import urllib3
import json

urllib3.disable_warnings()

'''
Rest API lib

'''
# fortigate_url = 'https://sandboxsdwan.cisco.com:8443/'
# base_url = 'https://sandboxsdwan.cisco.com:8443/dataservice/'

fortigate_url = 'http://192.168.224.222'
base_url = 'http://192.168.224.222'


class apiSession:
    def __init__(self):
        self.session = {}       # API Session Object
        self.uuid = []          # List of available UUID
        self.template_id = ''   # Device Template ID
        self.aaa_login()        # Perform AAA Login

    def aaa_login(self):
        print("********* Authenticating to vManage ****************")
        url = fortigate_url + 'j_security_check'
        body = {
            'j_username': 'devnetuser',
            'j_password': 'Cisco123!'
        }
        temp_session = requests.session()
        api_response = temp_session.post(url, data=body, verify=False)

        if api_response.status_code == 200:
            print("Connection Successful")
            self.session = temp_session
        else:
            print("Connection Failed")
            exit(1)

    def get_request(self, path):
        url = base_url + path
        temp_session = self.session
        api_response = temp_session.get(url, verify=False)
        if api_response.status_code == 200:
            print("GET Successful")
            return(api_response)
        else:
            print("GET Failed")
            exit(1)

    def post_request(self, path, body):
        url = base_url + path
        temp_session = self.session
        api_response = temp_session.post(url, json=body, verify=False)
        if api_response.status_code == 200:
            print("POST Successful")
        else:
            print("POST Failed")
            print(api_response.content)
            exit(1)

#***************** Main ******************


# Get Session Cookie
apiObj = apiSession()

# Get available device UUID
print("***** Get Available device UUID *****")
api_response = apiObj.get_request('system/device/vedges')
device_list = api_response.json()['data']
for device in device_list:
    if 'system-ip' not in device:
        print(device['chasisNumber'])
        apiObj.uuid.append(device['chasisNumber'])

# Get device template ID
print("***** Get Template UUID *****")
api_response = apiObj.get_request('template/device')
template_list = api_response.json()['data']
for template_name in template_list:
    if template_name['templateName'] == 'MY_TEMPLATE':
        apiObj.template_id = template_name['templateId']
print('Template ' + 'MY_TEMPLATE' + '=' + apiObj.template_id)

# Add device to template
print("***** Add device to template *****")
with open('vedge_para.csv', 'r') as f:
    # Get column header
    key_list = f.readline().rstrip('\n').split(',')
    dev_number = 0
    for line in f:
        # Read device config one line at a time
        para_list = line.rstrip('\n').split(',')
        dev_config = dict(zip(key_list, para_list))
        # Assign UUID to device
        dev_config['csv-deviceId'] = api.uuid[dev_number]
        # Build device config structure
        print("---> Creating config for device #" + str(dev_number + 1) + " " + dev_config)
        print(" - Assigned UUID is " + dev_config['csv-deviceId'])
        config_dict = {
            "deviceTemplateList": [
                {
                    "templateId": apiObj.template_id,
                    "device": [dev_config],
                    "isEdited": 'false',
                    "isMasterEdited": 'false'
                }
            ]
        }
        # Send to vManage
        api_response.apiObj.post_request('template/device/config/attachfeature', config_dict)
        print(" - Device successfully attached to template")
        dev_number += 1
    f.close()
