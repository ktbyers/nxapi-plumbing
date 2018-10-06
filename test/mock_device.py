from __future__ import unicode_literals
from builtins import super
from pynxos import Device
from pynxos.lib.rpc_client import RPCClient


class MockDevice(Device):
    def __init__(
        self,
        host,
        username,
        password,
        transport="http",
        encoding="rpc",
        port=None,
        timeout=30,
        verify=True,
    ):
        super().__init__(
            host,
            username,
            password,
            transport=transport,
            encoding=encoding,
            port=port,
            timeout=timeout,
            verify=verify,
        )
        self.rpc = MockRPCClient(
            host, username, password, transport=transport, port=port, verify=verify
        )


class MockRPCClient(RPCClient):
    pass
