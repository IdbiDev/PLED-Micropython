class Counter:
    def __init__(self, base_speed: int = 100):
        self.counter = 0
        self.last_run = 0
        self.running = False
        self.speed = base_speed

    def get_count(self):
        self.speed = max(1, self.speed)
        return int(self.counter / self.speed)

    def add(self) -> bool:
        if self.counter == 0:
            self.counter += 1
            return True

        if self.last_run + 1 == self.get_count():
            self.last_run = self.get_count()
            self.counter += 1
            return True

        self.counter += 1
        return False
