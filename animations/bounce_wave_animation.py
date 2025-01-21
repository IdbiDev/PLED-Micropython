import animation


class BounceWaveAnimation(animation.Animation):
    def __init__(self):
        super().__init__(3)
        self.length = 4

    def get_colors(self, led_strip):
        counter = led_strip.animation_progress.get("counter", 0)
        up = led_strip.animation_progress.get("up", 1)
        last_led = led_strip.led_count - 1

        led_colors2 = self.__get_colors(led_strip, up)

        if counter > 0:
            if up == 1:
                led_colors2[counter - 1] = (0, 0, 0, 0)
            else:
                led_colors2[last_led - counter + 1] = (0, 0, 0, 0)
        else:
            if up == 1:
                led_colors2[counter + self.length] = (0, 0, 0, 0)
            else:
                led_colors2[last_led - self.length] = (0, 0, 0, 0)

        led_strip.animation_progress["counter"] = counter + 1
        if counter + self.length >= led_strip.led_count:
            if up == 1:
                led_strip.animation_progress["up"] = 0
            else:
                led_strip.animation_progress["up"] = 1
            self.counter = 0

        return led_colors2


    def __get_colors(self, led_strip, up):
        led_colors = {}

        counter = led_strip.animation_progress.get("counter", 0)
        last_led = led_strip.led_count - 1

        for i in range(counter, counter + self.length):
            if up:
                if i >= led_strip.led_count:
                    break
                led_index = i
            else:
                if last_led - i < 0:
                    break
                led_index = last_led - i

            if counter + self.length >= led_strip.led_count:
                led_strip.animation_progress["counter"] = 0

            led_colors[led_index] = led_strip.color

        return led_colors