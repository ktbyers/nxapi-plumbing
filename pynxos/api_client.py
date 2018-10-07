from __future__ import print_function, unicode_literals

from builtins import super
import requests
from requests.auth import HTTPBasicAuth
import json

from xml.dom import minidom
from six import string_types

from pynxos.errors import NXOSError, NXAPIPostError, NXAPICommandError


class RPCBase(object):
    """RPCBase class should be API-type neutral (i.e. shouldn't care whether XML or jsonrpc)."""

    def __init__(
        self,
        host,
        username,
        password,
        transport="https",
        port=None,
        timeout=30,
        verify=True,
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
        self.timeout = timeout
        self.verify = verify

    def _process_api_response(self, response, commands):
        raise NotImplementedError("Method must be implemented in child class")

    def _send_request(self, commands, method):
        payload = self._build_payload(commands, method)

        response = requests.post(
            self.url,
            timeout=self.timeout,
            data=payload,
            headers=self.headers,
            auth=HTTPBasicAuth(self.username, self.password),
            verify=self.verify,
        )

        if response.status_code not in [200]:
            msg = """Invalid status code returned on NX-API POST
commands: {}
status_code: {}""".format(
                commands, response.status_code
            )
            raise NXAPIPostError(msg)

        return self._process_api_request(response, commands)

    def _error_check(self, command_response):
        error = command_response.get("error")
        if error:
            command = command_response.get("command")
            if "data" in error:
                raise NXAPICommandError(command, error["data"]["msg"])
            else:
                raise NXAPICommandError(command, "Invalid command.")


class RPCClient(RPCBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {"content-type": "application/json-rpc"}
        self.api = "jsonrpc"
        self.cmd_method = "cli"
        self.cmd_method_raw = "cli_ascii"

    def _nxapi_command(self, commands, method=None):
        """Send a command down the NX-API channel."""
        if method is None:
            method = self.cmd_method
        if isinstance(commands, string_types):
            commands = [commands]

        api_response = self._send_request(commands, method=method)

        text_response_list = []
        for command_response in api_response:
            self._error_check(command_response)
            text_response_list.append(command_response["result"])
        return text_response_list

    def _build_payload(self, commands, method, rpc_version="2.0", api_version=1.0):
        """Construct the JSON-RPC payload for NX-API."""
        payload_list = []
        id_num = 1
        for command in commands:
            payload = {
                "jsonrpc": rpc_version,
                "method": method,
                "params": {"cmd": command, "version": api_version},
                "id": id_num,
            }
            payload_list.append(payload)
            id_num += 1

        return json.dumps(payload_list)

    def _process_api_response(self, response, commands):
        response_list = json.loads(response.text)
        if isinstance(response_list, dict):
            response_list = [response_list]

        # Add the 'command' that was executed to the response dictionary
        for i, response_dict in enumerate(response_list):
            response_dict["command"] = commands[i]
        return response_list


class XMLClient(RPCBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {"content-type": "application/xml"}
        self.api = "xml"
        self.cmd_method = "cli_show"
        self.cmd_method_raw = "cli_show_ascii"

    def _nxapi_command(self, commands, method=None):
        """Send a command down the NX-API channel."""
        if method is None:
            method = self.cmd_method
        if isinstance(commands, string_types):
            commands = [commands]

        api_response = self._send_request(commands, method=method)

        text_response_list = []
        for command_response in api_response:
            self._error_check_xml(command_response)
            text_response_list.append(api_response)
        return text_response_list

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

    def _process_api_response(self, response, commands):
        response_list = [{"response": response.text}]

        # Add the 'command' that was executed to the response dictionary
        for i, response_dict in enumerate(response_list):
            response_dict["command"] = commands[i]
        return response_list

    def _error_check(self, command_response):
        def NodeAsText(node):
            # convert a XML element to a string
            try:
                nodetext = node[0].firstChild.data.strip()
                return nodetext
            except IndexError:
                return "__na__"

        # creates an xml object and identifies the clierror element
        dom = minidom.parseString(command_response["response"])
        node = dom.getElementsByTagName("clierror")

        if "__na__" != NodeAsText(node):
            raise NXAPICommandError(command_response["command"], NodeAsText(node))