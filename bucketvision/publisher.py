from typing import List, Callable, Optional, Any

from bucketvision import Frame


class Publisher:
    """
    This is a mixin to provide support for publishing updates to a frame
    This is used by the VisionPipeline and the TargetFinder
    """

    def __init__(self):
        # create an empty list of outputs to be called on update
        self.subscribers: List[Callable] = list()

    def add_subscriber(self, callback_function: Callable[[Frame], None]) -> None:
        """
        Register a callback function to be called whenever there is
        a new update
        """
        self.subscribers.append(callback_function)

    def publish_frame_update(self, frame: Frame):
        """
        Publish a new frame to any subscribers of this publisher
        This actually takes a pipeline as a parameter, but we can't
        type it because it would be a circular import
        """
        for on_update_func in self.subscribers:
            on_update_func(frame)


