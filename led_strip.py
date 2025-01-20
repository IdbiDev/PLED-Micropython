import array
from counter import Counter


class LedStrip:
    # sound - C#-ből kapja a dict datat
    def __init__(self, strip_type, id, pin, name, led_count, animation_id, animation_speed, power, color: tuple[int, int, int, float]):
        self.strip_type = strip_type
        self.id = id
        self.pin = pin
        self.name = name
        self.led_count = led_count
        self.animation_id = animation_id
        self.animation_speed = animation_speed
        self.power = power
        self.color = color
        self.counter = Counter(animation_speed)
        self.animation_progress = {}

        # Todo: Pico specific things
        self.brightness_levels = [0.05 for _ in range(self.led_count)]
        self.dimmer_ar = array.array("I", [0 for _ in range(self.led_count)])

    def is_sound_visualize(self):
        return self.animation_id == -1

    def fill(self, color):
        pass

    def set_pixel_color(self, pixel, color):
        pass

    def show_pixels(self):
        pass
