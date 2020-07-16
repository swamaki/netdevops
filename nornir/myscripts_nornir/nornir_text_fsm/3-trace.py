from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.functions.text import print_result
from nornir.plugins.tasks.networking import netmiko_send_config


def get_facts(task):
    r = task.run(
        netmiko_send_command,
        command_string="show interface switchport",
        use_textfsm=True,
    )
    task.host["facts"] = r.result


def main() -> None:
    nr = InitNornir(
        config_file="/Users/stephenamaki/Dropbox/netdevops/nornir/config.yaml"
    )
    target_hosts = nr.filter(role="core")

    result = target_hosts.run(task=get_facts)
    print_result(result)
    import ipdb

    ipdb.set_trace()


if __name__ == "__main__":
    main()

# commands to run in the debugger
# nr.inventory.hosts
# nr.inventory.hosts['CORE-1'].hostname
# nr.inventory.hosts['CORE-1'].groups
# nr.inventory.hosts['CORE-1'].data
# nr.inventory.hosts['CORE-1']['facts']
# nr.inventory.hosts['CORE-1']['facts'][0]
# nr.inventory.hosts['CORE-1']['facts'][0]['admin_mode']
# nr.inventory.hosts['CORE-1'] == task.host
