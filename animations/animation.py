class Animation:
    def __init__(self, id):
        self.id = id


    def is_fill(self):
        return self.id == 0


    def get_color(self, led_strip):
        pass


    def get_colors(self, led_strip):
        pass