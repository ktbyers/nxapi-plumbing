from __future__ import print_function
from __future__ import unicode_literals
import time


def test_obj_attributes(pynxos_device):
    #    assert pynxos_device.host == 'nxos1.fake.com'
    #    assert pynxos_device.username == 'admin'
    #    assert pynxos_device.password == 'foo'
    #    assert pynxos_device.port == 8443
    #    assert pynxos_device.transport == 'https'
    #    assert pynxos_device.encoding == 'rpc'
    #    assert pynxos_device.timeout == 60
    #    assert pynxos_device.verify == False

    print(pynxos_device.show("show hostname"))
    assert True
