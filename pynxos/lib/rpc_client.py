from __future__ import print_function, unicode_literals

from builtins import super
import requests
from requests.auth import HTTPBasicAuth
import json

from pynxos.errors import NXOSError


class RPCBase(object):
    def __init__(
        self, host, username, password, transport="https", port=None, verify=True
    ):
        if transport not in ["http", "https"]:
            raise NXOSError("'{}' is an invalid transport.".format(transport))

        if port is None:
            if transport == "http":
                port = 80
            elif transport == "https":
                port = 443

        self.url = "{}://{}:{}/ins".format(transport, host, port)
        self.username = username
        self.password = password
        self.verify = verify

    def _send_request(self, commands, method, timeout=30):
        timeout = int(timeout)
        payload = self._build_payload(commands, method)
        if self.api == "jsonrpc":
            payload = json.dumps(payload)

        response = requests.post(
            self.url,
            timeout=timeout,
            data=payload,
            headers=self.headers,
            auth=HTTPBasicAuth(self.username, self.password),
            verify=self.verify,
        )

        if self.api == "jsonrpc":
            response_list = json.loads(response.text)
            if isinstance(response_list, dict):
                response_list = [response_list]
        elif self.api == "xml":
            response_list = [{"response": response.text}]

        # Add the 'command' that was executed to the response dictionary
        for i, response_dict in enumerate(response_list):
            response_dict["command"] = commands[i]
        return response_list


class RPCClient(RPCBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {"content-type": "application/json-rpc"}
        self.api = "jsonrpc"

    def _build_payload(self, commands, method, rpc_version="2.0", api_version=1.0):
        payload_list = []

        id_num = 1
        for command in commands:
            payload = dict(
                jsonrpc=rpc_version,
                method=method,
                params=dict(cmd=command, version=api_version),
                id=id_num,
            )
            payload_list.append(payload)
            id_num += 1
        return payload_list

    def send_request(self, commands, method="cli", timeout=30):
        return self._send_request(commands, method=method, timeout=timeout)


class XMLClient(RPCBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {"content-type": "application/xml"}
        self.api = "xml"

    def _build_payload(self, commands, method, xml_version="1.0", version="1.0"):
        xml_commands = ""
        for command in commands:
            if not xml_commands:
                # initial command is just the command itself
                xml_commands += command
            else:
                # subsequent commands are separate by semi-colon
                xml_commands += " ;{}".format(command)

        payload = """<?xml version="{xml_version}"?>
            <ins_api>
                <version>{version}</version>
                <type>{method}</type>
                <chunk>0</chunk>
                <sid>sid</sid>
                <input>{command}</input>
                <output_format>xml</output_format>
            </ins_api>""".format(
            xml_version=xml_version,
            version=version,
            method=method,
            command=xml_commands,
        )
        return payload

    def send_request(self, commands, method="cli_show", timeout=30):
        return self._send_request(commands, method=method, timeout=timeout)
