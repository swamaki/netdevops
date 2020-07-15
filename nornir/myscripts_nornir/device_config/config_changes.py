from nornir import InitNornir
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks.networking import netmiko_send_config, netmiko_send_command

nr = InitNornir(config_file="/Users/stephenamaki/Dropbox/netdevops/nornir/config.yaml", dry_run=True)

def baseconfig(command_output):
    command_output.run(task=netmiko_send_config, config_file= "config_file.cfg")
    command_output.run(task=netmiko_send_command, command_string = "show run | in scp")

targets = nr.filter (country="usa")
results = targets.run(task = baseconfig)

print_title("DEPLOYING CONFIGURATIONS")
print_result(results)
