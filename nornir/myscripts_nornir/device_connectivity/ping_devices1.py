from nornir import InitNornir
from nornir.plugins.tasks import networking
from nornir.plugins.functions.text import print_result
from nornir.plugins.tasks.networking import netmiko_send_command
import colorama
from colorama import Fore, Style

nr = InitNornir(config_file="/Users/stephenamaki/Dropbox/netdevops/nornir/config.yaml")
target_hosts = nr.filter(role="access")

print(
    Fore.YELLOW
    + "*" * 5
    + " INITIALISING FULL NETWORK PING TEST "
    + "*" * 25
    + Style.RESET_ALL
)
print("Nornir is conducting a full ping test across all nodes in the network...")
print("< If there are no alerts: all devices have full reachability >")
print("\n")
for i in range(11, 16):
    target = "169.254.224." + str(i)
    results = target_hosts.run(netmiko_send_command, command_string="ping " + target)
    for key in results.keys():
        response = results[key].result
        if not "!!!" in response:
            print(Fore.CYAN + "-" * 40 + Style.RESET_ALL)
            print(
                Fore.RED + "ALERT: " + Style.RESET_ALL + key + " cannot ping " + target
            )
            print(Fore.CYAN + "-" * 40 + Style.RESET_ALL)

print("\n")
print("*" * 5 + Fore.GREEN + " TESTS COMPLETE " + Style.RESET_ALL + "*" * 46)
