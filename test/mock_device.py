from __future__ import unicode_literals
from builtins import super

from requests.auth import HTTPBasicAuth
import json
from lxml import etree

from pynxos import Device
from pynxos import RPCClient, XMLClient


class FakeResponse(object):
    def __init__(self):
        self.text = ""


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
        return f.read()


def mock_post_xml(url, timeout, data, headers, auth, verify):
    """Look up the response based on the URL and payload."""

    # Construct the path to search for the mocked data
    # e.g. ./mocked_data/jsonrpc_show_hostname/response.json
    base_dir = "test/mocked_data"
    xml_root = etree.fromstring(data)
    input_obj = xml_root.find("./input")
    api_type = "xml"
    api_cmd = input_obj.text
    api_cmd = api_cmd.replace(" ", "_")
    file_path = "{base_dir}/{api_type}_{api_cmd}/response.xml".format(
        base_dir=base_dir, api_type=api_type, api_cmd=api_cmd
    )

    with open(file_path) as f:
        return f.read()


class MockDevice(Device):
    def __init__(
        self,
        host,
        username,
        password,
        transport="http",
        api_format="jsonrpc",
        port=None,
        timeout=30,
        verify=True,
    ):
        super().__init__(
            host,
            username,
            password,
            transport=transport,
            api_format=api_format,
            port=port,
            timeout=timeout,
            verify=verify,
        )
        if api_format == "jsonrpc":
            self.api = MockRPCClient(
                host,
                username,
                password,
                transport=transport,
                port=port,
                timeout=timeout,
                verify=verify,
            )
        elif api_format == "xml":
            self.api = MockXMLClient(
                host,
                username,
                password,
                transport=transport,
                port=port,
                timeout=timeout,
                verify=verify,
            )


class MockRPCClient(RPCClient):
    def _send_request(self, commands, method="cli"):
        payload = self._build_payload(commands, method)

        mock_response = mock_post(
            self.url,
            timeout=self.timeout,
            data=payload,
            headers=self.headers,
            auth=HTTPBasicAuth(self.username, self.password),
            verify=self.verify,
        )

        response_obj = FakeResponse()
        response_obj.text = mock_response
        response_obj.status_code = 200

        return self._process_api_response(response_obj, commands)


class MockXMLClient(XMLClient):
    def _send_request(self, commands, method="cli_show"):
        payload = self._build_payload(commands, method)

        mock_response = mock_post_xml(
            self.url,
            timeout=self.timeout,
            data=payload,
            headers=self.headers,
            auth=HTTPBasicAuth(self.username, self.password),
            verify=self.verify,
        )

        response_obj = FakeResponse()
        response_obj.text = mock_response
        response_obj.status_code = 200

        return self._process_api_response(response_obj, commands)
