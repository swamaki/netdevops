import requests
import resp as resp
import urllib3

urllib3.disable_warnings()

'''
original from labminutes. not confirmed working 04/12/2020

'''
def aaa():
    print("********* Authenticating to ACI ****************")
    url = 'https://sandboxapicdc.cisco.com/api/aaaLogin.json'
    body = {
        "aaaUser": {
            "attributes": {
                "name": "admin",
                "pwd": "ciscopsdt"
            }
        }
    }
    resp = requests.post(url, json=body, verify=False)

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
                    "arpFlood": "no",
                    "descr": "",
                    "dn": "uni/tn-PROD/BD- " + bdName,
                    "epClear": "no",
                    "epMoveDetectMode": "",
                    "intersiteBumTrafficAllow": "no",
                    "intersiteL2Stretch": "no",
                    "ipLearning": "yes",
                    "limitIpLearnToSubnets": "yes",
                    "llAddr": "::",
                    "mac": "00:22:BD:F8:19:FF",
                    "mcastAllow": "yes",
                    "multiDstPktAct": "bd-flood",
                    "name": bdName,
                    "nameAlias": "",
                    "ownerKey": "",
                    "ownerTag": "",
                    "type": "regular",
                    "unicastRoute": "yes",
                    "unkMacUcastAct": "proxy",
                    "unkMcastAct": "flood",
                    "vmac": "not-applicable"
                },
                "children": [{
                    "igmpIfP": {
                        "attributes": {
                            "descr": "",
                            "name": "",
                            "nameAlias": ""
                        },
                        "children": [{
                            "igmpRsIfPol": {
                                "attributes": {
                                    "tDn": "uni/tn-PROD/igmpIfPol-igmpIntPolDefault"
                                }
                            }
                        }]
                    }
                },
                    {
                    "fvSubnet": {
                        "attributes": {
                            "ctrl": "nd",
                            "descr": "",
                            "ip": subnet,
                            "name": "",
                            "nameAlias": "",
                            "preferred": "yes",
                            "scope": "public",
                            "virtual": "no"
                        }
                    }
                },
                    {
                    "fvRsIgmpsn": {
                        "attributes": {
                            "tnIgmpSnoopPolName": "igmpSnoopPolDefault"
                        }
                    }
                },
                    {
                    "fvRsCtx": {
                        "attributes": {
                            "tnFvCtxName": "VRF1"
                        }
                    }
                },
                    {
                    "fvRsBdToEpRet": {
                        "attributes": {
                            "resolveAct": "resolve",
                            "tnFvEpRetPolName": ""
                        }
                    }
                },
                    {
                    "fvRsBDToNdP": {
                        "attributes": {
                            "tnNdIfPolName": ""
                        }
                    }
                },
                    {
                    "dhcpLbl": {
                        "attributes": {
                            "descr": "",
                            "name": "dhcpSrvB",
                            "nameAlias": "",
                            "owner": "tenant",
                            "ownerKey": "",
                            "ownerTag": "",
                            "tag": "yellow-green"
                        },
                        "children": [{
                            "dhcpRsDhcpOptionPol": {
                                "attributes": {
                                    "tnDhcpOptionPolName": ""
                                }
                            }
                        }]
                    }
                }]
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
