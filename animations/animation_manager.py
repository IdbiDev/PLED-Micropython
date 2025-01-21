import solid_animation
import wave_animation
from animations import reversed_wave_animation, bounce_wave_animation

"""
0 solid
1 wave
2 reversed wave
3 bounce wave
4 rainbow
"""

class AnimationManager:
    def __init__(self):
        self.animations = {
            0: solid_animation.SolidAnimation(),
            1: wave_animation.WaveAnimation(),
            2: reversed_wave_animation.ReversedWaveAnimation(),
            3: bounce_wave_animation.BounceWaveAnimation()
        }