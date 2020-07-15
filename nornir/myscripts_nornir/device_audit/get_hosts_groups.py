from nornir.core.deserializer.inventory import InventoryElement
import json
print(json.dumps(InventoryElement.schema(), indent=4))