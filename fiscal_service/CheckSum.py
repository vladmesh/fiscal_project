class CheckSum:

	def __init__(self):
		self.POLYNOMIAL = 0x1021
		self._tab = [self._initial(i) for i in range(256)]
		self.PRESET = 0xffff

	def _initial(self, c):
		crc = 0
		c = c << 8
		for j in range(8):
			if (crc ^ c) & 0x8000:
				crc = (crc << 1) ^ self.POLYNOMIAL
			else:
				crc = crc << 1
			c = c << 1
		return crc

	def _update_crc(self, crc, c):
		cc = 0xff & c

		tmp = (crc >> 8) ^ cc
		crc = (crc << 8) ^ self._tab[tmp & 0xff]
		crc = crc & 0xffff
		print(crc)

		return crc

	def crc(self, array):
		crc = self.PRESET
		for c in array:
			crc = self._update_crc(crc, c)
		return crc.to_bytes(2, 'little')

	def crcb(self, *i):
		crc = self.PRESET
		for c in i:
			crc = self._update_crc(crc, c)
		return crc
