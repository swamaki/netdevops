#!/usr/bin/env python3

import time
import datetime
from getpass import getpass
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from netmiko.ssh_exception import AuthenticationException
from paramiko.ssh_exception import SSHException
from pytz import timezone
import re
import yaml
import jinja2

advertised_routes = ['10.10.10.0/24', '10.10.20.0/24']
template_vars = {
    'fw_outside': 'outside',
    'ikev1_policy_no': 999,
    'bgp_asn': 65000,
    'remote_asn': 65012,
    'bgp_peer1': '169.254.1.1',
    'bgp_peer2': '169.254.2.1',
    'advertised_routes': advertised_routes,
    'received_routes': '172.18.0.0/21',
    'vpn_peer1': '1.1.1.1',
    'vpn_peer2': '2.2.2.2',
    'peer1_psk': 'password1',
    'peer2_psk': 'password1',
    'peer1_tunnel_no': '21',
    'peer2_tunnel_no': '22',
    'peer1_tunnel_nameif': 'aws_vpn21',
    'peer2_tunnel_nameif': 'aws_vpn22',
    'peer1_tunnel_ip': '169.254.1.2',
    'peer2_tunnel_ip': '169.254.2.2',
    'peer1_tunnel_mask': '255.255.255.252',
    'peer2_tunnel_mask': '255.255.255.252'
}

# contains list of commands to be run on devices
template_file = 'configs_file_aws.j2'
with open(template_file) as f:
    configs_template = f.read()
    #configs_list = f.read().splitlines()


template = jinja2.Template(configs_template)
print(template.render(template_vars))

'''
confirmed working 04/26/2020

'''
