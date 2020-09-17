

{
    "response": [
        {
            "id": "d4b33d28-04dd-4733-a6de-8877ec26c196",
            "tag": "campus",
            "networkDeviceId": "e5f93514-3ae5-4109-8b52-b9fa876e1eae",
            "attributeInfo": {}
        },
        {
            "id": "d4b33d28-04dd-4733-a6de-8877ec26c196",
            "tag": "campus",
            "networkDeviceId": "da733ffb-e34b-4733-bd85-b615fb7e61f3",
            "attributeInfo": {}
        },
        {
            "id": "d4b33d28-04dd-4733-a6de-8877ec26c196",
            "tag": "campus",
            "networkDeviceId": "f8c3fc68-cd26-4576-bcec-51f9b578f71e",
            "attributeInfo": {}
        }
    ],
    "version": "0.0"
}

# Import the JSON library. This library provides many handy features for formatting, displaying
# and manipulating json.
import json

# Use 'with" to open the file containing JSON
with open('my-json.json') as file:
    # read the whole file
    data = json.loads(file.read())

# Access values from the JSON and loop through devices and display the network device id
i = 0
for item in data["response"]:
    print("Network Device ID: " + data["response"][i]["networkDeviceId"])
    i += 1
