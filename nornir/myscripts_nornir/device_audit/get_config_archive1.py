from nornir import InitNornir
from nornir.plugins.tasks import networking
from nornir.plugins.functions.text import print_result
from nornir.plugins.tasks.files import write_file
from datetime import date
import pathlib


def backup_configurations(task):
    config_dir = "config_archive"
    device_dir = config_dir + "/" + task.host.name
    pathlib.Path(config_dir).mkdir(exist_ok=True)
    pathlib.Path(device_dir).mkdir(exist_ok=True)
    r = task.run(task=networking.napalm_get, getters=["config"])
    task.run(
        task=write_file,
        content=r.result["config"]["running"],
        filename=f"" + str(device_dir) + "/" + str(date.today()) + ".txt",
    )


nr = InitNornir(config_file="/Users/stephenamaki/Dropbox/netdevops/nornir/config.yaml")

target_hosts = nr.filter(role="core")
result = target_hosts.run(name="Creating Backup Archive", task=backup_configurations)

print_result(result)
