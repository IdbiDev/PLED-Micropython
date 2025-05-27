import json
import struct


class DataManager:
    def __init__(self, led_strip_manager):
        self.led_strip_manager = led_strip_manager

    # id countOfStrips (id, namelength, name, ledcount pinnum ledtype anim  animspeed pwr    color)
    # 0xA | 0xF |   0x1  | nameLength | nameData | 0xFFFF | 0xF   | 0xF    | 0xF | 0xFF    | 0xF | 0xRRGGBBAA |
    def get_data_bytes(self):
        strip_datas = struct.pack("<B", len(self.led_strip_manager.led_strips))
        for strip in self.led_strip_manager.led_strips:
            strip_datas = strip_datas + struct.pack("<BH", strip.id, len(strip.name))
            strip_datas = strip_datas + strip.name.encode('utf-8')
            strip_datas = strip_datas + struct.pack("<HBBBB?H", strip.led_count, strip.pin, strip.type, strip.animation_id, strip.animation_speed, strip.power,
                                                    struct.pack("<BBBB", strip.color[0], strip.color[1], strip.color[2], strip.color[3]))
        return strip_datas

    def get_data_json(self):
        strip_datas = []
        for strip in self.led_strip_manager.led_strips:
            strip_data = {
                "type": strip.type,
                "pin": strip.pin,
                "name": strip.name,
                "led_count": strip.led_count,
                "animation_id": strip.animation_id,
                "animation_speed": strip.animation_speed,
                "power": strip.power,
                "color": list(strip.color),
            }

            strip_datas.append(strip_data)

        return {"led_strips": strip_datas}

    def save(self):
        with open('saves.json', 'w') as f:
            f.seek(0)
            f.write(json.dumps(self.get_data_json()))

    def load(self):
        with open('saves.json', 'r') as f:
            json_data = json.load(f)
            for i in json_data["strips"]:
                self.led_strip_manager.register_strip(
                    i["type"],
                    i["pin"],
                    i["name"],
                    i["led_count"],
                    i["animation_id"],
                    i["animation_speed"],
                    i["power"],
                    i["color"],
                )
