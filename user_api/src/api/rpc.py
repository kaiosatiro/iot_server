from typing import Annotated

from asgi_correlation_id import correlation_id
from fastapi import Depends

from src.queue.channels import RpcChannel


class RpcHandler:
    def __init__(self) -> None:
        self.rpc: RpcChannel = RpcChannel()

    def add_device_handler_cache(self, device_id: int) -> bool:
        response = self.rpc.publish(
            {"device_id": device_id, "method": "add"},
            correlation_id=correlation_id.get() or "",
        )
        if response:
            return True
        return False

    def remove_device_handler_cache(self, device_id: int) -> bool:
        response = self.rpc.publish(
            {"device_id": device_id, "method": "remove"},
            correlation_id=correlation_id.get() or "",
        )
        if response:
            return True
        return False


rpcCall = Annotated[RpcHandler, Depends(RpcHandler)]
