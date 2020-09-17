#!/usr/bin/env python
import xml.dom.minidom
import json

import jinja2
import xmltodict
import yaml
from ncclient import manager
from decouple import config
import time

INVENTORY_FILE = "devices_file.yml"

CONNECTION_PARAMS = {
    'username': config("USER_NAME"),
    'password': config("PASSWORD"),
    'hostkey_verify': False,
}

CONFIG_DATA = {
    'loopbacks': [
        {
            'number': '1500',
            'description': 'This one has a description'
        },
        {
            'number': '1501',
            'ipv4_address': '100.64.151.1',
            'ipv4_mask': '255.255.255.0',
        }
    ]
}

TEMPLATES = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))


def read_inventory(file_name=INVENTORY_FILE):
    with open(file_name) as f:
        result = yaml.safe_load(f)
    return result

def get_devices_list():
    return read_inventory()["devices"]

def prettify_xml(xml_string):
    xml_dom = xml.dom.minidom.parseString(str(xml_string))
    return xml_dom.toprettyxml()


def get_config(nc_conn):
    nc_reply = nc_conn.get_config(source='running')
    current_config = xmltodict.parse(nc_reply.data_xml)['data']
    # print(json.dumps(current_config, indent=2))
    sw_version = current_config['native']['version']
    hostname = current_config['native']['hostname']
    print(f'SW version: {sw_version}')
    print(f'hostname: {hostname}')

def get_capbalities(nc_conn):
    for device_cap in nc_conn.server_capabilities: 
        print(device_cap)

def get_schema(nc_conn):
    device_schema = nc_conn.get_schema('Cisco-IOS-XE-native')
    return device_schema

def configure_device(nc_conn, config_data, template_name):
    template = TEMPLATES.get_template(template_name)
    config = template.render(config_data)
    nc_reply = nc_conn.edit_config(
        target='running',
        config=config,
    )
    if nc_reply.ok:
        print("Successfully performed NETCONF edit config operation")

def main():
    start_time = time.time()

    ip_list = get_devices_list()

    conn_params = CONNECTION_PARAMS.copy()
    
    for ip_address in ip_list:
        conn_params["host"] = ip_address
        with manager.connect(**conn_params) as nc_connection:
            get_config(nc_connection)
            # print(get_schema(nc_connection))
            get_capbalities(nc_connection)
            # configure_device(nc_connection, config_data=CONFIG_DATA, template_name='loopbacks.j2')
            print("=" * 80)
    
    print(f"It took {time.time() - start_time} seconds to run")


if __name__ == '__main__':
    main()
