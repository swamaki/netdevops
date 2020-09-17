import requests
import urllib3
#import resp as resp

urllib3.disable_warnings()

'''
not confirmed working 04/12/2020

'''

# import os

# ACI_USERNAME = os.environ.get("ACI_USERNAME")
# ACI_PASSWORD = os.environ.get("ACI_PASSWORD")

# if ACI_USERNAME is None or ACI_PASSWORD is None:
#     print("CISCO ACI login details must be set via environment variables before running.")
#     print("   export ACI_USERNAME=admin")
#     print("   export ACI_PASSWORD=admin")
#     print("")
#     exit("1")


def aaa():
    print("********* Authenticating to ACI ****************")

    url = 'https://sandboxapicdc.cisco.com/api/aaaLogin.json'
    body = {
        "aaaUser": {
            "attributes": {
                "name": "admin",  # ACI_USERNAME
                "pwd": "ciscopsdt"  # ACI_PASSWORD
            }
        }
    }
    resp = requests.post(url, json=body, verify=False)
    #resp = requests.post(url, data=body, verify=False)

    if resp.status_code == 200:
        print("Connection Successful")
        resp_json = resp.json()
        token = resp_json['imdata'][0]['aaaLogin']['attributes']['token']
        return {'APIC-cookie': token}
    else:
        print("Connection Failed")
        exit(1)


def bd(bdName, subnet, aci_token):
    print("***** Creating Bridge Domain " + bdName + "*****")
    url = "https://sandboxapicdc.cisco.com/api/mo/uni/tn-PROD/BD-" + bdName + ".json"
    body = {
        "totalCount": "1",
        "imdata": [{
            "fvBD": {
                "attributes": {
                    "OptimizeWanBandwidth": "no",
                    "annotation": "",
                    "arpFlood": "no",
                    "descr": "",
                    "dn": "uni/tn-PROD/BD- " + bdName,
                    "epClear": "no",
                    "epMoveDetectMode": "",
                    "hostBasedRouting": "no",
                    "intersiteBumTrafficAllow": "no",
                    "intersiteL2Stretch": "no",
                    "ipLearning": "yes",
                    "limitIpLearnToSubnets": "yes",
                    "llAddr": "::",
                    "mac": "00:22:BD:F8:19:FF",
                    "mcastAllow": "no",
                    "multiDstPktAct": "bd-flood",
                    "name": bdName,
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": "",
                    "type": "regular",
                    "unicastRoute": "yes",
                    "unkMacUcastAct": "proxy",
                    "unkMcastAct": "flood",
                    "v6unkMcastAct": "flood",
                    "vmac": "not-applicable"
                },
                "children": [
                    {
                        "fvRsCtx": {
                            "attributes": {
                                "annotation": "",
                                "tnFvCtxName": "VRF1"
                            }
                        }
                    },
                    {
                        "fvSubnet": {
                            "attributes": {
                                "annotation": "",
                                "ctrl": "",
                                "descr": "",
                                "ip": subnet,
                                "name": "",
                                "nameAlias": "",
                                "preferred": "no",
                                "scope": "public",
                                "virtual": "no"
                            }
                        }
                    },

                ]
            }
        }]
    }

    resp = requests.post(url, json=body, cookies=aci_token, verify=False)
    if resp.status_code == 200:
        print("Bridge Domain Successfully Created")
    else:
        print("Bridge Domain Failed to Create")
        exit(1)


#***************** Main ******************
# Get ACI Session Cookie
aci_token = aaa()

# Create one Bridge Domain
bd('BD_Test3', '10.255.3.1/24', aci_token)

# Create multiple Bridge Domains
bdList = [{'bd': 'BD_Test4', 'subnet': '10.255.4.1/24'},
          {'bd': 'BD_Test5', 'subnet': '10.255.5.1/24'},
          {'bd': 'BD_Test6', 'subnet': '10.255.6.1/24'}]
'''
for tempBd in bdList:
    bd(tempBd['bd'],tempBd['subnet'], aci_token)
'''
