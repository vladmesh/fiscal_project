from enum import Enum


class Tax(Enum):
    SIMPEXP = 2
    GEN = 0
    SIMP = 1


class Vat(Enum):
    NONDS = 6
    NDS20 = 2


class PaymentType(Enum):
    CASH = 1
    NON_CASH = 2


class DocumentType(Enum):
    receipt = 1
    correction = 8
