from fiscal_service.CheckSum import CheckSum
from fiscal_service.Enums import ErrorCode


class ResponseParser:
	def __init__(self):
		self.startBytes = bytearray.fromhex("B6 29")

	def parse(self, answer):
		if not answer.startswith(self.startBytes):
			raise Exception("Неверный формат ответа")
		checker = CheckSum()
		answer = answer[2:]
		crc = checker.crc(answer[:-2])
		if crc != answer[-2:]:
			raise Exception("Не сходится контрольная сумма")
		answer = answer[:-2]
		if answer[0]:
			error = ErrorCode(int.from_bytes(answer[0], 'big'))
			raise Exception(error.description)
		answer = answer[1:]
		return answer


def parse(answer):
	parser = ResponseParser()
	return parser.parse(answer)
