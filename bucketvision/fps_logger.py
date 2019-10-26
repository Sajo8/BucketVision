import time


class FPSLogger:
    """A simple utilty to log fps"""
    def __init__(self, name: str, log_at_frames=30):
        self.name = name
        self.log_at_frames = log_at_frames

        self.num_frames = 0
        self.total_frames = 0
        self.last_frame_time = time.time()

    def log_frame(self):
        self.num_frames += 1
        self.total_frames += 1

        if self.num_frames >= self.log_at_frames:
            duration = time.time() - self.last_frame_time
            fps = self.num_frames / duration
            print(f"{self.name:<30} {fps:.1f}fps")
            self.num_frames = 0
            self.last_frame_time = time.time()
