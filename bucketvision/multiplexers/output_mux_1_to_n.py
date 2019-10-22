from typing import List

from bucketvision.multiplexers.capture_source_mux import CaptureSourceMux
from bucketvision.sourceprocessors.delegated_source import DelegatedSource


class OutputMux1toN:
    """
    This multiplexer takes a series of input sources and creates one
    output source
    """

    def __init__(self, capture_source_mux: CaptureSourceMux):
        self.capture_source_mux = capture_source_mux
        self.outputs: List[DelegatedSource] = []

    def check_new_frame(self):
        if self.capture_source_mux.has_new_frame():
            self.capture_source_mux.set_new_frame(False)
            for output in self.outputs:
                output._new_frame = True

    def create_output(self) -> DelegatedSource:
        output = DelegatedSource(self, self.capture_source_mux)
        self.outputs.append(output)
        return output
