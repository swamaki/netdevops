#!/usr/bin/env python3

import time
import datetime
from pytz import timezone
import re
from decouple import config
import yaml
import asyncio
import netdev

"""
works as of 05/01/2020

"""


INVENTORY_FILE = "device_inventory_scripts\\inventory_devices.yml"
COMMANDS_FILE = "device_inventory_scripts\\inventory_commands.yml"

GLOBAL_DEVICE_PARAMS = {
    "device_type": "cisco_ios",
    "username": config("USER_NAME"),
    "password": config("PASSWORD"),
}
SHOW_VER_RE_LIST = [re.compile(r"(?P<hostname>^\S+)\s+uptime", re.M)]


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
    for regexp in SHOW_VER_RE_LIST:
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


async def commands_output(ip_address):

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
    device_params["host"] = ip_address
    parsed_values = dict()

    async with netdev.create(**device_params) as device_conn:
        show_version_output = await device_conn.send_command("show version")
        parsed_values.update(extract_hostname(show_version_output))
        print("Running commands on {hostname}".format(**parsed_values))

        commands_list = get_commmands_list()
        commands_output = ""
        for show_command in commands_list:
            commands_output += "\n\n" + ("=" * 80) + "\n\n" + show_command + "\n\n"
            commands_output += await device_conn.send_command(show_command)

        result = {
            "device_hostname": "{hostname}".format(**parsed_values),
            "commands_output": commands_output,
        }
        return result


def main():
    start_time = time.time()

    ip_list = get_devices_list()

    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(commands_output(ip)) for ip in ip_list]

    loop.run_until_complete(asyncio.wait(tasks))

    for task in tasks:
        save_output(task.result()["device_hostname"], task.result()["commands_output"])

    print(f"It took {time.time() - start_time} seconds to run")


if __name__ == "__main__":
    main()
