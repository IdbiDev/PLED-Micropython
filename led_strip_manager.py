from led_strip import LedStrip


class LedStripManager:
    def __init__(self, max_state_machine: int):
        self.led_strips = {}
        self.led_strips_slot = {i: False for i in range(max_state_machine)}
        self.max_state_machine = max_state_machine

    def get_free_slot(self):
        for k, v in self.led_strips_slot.items():
            if not v:
                return k
        return None

    def remove_strip(self, id):
        self.led_strips.pop(id)
        self.led_strips_slot[id] = False

    def register_strip(self, strip_type, pin, name, led_count, animation_id, animation_speed, power, color: tuple[int, int, int, float]):
        free_id = self.get_free_slot()
        if free_id is None:
            return None

        strip = LedStrip(strip_type, free_id, pin, name, led_count, animation_id, animation_speed, power, color)
        self.led_strips[strip.id] = strip
        self.led_strips_slot[strip.id] = True
        return strip
