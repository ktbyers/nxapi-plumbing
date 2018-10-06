from __future__ import unicode_literals
from builtins import super

import requests
from requests.auth import HTTPBasicAuth
import json

from pynxos import Device
from pynxos.lib.rpc_client import RPCClient


def mock_post(url, timeout, data, headers, auth, verify):
    """Look up the response based on the URL and payload."""
    """
[{"jsonrpc": "2.0", "method": "cli", "params": {"cmd": "show hostname", "version": 1}, "id": 1}]
test/test_std.py::test_obj_attributes https://nxos1.twb-tech.com:8443/ins
{'content-type': 'application/json-rpc'}
[{"jsonrpc": "2.0", "method": "cli", "params": {"cmd": "show hostname", "version": 1}, "id": 1}]
mocked_data/jsonrpc_show_hostname/
mocked_data/jsonrpc_show_hostname/
└── response.json


    """
    base_dir = "./mocked_data"
    data = json.loads(data)
    if data[0].get('jsonrpc'):
        api_type = 'jsonrpc'
    api_cmd = data[0]['params']['cmd']
    api_cmd = api_cmd.replace(' ', '_')
    file_path = "{base_dir}/{api_type}_{api_cmd}/response.json".format(base_dir=base_dir,
        api_type=api_type,
        api_cmd=api_cmd)

    with open(file_path) as f:
        response = json.load(f)
    print(file_path)
    response = requests.post(
            url,
            timeout=timeout,
            data=data,
            headers=headers,
            auth=auth,
            verify=verify,
        )
    print(response)
    return response


class MockDevice(Device):
    def __init__(
        self,
        host,
        username,
        password,
        transport="http",
        encoding="rpc",
        port=None,
        timeout=30,
        verify=True,
    ):
        super().__init__(
            host,
            username,
            password,
            transport=transport,
            encoding=encoding,
            port=port,
            timeout=timeout,
            verify=verify,
        )
        self.rpc = MockRPCClient(
            host, username, password, transport=transport, port=port, verify=verify
        )


class MockRPCClient(RPCClient):
    def send_request(self, commands, method="cli", timeout=30, post_args=False):
        """
        post_args is for testing only and will return the post arguments as a dictionary
        instead of the normal response.
        """
        timeout = int(timeout)
        payload_list = self._build_payload(commands, method)

        if post_args is True:
            return {
                "url": self.url,
                "timeout": timeout,
                "data": payload_list,
                "headers": self.headers,
                "auth": HTTPBasicAuth(self.username, self.password),
                "verify": self.verify,
            }

        response = mock_post(
            self.url,
            timeout=timeout,
            data=json.dumps(payload_list),
            headers=self.headers,
            auth=HTTPBasicAuth(self.username, self.password),
            verify=self.verify,
        )
        response_list = json.loads(response.text)
        print(response_list)

        if isinstance(response_list, dict):
            response_list = [response_list]

        # Add the 'command' that was executed to the response dictionary
        for i, response_dict in enumerate(response_list):
            response_dict["command"] = commands[i]
        return response_list
