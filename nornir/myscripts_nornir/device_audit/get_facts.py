from nornir import InitNornir
from nornir.plugins.functions.text import print_result
from nornir.plugins.tasks.networking import napalm_get

nr = InitNornir(config_file="/Users/stephenamaki/Dropbox/netdevops/nornir/config.yaml", dry_run=True)

targets = nr.filter (role="router")
results = targets.run(task=napalm_get, getters=["facts", "arp_table"])

print_result(results)
# print (nr.config.core.num_workers)
# print(nr.inventory.hosts)
