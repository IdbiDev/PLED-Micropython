import json
import time
import _thread

from animations.animation_manager import AnimationManager
from connection.packet_manager import PacketManager

from connection.packet_manager import PacketType
from data.data_manager import DataManager
from led_strip_manager import LedStripManager

packet_manager = PacketManager()
led_strip_manager = LedStripManager(8)
data_manager = DataManager(led_strip_manager)
animation_manager = AnimationManager()


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


idle_thread = _thread.start_new_thread(animation_thread, ())

while True:
    try:
        # Packet processing...
        packet_data = packet_manager.process()  # {"id": 1, "data": "ready"}
        if packet_data is None:
            continue

        packet_id: int = packet_data["id"]
        data: str = packet_data["data"]

        if packet_id == PacketType.TEST_CONNECTION.value:  # create connection
            if data.startswith("led_controller"):
                packet_manager.complete()
            else:
                packet_manager.complete_error("connection_failed!")
            continue

        if packet_id == PacketType.UPDATE_LED_STRIP_POWER.value:  # data: {strip_id: True}
            data: dict = eval(data)
            for i in data.keys():
                led_strip_manager.led_strips[i].power = data[i]
                led_strip_manager.led_strips[i].fill((0, 0, 0, 1))
                led_strip_manager.led_strips[i].show_pixels()

        elif packet_id == PacketType.UPDATE_LED_STRIP_FILL_COLOR.value:  # data: {strip_id: (rgba
            data: dict = eval(data)
            for i in data.keys():
                led_strip_manager.led_strips[i].fill(data[i])
                led_strip_manager.led_strips[i].show_pixels()

        elif packet_id == PacketType.UPDATE_LED_STRIP_PER_LED_COLOR.value:  # data: {strip_id:{led_id:rgba,...},strip_id:{led_id:rgba,...},...}
            data: dict = eval(data)
            for strip_id, color_data in data.items():
                led_strip = led_strip_manager.led_strips[strip_id]
                for led_id, color in color_data.items():
                    led_strip.set_pixel_color(led_id, color)
                led_strip.show_pixels()

        elif packet_id == PacketType.UPDATE_LED_STRIP_PROPERTIES.value:  # data: {strip_id:{"animation":0..},..}
            data: dict = eval(data)
            for strip_id, setting_data in data.items():
                led_strip = led_strip_manager.led_strips[strip_id]
                for setting_name, setting_value in setting_data.items():
                    setattr(led_strip, setting_name, setting_value)
                led_strip.refresh_led_strip()
            data_manager.save()

        elif packet_id == PacketType.HOST_REQUEST_SETTINGS.value:  # data: Empty
            # Pack up the settings
            packet_manager.send_data(PacketType.CONTROLLER_SEND_SETTINGS, data_manager.get_data())
            # Delay for processing time
            time.sleep(1)

        elif packet_id == PacketType.HOST_SEND_SETTINGS.value:  # data: json formatted thing {"led_strips": [{"type": "ws2815", ...}]}
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
