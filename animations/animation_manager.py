import solid_animation
import wave_animation

class AnimationManager:
    def __init__(self):
        self.animations = {
            0: solid_animation.SolidAnimation(),
            1: wave_animation.WaveAnimation()
        }