""""
Ответы от ККТ
Любая структура, возвращаемая кассой в ответ на запрос является наследником класса TerminalAnswer
"""
import struct
from datetime import datetime




# noinspection PyBroadException
from fiscal_service.Enums import BinaryTypes, TerminalFAPrinterStatus


class TerminalAnswer:
	def getNext(self, fmt: BinaryTypes = BinaryTypes.BYTE, size=0):
		if size == 0:
			size = fmt.size
		if size == 0:
			raise Exception("Не указан размер байтовой строки для чтения")
		res = self.data[self.pos: self.pos + size]
		self.pos += size

		if fmt == BinaryTypes.BYTE:
			return struct.unpack('b', res)[0]
		if fmt == BinaryTypes.UBYTE:
			return struct.unpack('B', res)[0]
		if fmt == BinaryTypes.INT32:
			return struct.unpack("i", res)[0]
		if fmt == BinaryTypes.UINT32:
			return struct.unpack('I', res)[0]
		if fmt == BinaryTypes.INT64:
			return struct.unpack('l', res)[0]
		if fmt == BinaryTypes.UINT64:
			return struct.unpack('L', res)[0]
		if fmt == BinaryTypes.STRING:
			return res.decode('utf-8')
		if fmt == BinaryTypes.DATETIME:
			year, month, day, hour, minute = struct.unpack("bbbbb", res)
			try:
				return datetime(year + 2000, month, day, hour, minute).isoformat()
			except:
				return datetime.min

	def __init__(self, data):  # конструктор принимает двоичные данные, полученные от ККТ
		self.pos = 2  # в первых двух байтах ответа ничего интересного
		self.data = data


class TerminalStatus(TerminalAnswer):
	"""
	Статус ККТ
	"""

	def __init__(self, data):
		super().__init__(data)
		self.factoryNum = self.getNext(BinaryTypes.STRING, 12)
		self.DateTime = self.getNext(BinaryTypes.DATETIME)
		ans = self.getNext()
		self.FatalErrors = (ans != 0)
		self.PrinterStatus = TerminalFAPrinterStatus(self.getNext())
		self.hasFN = (self.getNext() != 0)
		self.phaseFN = self.getNext()


class FiscalStorageStatus(TerminalAnswer):
	"""
	Статус фискального накопителя
	"""

	def __init__(self, data):
		super().__init__(data)
		self.phaseFN = self.getNext()
		self.CurrentDocument = self.getNext()
		self.hadDocData = self.getNext()
		self.SessionIsOpen = (self.getNext() != 0)
		self.Warnings = self.getNext()  # TODO обработку предупреждений
		year = self.getNext()
		month = self.getNext()
		day = self.getNext()
		hour = self.getNext()
		minute = self.getNext()
		if year != 0:
			self.DateTimeLastDocument = \
				datetime(year+2000, month, day, hour, minute).isoformat()
		else:
			self.DateTimeLastDocument = None
		self.StorageNumber = self.getNext(BinaryTypes.STRING, 16)
		self.qty = self.getNext()


class RegStatus(TerminalAnswer):
	"""
	Параметры регистрации ККТ
	"""

	def __init__(self, data):
		super().__init__(data)
		try:
			self.regNum = self.getNext(BinaryTypes.STRING, 20)
			self.inn = self.getNext(BinaryTypes.STRING, 12).strip()
		except:
			self.regNum = ''
			self.inn = ''


class FiscalDocument(TerminalAnswer):
	"""Фискальный документ по номеру"""

	def __init__(self, data):
		super().__init__(data)
		self.docType = self.getNext()
		self.isSent = self.getNext() != 0
		self.dateTime = self.getNext(BinaryTypes.DATETIME)
		if self.docType == 3:
			self.docNum = self.getNext(BinaryTypes.UINT32)
			self.fiscalSign = self.getNext(BinaryTypes.UINT32)

