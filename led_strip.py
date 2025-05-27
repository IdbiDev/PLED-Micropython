import array
from counter import Counter
import rp2
from machine import Pin


@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2815():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1).side(0)[T3 - 1]
    jmp(not_x, "do_zero").side(1)[T1 - 1]
    jmp("bitloop").side(1)[T2 - 1]
    label("do_zero")
    nop().side(0)[T2 - 1]
    wrap()


class LedStrip:
    # sound - C#-ből kapja a dict datat
    def __init__(self, strip_type, id, pin, name, led_count, animation_id, animation_speed, power, color: tuple[int, int, int, int]):
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
        self.animation_progress_data = {} # {"counter": 0, "up": 0}

        # Todo: Pico specific things
        self.brightness_levels = [0.05 for _ in range(self.led_count)]
        self.dimmer_ar = array.array("I", [0 for _ in range(self.led_count)])

        self.sm = rp2.StateMachine(id, ws2815, freq=8_000_000, sideset_base=Pin(self.pin))

        self.sm.active(1)

    def refresh_led_strip(self):
        self.fill((0, 0, 0, 1))
        self.show_pixels(True)
        self.brightness_levels = [0.05 for _ in range(self.led_count)]
        self.dimmer_ar = array.array("I", [0 for _ in range(self.led_count)])
        self.animation_progress_data = {}
        self.counter = Counter(self.animation_speed)

    def is_sound_visualize(self):
        return self.animation_id == -1

    def fill(self, color):
        for i in range(self.led_count):
            self.set_pixel_color(i, color)

    def set_pixel_color(self, pixel, color):
        # Todo: RGB OR GRB... This is GRB
        temp = (color[1] << 16) + (color[0] << 8) + color[2]
        self.brightness_levels[pixel] = color[3] / 255  # Set individual brightness
        r = int(((temp >> 8) & 0xFF) * color[3] / 255)
        g = int(((temp >> 16) & 0xFF) * color[3] / 255)
        b = int((temp & 0xFF) * color[3] / 255)
        self.dimmer_ar[pixel] = (g << 16) + (r << 8) + b

    def show_pixels(self, force = False):
        if self.power or force:
            self.sm.put(self.dimmer_ar, 8)
