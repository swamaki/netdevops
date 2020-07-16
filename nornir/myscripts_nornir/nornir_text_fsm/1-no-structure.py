from nornir import InitNornir
from nornir.plugins.tasks.networking import netmiko_send_command
from nornir.plugins.functions.text import print_result

nr = InitNornir(config_file="/Users/stephenamaki/Dropbox/netdevops/nornir/config.yaml")
target_hosts = nr.filter(role="access")

results = target_hosts.run(
    netmiko_send_command, command_string="show interface switchport"
)

print_result(results)
