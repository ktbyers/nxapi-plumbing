from __future__ import print_function
from __future__ import unicode_literals
import time
import json
from lxml import etree


# def test_real_device(pynxos_device):
#    result = pynxos_device.show("show ip int brief vrf management")
#    from pprint import pprint as pp
#    pp(result)
#    assert True


def test_pynxos_attributes(mock_pynxos_device):
    pynxos_device = mock_pynxos_device
    assert pynxos_device.host == "nxos1.fake.com"
    assert pynxos_device.username == "admin"
    assert pynxos_device.password == "foo"
    assert pynxos_device.port == 8443
    assert pynxos_device.transport == "https"
    assert pynxos_device.api_format == "jsonrpc"
    assert pynxos_device.verify == False


def test_build_payload(mock_pynxos_device):
    """
    Payload format should be as follows:
    [
        {
            'id': 1,
            'jsonrpc': '2.0',
            'method': 'cli',
            'params': {'cmd': 'show hostname', 'version': 1.0}
        }
    ]
    """
    mock_device = mock_pynxos_device
    payload = mock_device.api._build_payload(["show hostname"], method="cli")
    payload = json.loads(payload)
    assert isinstance(payload, list)
    payload_dict = payload[0]
    assert payload_dict["id"] == 1
    assert payload_dict["jsonrpc"] == "2.0"
    assert payload_dict["method"] == "cli"
    assert payload_dict["params"]["cmd"] == "show hostname"
    assert payload_dict["params"]["version"] == 1.0


def test_build_payload_xml(mock_pynxos_device_xml):
    """
    Payload format should be as follows:
    <?xml version="1.0"?>
    <ins_api>
      <version>1.2</version>
      <type>cli_show</type>
      <chunk>0</chunk>
      <sid>sid</sid>
      <input>show hostname</input>
      <output_format>xml</output_format>
    </ins_api>
    """
    mock_device = mock_pynxos_device_xml
    payload = mock_device.api._build_payload(["show hostname"], method="cli_show")
    xml_root = etree.fromstring(payload)
    assert xml_root.tag == "ins_api"
    version = xml_root.find("./version")
    api_method = xml_root.find("./type")
    sid = xml_root.find("./sid")
    api_cmd = xml_root.find("./input")
    output_format = xml_root.find("./output_format")
    assert version.tag == "version"
    assert version.text == "1.0"
    assert api_method.tag == "type"
    assert api_method.text == "cli_show"
    assert sid.tag == "sid"
    assert sid.text == "sid"
    assert api_cmd.tag == "input"
    assert api_cmd.text == "show hostname"
    assert output_format.tag == "output_format"
    assert output_format.text == "xml"


def test_show_hostname(mock_pynxos_device):
    result = mock_pynxos_device.show("show hostname")
    assert result["hostname"] == "nxos.domain.com"


def test_show_version(mock_pynxos_device):
    result = mock_pynxos_device.show("show version")
    assert result["chassis_id"] == "NX-OSv Chassis"
    assert result["memory"] == 4002196
    assert result["proc_board_id"] == "TM6012EC74B"
    assert result["sys_ver_str"] == "7.3(1)D1(1) [build 7.3(1)D1(0.10)]"


# def test_show_ip_int_brief(mock_pynxos_device):
#    result = mock_pynxos_device.show("show ip int brief vrf management")
#    assert result["TABLE_intf"]["ROW_intf"]["prefix"] == "10.0.0.71"
#    assert result["TABLE_vrf"]["ROW_vrf"]["vrf-name-out"] == "management"
