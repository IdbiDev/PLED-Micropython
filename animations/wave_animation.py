import animation


class WaveAnimation(animation.Animation):
    def __init__(self):
        super().__init__(1)
        self.length = 4

    def get_colors(self, led_strip) -> dict[int, tuple[int, int, int, float]]:
        led_colors = {}

        counter = led_strip.animation_progress[self.id]

        if counter > 0:
            led_colors[counter - 1] = (0, 0, 0, 0)

        for i in range(counter, counter + self.length):
            led_index = (i - led_strip.led_count if i >= led_strip.led_count else i)

            led_colors[led_index] = led_strip.color

            if counter >= led_strip.led_count:
                led_strip.animation_progress[self.id] = 0

        led_strip.animation_progress[self.id] += 1
        return led_colors
