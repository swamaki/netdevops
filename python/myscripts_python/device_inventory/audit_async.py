#!/usr/bin/env python3

import time
import datetime
from pytz import timezone
from decouple import config
import re
import yaml
import asyncio
import netdev

"""
works as of 

"""

COMMANDS_FILE = "commands.yml"
INVENTORY_FILE = "devices.yml"

GLOBAL_DEVICE_PARAMS = {
    "device_type": "cisco_ios",
    "username": config("USER_NAME"),
    "password": config("PASSWORD"),
}

# from getpass import getpass
# USER_NAME = input("Enter your SSH username:")
# PASSWORD = getpass()

# GLOBAL_DEVICE_PARAMS = {
#     "device_type": "cisco_ios",
#     "username": USER_NAME,
#     "password": PASSWORD,
# }

def get_devices_list(file_name=INVENTORY_FILE):
    with open(file_name) as f:
        result = yaml.safe_load(f)
    return result["devices"]

def get_commmands_list(file_name=COMMANDS_FILE):
    with open(file_name) as f:
        result = yaml.safe_load(f)
    return result["commands"]

def extract_hostname(sh_ver):
    device_hostname = dict()
    for regexp in software_ver_check(sh_ver):
        device_hostname.update(regexp.search(sh_ver).groupdict())
    return device_hostname

def software_ver_check(sh_ver):

    # Types of devices
    version_list = [
        "IOS XE",
        "NX-OS",
        "C2960X-UNIVERSALK9-M",
        "vios_l2-ADVENTERPRISEK9-M",
        "VIOS-ADVENTERPRISEK9-M",
        "Junos"
    ]
    # Check software versions
    for version in version_list:
        int_version = 0  # Reset integer value
        int_version = sh_ver.find(version)  # Check software version
        if int_version > 0:  # software version found, break out of loop.
            break

    if version == "NX-OS":
        parsed_hostname = [
            re.compile(r"(^\s+)+(Device name:)\s(?P<hostname>\S+)", re.M)
        ]
    elif version == "Junos":
        parsed_hostname = [re.compile(r"(^Hostname:\s+)(?P<hostname>\S+)", re.M)]
    else:  # other cisco ios versions
        parsed_hostname = [re.compile(r"(?P<hostname>^\S+)\s+uptime", re.M)]

    return parsed_hostname


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
    output_filename = "%s_%.2i%.2i%i_%.2i%.2i%.2i.log" % (
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
    
    try: 
        async with netdev.create(**device_params) as device_conn:
            show_version_output = await device_conn.send_command("show version")
            parsed_values.update(extract_hostname(show_version_output))
            print("Running commands on {hostname}".format(**parsed_values))

            commands_list = get_commmands_list()
            commands_output = ["Ping/Traceroute commands of {hostname}".format(**parsed_values)]
            for show_command in commands_list:
                commands_output.append("\n" + ("-" * 60) + "\n\n" + show_command + "\n\n")
                commands_output.append(await device_conn.send_command(show_command))
            commands_output.append("\n" + ("=" * 80) + "\n")
            all_commands_output = "\n".join(commands_output)

            result = {
                "device_hostname": "{hostname}".format(**parsed_values),
                "commands_output": all_commands_output,
            }
            return result
            # yield result

    # except netdev.exceptions.DisconnectError as e:
    except Exception as e:
        exception_msg = "Unable to login to device " + ip_address + "\n"
        exception_msg+= str(e)
        exception_msg+= "\n" + ("=" * 80) + "\n"
        result = {
                "device_hostname": ip_address,
                "commands_output": exception_msg,
            }
        print("Unable to login to device " + ip_address)
        print (e)
        return result


def main():

    start_time = time.time()

    ip_list = get_devices_list()

    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(commands_output(ip)) for ip in ip_list]
    loop.run_until_complete(asyncio.gather(*tasks))

    for task in tasks:
        save_output(task.result()["device_hostname"], task.result()["commands_output"])

    print(f"It took {time.time() - start_time} seconds to run")


if __name__ == "__main__":
    main()
