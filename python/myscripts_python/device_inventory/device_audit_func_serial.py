#!/usr/bin/env python3

import time
import datetime
from getpass import getpass
from netmiko import ConnectHandler
from pytz import timezone
import re
from decouple import config
import yaml

"""
works as of 05/01/2020

"""

COMMANDS_FILE = "inventory_commands.yml"
INVENTORY_FILE = "inventory_devices.yml"

GLOBAL_DEVICE_PARAMS = {
    "device_type": "cisco_ios",
    "username": config("USER_NAME"),
    "password": config("PASSWORD"),
}
# SHOW_VER_RE_LIST = [re.compile(r"(?P<hostname>^\S+)\s+uptime", re.M)]


def software_ver_check(sh_ver):

    # Types of devices
    version_list = [
        "IOS XE",
        "NX-OS",
        "C2960X-UNIVERSALK9-M",
        "vios_l2-ADVENTERPRISEK9-M",
        "VIOS-ADVENTERPRISEK9-M",
    ]
    # Check software versions
    for version in version_list:
        int_version = 0  # Reset integer value
        int_version = sh_ver.find(version)  # Check software version
        if int_version > 0:  # software version found, break out of loop.
            break

    if version == "NX-OS":
        SHOW_VER_RE_LIST = [
            re.compile(r"(^\s+)+(Device name:)\s(?P<hostname>\S+)", re.M)
        ]

    else:  # other cisco ios versions
        SHOW_VER_RE_LIST = [re.compile(r"(?P<hostname>^\S+)\s+uptime", re.M)]

    return SHOW_VER_RE_LIST


def read_inventory(file_name=INVENTORY_FILE):
    with open(file_name) as f:
        result = yaml.safe_load(f)
    return result


def get_devices_list():
    return read_inventory()["devices"]


def read_commands(file_name=COMMANDS_FILE):
    with open(file_name) as f:
        result = yaml.safe_load(f)
    return result


def get_commmands_list():
    return read_commands()["commands"]


def extract_hostname(sh_ver):
    device_hostname = dict()
    for regexp in software_ver_check(sh_ver):
        device_hostname.update(regexp.search(sh_ver).groupdict())
    return device_hostname


def save_output(device_hostname, commands_output):

    """
    writes outputs to a file.

    Args:
        device_hostname (string): parsed hostname of device on which commands were executed
        command output(dict): concantenated string of the outputs executed on devices

    Returns:
        Filename is timestamped with date etc

    """

    est = timezone("EST")
    time_now = datetime.datetime.now(est)
    output_filename = "%s_%.2i%.2i%i_%.2i%.2i%.2i" % (
        device_hostname,
        time_now.year,
        time_now.month,
        time_now.day,
        time_now.hour,
        time_now.minute,
        time_now.second,
    )
    output_file = open(output_filename, "a")
    output_file.write(commands_output)
    output_file.close


def commands_output(ip_address):

    """
    Login and run list of commands from file on all devices on the site

    Args:
        ip_address (list): host ip address from list component

    Returns:
        hostname (dict): key is device hostname, value is dictionary containing hostname for use in saving output to file
        command output(dict): concantenated string of the outputs executed on devices

    the method used to parse the device hostname could be simpler but it's flexible enough to add other parsed variables.

    """

    device_params = GLOBAL_DEVICE_PARAMS.copy()
    device_params["ip"] = ip_address
    device_conn = ConnectHandler(**device_params)

    parsed_values = dict()
    parsed_values.update(extract_hostname(device_conn.send_command("show version")))
    print("Running commands on {hostname}".format(**parsed_values))

    commands_list = get_commmands_list()
    # commands_output = ""
    commands_output = "Running commands on {hostname}".format(**parsed_values)
    for show_command in commands_list:
        commands_output += "\n\n" + ("=" * 80) + "\n\n" + show_command + "\n\n"
        commands_output += device_conn.send_command(show_command)

    # save_output("{hostname}".format(**parsed_values), commands_output)
    result = {
        "device_hostname": "{hostname}".format(**parsed_values),
        "commands_output": commands_output,
    }
    device_conn.disconnect()
    return result


def main():
    start_time = time.time()

    ip_list = get_devices_list()

    for ip in ip_list:
        result = commands_output(ip)
        save_output(result["device_hostname"], result["commands_output"])

    print(f"It took {time.time() - start_time} seconds to run")


if __name__ == "__main__":
    main()
