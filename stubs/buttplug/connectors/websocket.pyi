from ..errors import (
    ConnectorError as ConnectorError,
    DisconnectedError as DisconnectedError,
    InvalidAddressError as InvalidAddressError,
    InvalidHandshakeError as InvalidHandshakeError,
    ServerNotFoundError as ServerNotFoundError,
    WebsocketTimeoutError as WebsocketTimeoutError,
)
from .abstract import Connector as Connector
from websockets import WebSocketClientProtocol as WebSocketClientProtocol

class WebsocketConnector(Connector):
    def __init__(self, address: str, *args, **kwargs) -> None: ...
    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...
    async def send(self, message: str) -> None: ...
