from a2y_inst import mvsdk
import numpy as _np


class CameraEnumerator:
	def __init__(self, max_count=1):
		self._camera_infos = mvsdk.CameraEnumerateDevice(max_count)

	def __getitem__(self, item):
		return self._camera_infos[item]

	def __len__(self):
		return len(self._camera_infos)


class Camera:
	def __init__(self, name):
		camera = mvsdk.CameraInitEx2(name)
		cap = mvsdk.CameraGetCapability(camera)
		monoCamera = (cap.sIspCapacity.bMonoSensor != 0)
		if monoCamera:
			mvsdk.CameraSetIspOutFormat(camera, mvsdk.CAMERA_MEDIA_TYPE_MONO8)
		mvsdk.CameraSetTriggerMode(camera, 0)
		mvsdk.CameraPlay(camera)
		FrameBufferSize = cap.sResolutionRange.iWidthMax * cap.sResolutionRange.iHeightMax * (1 if monoCamera else 3)
		frame_buffer = mvsdk.CameraAlignMalloc(FrameBufferSize, 16)

		self._camera_handle = camera
		self._frame_buffer = frame_buffer

	def __del__(self):
		self.close()

	def set_exposure_time(self, time_ms):
		mvsdk.CameraSetExposureTime(self._camera_handle, time_ms*1000)

	def get_exposure_time(self):
		time_us = mvsdk.CameraGetExposureTime(self._camera_handle)
		return int(time_us / 1000)

	def start_play(self):
		mvsdk.CameraPlay(self._camera_handle)

	def pause_play(self):
		mvsdk.CameraPause(self._camera_handle)

	def stop_play(self):
		mvsdk.CameraStop(self._camera_handle)

	def close(self):
		if hasattr(self, '_camera_handle'):
			mvsdk.CameraUnInit(self._camera_handle)
			delattr(self, '_camera_handle')

	def _snap(self, timeout):
		camera = self._camera_handle
		frame_buffer = self._frame_buffer
		pRawData, FrameHead = mvsdk.CameraGetImageBuffer(camera, timeout)
		mvsdk.CameraImageProcess(camera, pRawData, frame_buffer, FrameHead)
		mvsdk.CameraReleaseImageBuffer(camera, pRawData)
		frame_data = (mvsdk.c_ubyte * FrameHead.uBytes).from_address(frame_buffer)
		frame = _np.frombuffer(frame_data, dtype=_np.uint8)
		frame = frame.reshape((FrameHead.iHeight, FrameHead.iWidth, 1 if FrameHead.uiMediaType == mvsdk.CAMERA_MEDIA_TYPE_MONO8 else 3))
		return frame

	def snap(self, timeout: int = 1000, retry_count: int = 0):
		frame: _np.ndarray = None
		try_count = 0
		exception: Exception = None
		while try_count <= retry_count:
			try:
				frame = self._snap(timeout)
			except mvsdk.CameraException as e:
				exception = e
				try_count += 1
			else:
				break
		if frame is None:
			raise exception
		return frame

	def apply_configure_from_file(self, filename: str):
		mvsdk.CameraReadParameterFromFile(self._camera_handle, filename)
