import struct
import sys
from enum import Enum

import select
import json


class PacketType(Enum):
    # PC to controller
    TEST_CONNECTION: int = 0
    UPDATE_LED_STRIP_POWER: int = 2
    UPDATE_LED_STRIP_PROPERTIES: int = 4
    UPDATE_LED_STRIP_FILL_COLOR: int = 6
    UPDATE_LED_STRIP_PER_LED_COLOR: int = 8
    HOST_REQUEST_SETTINGS: int = 10
    HOST_SEND_SETTINGS: int = 12

    # Controller to PC
    READY: int = 1
    ERROR: int = 3
    CONTROLLER_REQUEST_SETTINGS: int = 5
    CONTROLLER_SEND_SETTINGS: int = 7


class PacketManager:
    @staticmethod
    def process() -> dict | None:
        ready, _, _ = select.select([sys.stdin], [], [], 0.00001)
        if not ready:
            return None

        header = sys.stdin.buffer.read(4)
        magic_value, payload_size = struct.unpack("<HH", header)
        if magic_value == 0xABCD:
            data = sys.stdin.buffer.read(payload_size)  # format : {"packet_id": 1, "data":"asdasdddasdasdasddasdasdas"}
            return eval(data.decode("utf-8"))

    @staticmethod
    def send_data(packet, data):
        data = json.dumps(str({"id": packet.value, "data": data})).encode("utf-8")
        sys.stdout.buffer.write(struct.pack("<HH", 0xABCD, len(data)) + data)

    def complete(self):
        self.send_data(PacketType.READY, "ready")

    def complete_error(self, error):
        self.send_data(PacketType.ERROR, error)