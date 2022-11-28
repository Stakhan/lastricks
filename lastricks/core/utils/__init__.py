from datetime import datetime
class Timer:
    def __init__(self):
        self.start_time = datetime.now()
    def __str__(self):
        return str(datetime.now()-self.start_time)