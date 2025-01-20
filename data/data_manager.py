import json


class DataManager:
    def __init__(self, led_strip_manager):
        self.led_strip_manager = led_strip_manager

    def get_data(self):
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
            f.write(json.dumps(self.get_data()))

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
