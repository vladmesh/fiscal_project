import enum


class ErrorCode(enum.Enum):
	def __init__(self, val, description=""):
		self.val = val
		self.description = description

	OK = (0, "OK")
	WrongFormat = (0x01, "Неверный формат")
	WrongState = 0x02
	FiscalStorageError = 0x03
	CryptoprocessorError = 0x04
	FiscalStorageLifeTime = 0x05
	ArchiveIsFull = 0x06
	WrongTime = 0x07
	NoData = 0x08
	ParametersWrongFormat = 0x09
	TLVDataExceeding = 0x10
	CryptoprocessorResourceExhausted = 0x12
	OFDResourceExhausted = 0x14
	WaitingTimeExceeded = 0x15
	Session24 = 0x16
	WrongTimeDifference = 0x17
	MessageCanNotBeAccepted = 0x20
	WrongCommand = 0x25
	UnknownCommand = 0x26
	WrongLength = 0x27
	WrongParametersFormat = 0x28
	FiscalStorageNoConnect = 0x30
	WrongDateTime = 0x31
	NotFullData = 0x32
	WrongRN = 0x33
	AlreadyTransferred = 0x34
	HardwareError = 0x35
	WrongCalculationSign = 0x36
	WrongTax = 0x37
	DataForAgentOnly = 0x38
	WrongSum = 0x39
	WrongStatePrinter = 0x40
	SavingSettingsError = 0x50
	WrongTimeValue = 0x51
	OtherCalculationSubject = 0x52
	FewDataForAgent = 0x53
	WrongSum2 = 0x54
	WrongCalculationSignCorrection = 0x55
	WrongDataForAgent = 0x56
	NoTaxMode = 0x57
	WrongTaxForAgent = 0x58
	WrongTaxValueSign = 0x59
	WrongBlockFirmware = 0x60
	NotSentDocuments = 0xE0
	WrongRegistrationData = 0xF3
	Timeout = 0xFE
	FnIsNotActive = 0xF4
	UnknownError = 0xFF


class Commands(enum.Enum):
	GET_STATUS = 0x01
	GET_MODEL = 0x04
	GET_FISCAL_STORAGE_STATUS = 0x08
	BEGIN_OPEN_SESSION = 0x21
	OPEN_SESSION = 0x22
	BEGIN_CLOSE_SESSION = 0x29
	CLOSE_SESSION = 0x2A
	BEGIN_RECEIPT = 0x23
	RECEIPT_POSITION = 0x2B
	BEGIN_REGISTRATION = 0x12
	SEND_REGISTRATION_DATA = 0x16
	MAKE_REGISTRATION_REPORT = 0x13
	AGENT_DATA = 0x2C
	PAYMENT_DATA = 0x2D
	MAKE_RECEIPT = 0x24
	GET_DOCUMENT = 0x30
	GET_DOCUMENT_ALL_TAGS = 0x3A
	PRINT = 0x61
	CUT = 0x62
	REGISTRATION_PARAMETERS = 0x0A
	CANCEL_DOCUMENT = 0x10
	RESTART = 0xEF
	BEGIN_CLOSE_FN = 0x14
	CLOSE_FN_DATA = 0x17
	CLOSE_FN_FINISH = 0x15


class TerminalFAPrinterStatus(enum.Enum):
	OK = 0
	NoDevice = 1
	NoPaper = 2
	PaperJammed = 3
	OpenBox = 5
	CutterError = 6
	HardwareError = 7


class BinaryTypes(enum.Enum):
	"""Типы данных, в которые можно превратить последовательность байт"""

	def __init__(self, val, size=0):
		self.val = val
		self.size = size

	INT32 = (0, 4)
	UINT32 = (1, 4)
	INT64 = (2, 8)
	UINT64 = (3, 8)
	BYTE = (4, 1)
	UBYTE = (5, 1)
	DATETIME = (7, 5)
	STRING = 6
