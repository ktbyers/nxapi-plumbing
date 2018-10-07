from __future__ import unicode_literals
from builtins import super

from requests.auth import HTTPBasicAuth
import json

from pynxos import Device
from pynxos.rpc_client import RPCClient


def mock_post(url, timeout, data, headers, auth, verify):
    """Look up the response based on the URL and payload."""

    # Construct the path to search for the mocked data
    # e.g. ./mocked_data/jsonrpc_show_hostname/response.json
    base_dir = "test/mocked_data"
    data = json.loads(data)
    if data[0].get("jsonrpc"):
        api_type = "jsonrpc"
    api_cmd = data[0]["params"]["cmd"]
    api_cmd = api_cmd.replace(" ", "_")
    file_path = "{base_dir}/{api_type}_{api_cmd}/response.json".format(
        base_dir=base_dir, api_type=api_type, api_cmd=api_cmd
    )

    with open(file_path) as f:
        return json.load(f)


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

        mock_response = mock_post(
            self.url,
            timeout=timeout,
            data=json.dumps(payload_list),
            headers=self.headers,
            auth=HTTPBasicAuth(self.username, self.password),
            verify=self.verify,
        )
        # Modified from actual behavior here to simplify the mocking
        # response_list = json.loads(response.text)
        response_list = mock_response

        if isinstance(response_list, dict):
            response_list = [response_list]

        # Add the 'command' that was executed to the response dictionary
        for i, response_dict in enumerate(response_list):
            response_dict["command"] = commands[i]
        return response_list
