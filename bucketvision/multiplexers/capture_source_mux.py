from typing import List

from bucketvision.capturers.cv2capture import Cv2Capture


class CaptureSourceMux:
	"""
	This multiplexer takes captures from the camera as sources
	"""
	def __init__(self, capture_sources: List[Cv2Capture]):
		self.sources = capture_sources
		self.source_num = 0

	def has_new_frame(self) -> bool:
		return self.sources[self.source_num].new_frame

	def set_new_frame(self, val: bool) -> None:
		self.sources[self.source_num].new_frame = val

	def next_frame(self):
		return self.sources[self.source_num].next_frame()

	@property
	def width(self):
		return self.sources[self.source_num].width

	@width.setter
	def width(self, val: int) -> None:
		self.sources[self.source_num].width = val

	@property
	def height(self):
		return self.sources[self.source_num].height

	@height.setter
	def height(self, val: int) -> None:
		self.sources[self.source_num].height = val

	@property
	def exposure(self):
		return self.sources[self.source_num].exposure

	@exposure.setter
	def exposure(self, val: int) -> None:
		self.sources[self.source_num].exposure = val

	# def __getattr__(self, name):
	# 	if name in self.__dict__:
	# 		return self.__dict__[name]
	# 	else:
	# 		return getattr(self.sources[self.source_num], name)
	#
	# def __setattr__(self, name, value):
	# 	if name in self.__dict__:
	# 		self.__dict__[name] = value
	# 	else:
	# 		setattr(self.sources[self.source_num], name, value)
