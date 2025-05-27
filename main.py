import json
import struct
import time
import _thread

from animations.animation_manager import AnimationManager
from connection.packet_manager import PacketManager
from data.data_manager import DataManager
from led_strip_manager import LedStripManager

packet_manager = PacketManager()
led_strip_manager = LedStripManager(8)
data_manager = DataManager(led_strip_manager)
animation_manager = AnimationManager()

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
CONTROLLER_SEND_DEBUG_MESSAGE: int = 9

# Header 0xABCD | Payloadsize | 2byte
# Data byte -> packet id
# Fill color
# id      CountofStrips   strip   value
# 0x6 |  0xF| 0x0 | 0xRRGGBBAA

# UPDATE_LED_STRIP_PER_LED_COLOR
#  id countOFStrips    strip  count   pixelid, color
# 0x8 | 0xF | (0x0 | 0xFFFF | 0xFFFF, 0xRRGGBBAA), (0x1 | 0xFAFF, 0xFFFF, 0xRRGGBBAA)

"""
    public string Name
    public int LedCount; 
    public int PinNum;
    public LedType LedType;
    public int Animation;
    public float AnimationSpeed;
    public bool PowerState;
    public Color Color;
"""


# UPDATE_LED_STRIP_PROPERTIES
# id    strip ledcount pinnum ledtype anim  animspeed pwr    color
# 0x4 | 0x5 | 0xFFFF | 0xF   | 0xF    | 0xF | 0xFF    | 0xF | 0xRRGGBBAA |

# HOST_REQUEST_SETTINGS | HOST_SEND_SETTINGS
# id countOfStrips (id, namelength, name, ledcount pinnum ledtype anim  animspeed pwr    color)
# 0xA | 0xF |   0x1  | nameLength | nameData | 0xFFFF | 0xF   | 0xF    | 0xF | 0xFF    | 0xF | 0xRRGGBBAA |

#                      65ezer
def color_to_tuple(rgba_num):
    r, g, b, a = struct.unpack('<BBBB', rgba_num)
    return r, g, b, a


def animation_thread():
    while True:
        for led_strip in led_strip_manager.led_strips:
            if led_strip.is_sound_visualize() or led_strip.power:
                continue

            if not led_strip.counter.add():
                continue

            anim = animation_manager.animations[led_strip.animation_id]
            if anim.is_fill():
                led_strip.fill(anim.get_color())
            else:
                for led_id, color in anim.get_colors().items():
                    led_strip.set_pixel_color(led_id, color)
            led_strip.show_pixels()


#idle_thread = _thread.start_new_thread(animation_thread, ())
print("OK")
while True:
    try:
        # Packet processing...
        packet_data = packet_manager.process()  # {"id": 1, "data": "ready"}
        if packet_data is None:
            continue

        packet_id: int = struct.unpack("<B", packet_data)[0]
        data: bytes = packet_data[1:]

        if packet_id == TEST_CONNECTION:  # create connection
            if data.decode("utf-8").startswith("led_controller"):
                packet_manager.complete()
            else:
                packet_manager.complete_error("connection_failed!")
            continue

        if packet_id == UPDATE_LED_STRIP_POWER:  # data: {strip_id: True} -> 0x0 0x
            strip, power = struct.unpack("<B?", data)

            led_strip_manager.led_strips[strip].power = power
            led_strip_manager.led_strips[strip].fill((0, 0, 0, 1))
            led_strip_manager.led_strips[strip].show_pixels()

        elif packet_id == UPDATE_LED_STRIP_FILL_COLOR:  # data: {strip_id: (rgba
            count = struct.unpack("<B", data)[0]

            for i in range(count):
                strip, rgb = struct.unpack("<BH", data)
                led_strip_manager.led_strips[strip].fill(color_to_tuple(rgb))
                led_strip_manager.led_strips[strip].show_pixels()
                data = data[5:]

        elif packet_id == UPDATE_LED_STRIP_PER_LED_COLOR:  # data: {strip_id:{led_id:rgba,...},strip_id:{led_id:rgba,...},...}
            count = struct.unpack("<B", data)[0]
            # UPDATE_LED_STRIP_PER_LED_COLOR
            #  id countOFStrips    strip  count   pixelid, color
            # 0x8 | 0xF | (0x0 | 0xFFFF | 0xFFFF, 0xRRGGBBAA), (0x1 | 0xFAFF, 0xFFFF, 0xRRGGBBAA)
            for i in range(count):
                strip, led_count = struct.unpack("<BH", data)
                led_strip = led_strip_manager.led_strips[strip]
                data = data[5:]
                for j in range(led_count):
                    pixelID, rgb = struct.unpack("<HH", data)
                    led_strip.set_pixel_color(pixelID, color_to_tuple(rgb))
                    data = data[7:]
                led_strip.show_pixels()

        # UPDATE_LED_STRIP_PROPERTIES
        # id    strip ledcount pinnum ledtype anim  animspeed pwr    color
        # 0x4 | 0x5 | 0xFFFF | 0xF   | 0xF    | 0xF | 0xFF    | 0xF | 0xRRGGBBAA |

        # self.strip_type = strip_type
        # self.pin = pin
        # self.led_count = led_count
        # self.animation_id = animation_id
        # self.animation_speed = animation_speed
        # self.power = power
        # self.color = color
        # self.counter = Counter(animation_speed)
        # self.animation_progress_data = {} # {"counter": 0, "up": 0}

        elif packet_id == UPDATE_LED_STRIP_PROPERTIES:  # data: {strip_id:{"animation":0..},..}
            strip, led_count, pin, strip_type, animation_id, animation_speed, power, color = struct.unpack("<BHBBBB?H", data)
            led_strip = led_strip_manager.led_strips[strip]

            led_strip.strip_type = strip_type
            led_strip.pin = pin
            led_strip.led_count = led_count
            led_strip.animation_id = animation_id
            led_strip.animation_speed = animation_speed
            led_strip.power = power
            led_strip.color = color_to_tuple(color)

            led_strip.refresh_led_strip()
            data_manager.save()

        elif packet_id == HOST_REQUEST_SETTINGS:  # data: Empty
            # Pack up the settings
            packet_manager.send_data(CONTROLLER_SEND_SETTINGS, data_manager.get_data_bytes())
            # Delay for processing time
            time.sleep(1)

        elif packet_id == HOST_SEND_SETTINGS:  # data: json formatted thing {"# ": [{"type": "ws2815", ...}]}

            # HOST_REQUEST_SETTINGS | HOST_SEND_SETTINGS
            # id countOfStrips (id, namelength, name, ledcount pinnum ledtype anim  animspeed pwr    color)
            # 0xA | 0xF |   0x1  | nameLength | nameData | 0xFFFF | 0xF   | 0xF    | 0xF | 0xFF    | 0xF | 0xRRGGBBAA |
            strip_count = struct.unpack("<B", data)[0]
            data = data[1:]
            led_strip_manager.led_strips.clear()
            led_strip_manager.current_state_machine = 0

            for i in range(strip_count):
                id, name_length = struct.unpack("<BH", data)
                data = data[3:]
                name = data[:name_length]
                data = data[name_length:]
                led_count, pin_num, led_type, animation, animation_speed, power, color = struct.unpack("<HBBBB?H", data)
                led_strip_manager.register_strip(
                        led_type,
                        pin_num,
                        name,
                        led_count,
                        animation,
                        animation_speed,
                        power,
                        color_to_tuple(color)
                )
            data_manager.save()

        packet_manager.complete()
    except Exception as e:
        packet_manager.complete_error(str(e))
