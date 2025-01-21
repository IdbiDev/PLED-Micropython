import animation


class ReversedWaveAnimation(animation.Animation):
    def __init__(self):
        super().__init__(2)
        self.length = 4

    def get_colors(self, led_strip) -> dict[int, tuple[int, int, int, float]]:
        led_colors = {}

        last_led = led_strip.led_count - 1
        color = led_strip.color
        counter = led_strip.animation_progress.get("counter", 0)

        if counter > 0:
            led_colors[last_led - counter + 1] = (0, 0, 0, 0)

        for i in range(counter, counter + self.length):
            led_index = last_led - i
            if led_index < 0:
                led_index = last_led + (led_index + 1)

            led_colors[led_index] = color

            if counter >= led_strip.led_count:
                led_strip.animation_progress["counter"] = 0

        led_strip.animation_progress["counter"] = counter + 1
        return led_colors
