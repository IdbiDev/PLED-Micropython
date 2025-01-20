import animation

class SolidAnimation(animation.Animation):
    def __init__(self):
        super().__init__(0)

    def get_color(self, led_strip) -> dict[int, tuple[int, int, int, float]]:
        return led_strip.color

