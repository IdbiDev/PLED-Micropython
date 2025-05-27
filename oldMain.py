import json
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
# id   strip   value
# 0x6 | 0x0 | 0xRRGGBBAA

# UPDATE_LED_STRIP_PER_LED_COLOR
#  id    strip  count   pixelid, color
# 0x8 | (0x0 | 0xFFFF | 0xFFFF, 0xRRGGBBAA), (0x1 | 0xFAFF, 0xFFFF, 0xRRGGBBAA)

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

        packet_id: int = packet_data["id"]
        data: str = packet_data["data"]

        if packet_id == TEST_CONNECTION:  # create connection
            if data.startswith("led_controller"):
                packet_manager.complete()
            else:
                packet_manager.complete_error("connection_failed!")
            continue

        if packet_id == UPDATE_LED_STRIP_POWER:  # data: {strip_id: True} -> 0x0 0x
            data: dict = eval(data)
            for i in data.keys():
                led_strip_manager.led_strips[i].power = data[i]
                led_strip_manager.led_strips[i].fill((0, 0, 0, 1))
                led_strip_manager.led_strips[i].show_pixels()

        elif packet_id == UPDATE_LED_STRIP_FILL_COLOR:  # data: {strip_id: (rgba
            data: dict = eval(data)
            for i in data.keys():
                led_strip_manager.led_strips[i].fill(data[i])
                led_strip_manager.led_strips[i].show_pixels()

        elif packet_id == UPDATE_LED_STRIP_PER_LED_COLOR:  # data: {strip_id:{led_id:rgba,...},strip_id:{led_id:rgba,...},...}
            data: dict = eval(data)
            for strip_id, color_data in data.items():
                led_strip = led_strip_manager.led_strips[strip_id]
                for led_id, color in color_data.items():
                    led_strip.set_pixel_color(led_id, color)
                led_strip.show_pixels()

        elif packet_id == UPDATE_LED_STRIP_PROPERTIES:  # data: {strip_id:{"animation":0..},..}
            data: dict = eval(data)
            for strip_id, setting_data in data.items():
                led_strip = led_strip_manager.led_strips[strip_id]
                for setting_name, setting_value in setting_data.items():
                    setattr(led_strip, setting_name, setting_value)
                led_strip.refresh_led_strip()
            data_manager.save()

        elif packet_id == HOST_REQUEST_SETTINGS:  # data: Empty
            # Pack up the settings
            packet_manager.send_data(CONTROLLER_SEND_SETTINGS, data_manager.get_data())
            # Delay for processing time
            time.sleep(1)

        elif packet_id == HOST_SEND_SETTINGS:  # data: json formatted thing {"# ": [{"type": "ws2815", ...}]}
            data: dict = json.loads(data)
            led_strip_manager.led_strips.clear()
            led_strip_manager.current_state_machine = 0
            for led_strip_data in data["led_strips"]:
                led_strip_manager.register_strip(
                    led_strip_data["type"],
                    led_strip_data["pin"],
                    led_strip_data["name"],
                    led_strip_data["led_count"],
                    led_strip_data["animation_id"],
                    led_strip_data["animation_speed"],
                    led_strip_data["power"],
                    led_strip_data["color"]
                )
            data_manager.save()

        packet_manager.complete()
    except Exception as e:
        packet_manager.complete_error(str(e))

