
nxapi-plumbing
=======

A low-level library for managing Cisco devices through NX-API using JSON-RPC and XML.


## Examples:

#### Creating device object using JSON-RPC.

```py
from nxapi_plumbing import Device

device = Device(
    api_format="jsonrpc",
    host="device.domain.com",
    username="admin",
    password="password",
    transport="https",
    port=8443,
)
```

#### JSON-RPC single command that returns structured data.

```py
output = device.show("show hostname")
print(output)
```

#### Output would be the response from the command 

```py
{'hostname': 'nxos.domain.com'}
```

#### JSON-RPC list of commands

```py
output = device.show_list(["show hostname", "show ntp status"])
pprint(output)
```

#### Output would be a list of responses (list of dictionaries)

```json
[
    {
        "command": "show hostname",
        "result": {
            "hostname": "nxos.domain.com"
        }
    },
    {
        "command": "show ntp status",
        "result": {
            "distribution": "Distribution : Disabled",
            "operational_state": "Last operational state: No session"
        }
    }
]
```
