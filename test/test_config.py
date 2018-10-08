from __future__ import print_function
from __future__ import unicode_literals
import time
import json
from lxml import etree


def test_config_jsonrpc(mock_pynxos_device):
    result = mock_pynxos_device.config("logging history size 200")
    assert result is None


def test_config_list_jsonrpc(mock_pynxos_device):
    cfg_cmds = [
        "logging history size 200",
        "logging history size 300",
        "logging history size 400",
    ]
    result = mock_pynxos_device.config_list(cfg_cmds)
    assert result == [None, None, None]


# def test_show_hostname_xml(mock_pynxos_device_xml):
#    result = mock_pynxos_device_xml.show("show hostname")
#    xml_obj = result
#    response = xml_obj.find("./body/hostname")
#    input_obj = xml_obj.find("./input")
#    msg_obj = xml_obj.find("./msg")
#    code_obj = xml_obj.find("./code")
#    assert input_obj.text == "show hostname"
#    assert msg_obj.text == "Success"
#    assert code_obj.text == "200"
#    assert response.text == "nxos.domain.com"
