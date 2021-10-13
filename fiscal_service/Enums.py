import enum


def get_enum_code_elem_by_code(code):
    for code_elem in ErrorCode:
        if code_elem.code == code:
            return code_elem


class ErrorCode(enum.Enum):
    def __init__(self, code: int, description: str):
        self.code = code
        self.description = description

    OK = (0, "OK")
    WrongFormat = (0x01, "Неверный формат команды")
    WrongState = (0x02, "Данная команда требует другого состояния ФН")
    FiscalStorageError = (0x03, "Ошибка ФН")
    CryptoprocessorError = (0x04, "Ошибка KC")
    FiscalStorageLifeTime = (0x05, "Закончен срок эксплуатации ФН")
    ArchiveIsFull = (0x06, "Архив ФН переполнен")
    WrongTime = (0x07, "Дата и время операции не соответствуют логике работы ФН")
    NoData = (0x08, "Запрошенные данные отсутствуют в Архиве ФН")
    ParametersWrongValue = (0x09, "Параметры команды имеют правильный формат, но их значение не верно")
    TLVDataExceeding = (0x10, "Превышение размеров TLV данных")
    CryptoprocessorResourceExhausted = (0x12, "Исчерпан ресурс КС. Требуется закрытие фискального режима")
    OFDResourceExhausted = (0x14, "Ресурс хранения документов для ОФД исчерпан")
    WaitingTimeExceeded = (0x15, "Превышено время ожидания передачи сообщения (30 дней)")
    Session24 = (0x16, "Продолжительность смены более 24 часов")
    WrongTimeDifference = (0x17, "Неверная разница во времени между 2 операциями (более 5 минут)")
    MessageCanNotBeAccepted = (0x20, "Сообщение от ОФД не может быть принято")
    WrongCommandStructure = (0x25, "Неверная структура команды, либо неверная контрольная сумма")
    UnknownCommand = (0x26, "Неизвестная команда")
    WrongLength = (0x27, "Неверная длина параметров команды")
    WrongParametersFormat = (0x28, "Неверный формат или значение параметров команды")
    FiscalStorageNoConnect = (0x30, "Нет связи с ФН")
    WrongDateTime = (0x31, "Неверные дата/время в ККТ")
    NotFullData = (0x32, "Переданы не все необходимые данные")
    WrongRN = (0x33, "РНМ сформирован неверно, проверка на данной ККТ не прошла")
    AlreadyTransferred = (0x34, "Данные команды уже были переданы ранее.")
    HardwareError = (0x35, "Аппаратный сбой ККТ")
    WrongCalculationSign = (0x36, "Неверно указан признак расчета, возможные значения:"
                                  " приход, расход, возврат прихода, возврат расхода")
    WrongTax = (0x37, "Указанный налог не может быть применен")
    DataForAgentOnly = (0x38, "Команда необходима только для платежного агента")
    WrongSum = (0x39, "Сумма расчета чека не равна сумме значений по чеку")
    SumIsBigger = (0x3A, "Сумма оплаты соответствующими типами (за исключением наличных) превышает итог чека")

    WrongStatePrinter = (0x40, "Некорректный статус печатающего устройства")
    SavingSettingsError = (0x50, "Ошибка сохранения настроек")
    WrongTimeValue = (0x51, "Передано некорректное значение времени")
    OtherCalculationSubject = (0x52, "В чеке не должны присутствовать иные предметы расчета помимо предмета расчета "
                                     "с признаком способа расчета «Оплата кредита»")
    FewDataForAgent = (0x53, "Переданы не все необходимые данные для агента")
    WrongSum2 = (0x54, "Итоговая сумма расчета(в рублях без учета копеек) не "
                       "равна сумме стоимости всех предметов расчета(в рублях без учета копеек)")
    WrongCalculationSignCorrection = (0x55, " Неверно указан признак расчета для чека коррекции, "
                                            "возможные значения: приход, расход")
    WrongDataForAgent = (0x56, "Неверная структура переданных данных для агента")
    NoTaxMode = (0x57, "Не указан режим налогообложения")
    WrongTaxForAgent = (0x58, "Данная ставка НДС недопустима для агента. Агент не является плательщиком НДС")
    WrongAgentTag = (0x59, "Не указано или неверно указано значение тэга Признак платежного агента")
    WrongBlockFirmware = (0x60, "Номер блока прошивки указан некорректно")
    NotSentDocuments = (0xE0, "Присутствуют неотправленные в ОФД документы")
    WrongRegistrationData = (0xF3, "Подключенный ФН не соответствует данным регистрации ККТ")
    Timeout = (0xFE, "Timeout")
    FnIsNotActive = (0xF4, "ФН еще не был активирован")
    UnknownError = (0xFF, "Неизвестная ошибка")


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
