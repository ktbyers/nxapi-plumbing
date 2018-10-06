from __future__ import print_function, unicode_literals

import requests
from requests.auth import HTTPBasicAuth

from pynxos.errors import NXOSError


class XMLClient(object):
    def __init__(
        self, host, username, password, transport="http", port=None, verify=True
    ):

        if transport not in ["http", "https"]:
            raise NXOSError("'{}' is an invalid transport.".format(transport))

        if port is None:
            if transport == "http":
                port = 80
            elif transport == "https":
                port = 443

        self.url = "{}://{}:{}/ins".format(transport, host, port)
        self.headers = {"content-type": "application/xml"}
        self.username = username
        self.password = password
        self.verify = verify

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
        timeout = int(timeout)
        payload = self._build_payload(commands, method)

        try:
            response = requests.post(
                self.url,
                timeout=timeout,
                data=payload,
                headers=self.headers,
                auth=HTTPBasicAuth(self.username, self.password),
                verify=False,
            )
        except requests.exceptions.ConnectionError as e:
            raise requests.exceptions.ConnectionError(e)
        else:
            response_list = [{"response": response.text}]

            # Add the 'command' that was executed to the response dictionary
            for i, response_dict in enumerate(response_list):
                response_dict["command"] = commands[i]
            return response_list
