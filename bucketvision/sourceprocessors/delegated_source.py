from bucketvision.multiplexers.capture_source_mux import CaptureSourceMux


class DelegatedSource:
    """
    The delegated source delegates most properties to a CaptureSourceMux but
    calls back into the OutputMux1toN to check for new frames
    """
    def __init__(self, output_mux, capture_source_mux: CaptureSourceMux) -> None:
        from bucketvision.multiplexers.output_mux_1_to_n import OutputMux1toN
        self.output_mux: OutputMux1toN = output_mux
        self.capture_source_mux = capture_source_mux
        self._new_frame = False

    def next_frame(self):
        self._new_frame = False
        return self.capture_source_mux.next_frame()

    @property
    def width(self):
        return self.capture_source_mux.width

    @width.setter
    def width(self, val: int) -> None:
        self.capture_source_mux.width = val

    @property
    def height(self):
        return self.capture_source_mux.height

    @height.setter
    def height(self, val: int) -> None:
        self.capture_source_mux.height = val

    @property
    def exposure(self):
        return self.capture_source_mux.exposure

    @exposure.setter
    def exposure(self, val: int) -> None:
        self.capture_source_mux.exposure = val

    @property
    def new_frame(self):
        self.output_mux.check_new_frame()
        return self._new_frame
