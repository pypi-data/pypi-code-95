import win32com.client


class RUDAT:
	def __init__(self):
		self.__handle = win32com.client.Dispatch("mcl_RUDAT.USB_DAT")
		assert self.__handle is not None

	def connect(self, sn: str = ''):
		"""
		在执行读取、写入配置参数前，需要连接仪器。
		:param sn: 要连接仪器的设备序列号。如果系统只连接着一个仪器，可以传入空字符串（不是None）。
		:return: No return value. 如果连接失败，将抛出 IOError 异常。
		"""
		ret = self.__handle.Connect(sn)
		if ret != 1:
			raise IOError('Connect to RUDAT failed.')

	def disconnect(self):
		"""
		断开与仪器的连接。
		:return: No return value.
		"""
		self.__handle.Disconnect()

	def get(self) -> float:
		"""
		读取衰减器的当前衰减配置值。如果读取失败，将抛出 IOError 异常。
		:return: 当前配置值，浮点数。
		"""
		_value = 0.0
		ret, value = self.__handle.Read_Att(_value)
		if ret != 1:
			raise IOError('get attenuate setting failed.')
		return value

	def set(self, value: float):
		"""
		设置衰减器的衰减值。
		:param value: 目标设置值。
		:return: 如果成功，无返回值；如果与仪器通信失败，抛出 IOError 异常；如果目标设置值超出可设置范围，抛出 ValueError 异常。
		"""
		ret, _value = self.__handle.SetAttenuation(value)
		if ret == 2:
			raise ValueError('attenuate value overflow.')
		if ret != 1:
			raise IOError('set attenuate value failed.')

	@property
	def native_handle(self):
		"""
		获取控制仪器的句柄。当封装的函数无法满足需要的时候，可以通过此句柄调用底层接口。
		:return: 仪器控制句柄，一个 Windows COM 对象。
		"""
		return self.__handle
