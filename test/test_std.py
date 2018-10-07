from __future__ import print_function
from __future__ import unicode_literals
import time


# def test_pynxos_real(pynxos_device):
#    print(pynxos_device.show("show version"))
#    assert True


def test_pynxos_attributes(mock_pynxos_device):
    pynxos_device = mock_pynxos_device
    assert pynxos_device.host == "nxos1.fake.com"
    assert pynxos_device.username == "admin"
    assert pynxos_device.password == "foo"
    assert pynxos_device.port == 8443
    assert pynxos_device.transport == "https"
    assert pynxos_device.encoding == "rpc"
    assert pynxos_device.timeout == 60
    assert pynxos_device.verify == False


def test_build_payload(mock_pynxos_device):
    assert True


def test_show_hostname(mock_pynxos_device):
    assert True


def test_show_version(mock_pynxos_device):
    assert True


def test_show_ip_int_brief(mock_pynxos_device):
    assert True
