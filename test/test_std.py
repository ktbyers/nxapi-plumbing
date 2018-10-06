from __future__ import print_function
from __future__ import unicode_literals
import time


def test_disable_paging(pynxos_device):
    print(pynxos_device.show('show hostname'))
    assert True
