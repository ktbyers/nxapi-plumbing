from __future__ import print_function, unicode_literals
import requests
from requests.auth import HTTPBasicAuth

from pynxos.errors import NXOSError


class XMLClient(object):
    def __init__(self, host, username, password, transport='http', port=None):
        if transport not in ['http', 'https']:
            raise NXOSError("'%s' is an invalid transport." % transport)

        if port is None:
            if transport == 'http':
                port = 80
            elif transport == 'https':
                port = 443

        self.url = '%s://%s:%s/ins' % (transport, host, port)
        self.headers = {'content-type': u'application/xml'}
        self.username = username
        self.password = password

    def _build_payload(self, commands, method, xml_version='1.0', version=1):

        xml_commands = ""
        for command in commands:
            if not xml_commands:
                # initial command is just the command itself
                xml_commands += command
            else:
                # subsequent commands are separate by semi-colon
                xml_commands += ' ;{}'.format(command)

        payload = """<?xml version="{xml_version}"?>
            <ins_api>
                <version>{version}</version>
                <type>{method}</type>
                <chunk>0</chunk>
                <sid>sid</sid>
                <input>{command}</input>
                <output_format>xml</output_format>
            </ins_api>""".format(xml_version=xml_version, version=version,
                                 method=method, command=xml_commands)
        return payload

    def send_request(self, commands, method='cli_show', timeout=30):
        timeout = int(timeout)
        payload = self._build_payload(commands, method)
        response = requests.post(self.url,
                                 timeout=timeout,
                                 data=payload,
                                 headers=self.headers,
                                 auth=HTTPBasicAuth(self.username, self.password),
                                 verify=False)
        response = response.text
        return response
