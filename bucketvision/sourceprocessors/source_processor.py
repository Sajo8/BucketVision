from bucketvision import Frame


class SourceProcessor:
    """
    This is a base class for the resize and overlay source processors we have
    """

    def __init__(self) -> None:
        pass

    def process_frame(self, frame: Frame) -> Frame:
        raise NotImplementedError("Subclasses of SourceProcessor must implement process_frame() method")
