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

    def has_new_frame(self):
        self.output_mux.check_new_frame()
        return self._new_frame

    @property
    def source_width(self):
        return self.capture_source_mux.width

    @source_width.setter
    def source_width(self, val: int) -> None:
        self.capture_source_mux.width = val

    @property
    def source_height(self):
        return self.capture_source_mux.height

    @source_height.setter
    def source_height(self, val: int) -> None:
        self.capture_source_mux.height = val

    @property
    def source_exposure(self):
        return self.capture_source_mux.exposure

    @source_exposure.setter
    def source_exposure(self, val: int) -> None:
        self.capture_source_mux.exposure = val

