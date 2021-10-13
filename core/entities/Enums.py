from enum import Enum


class Tax(Enum):
    SIMPEXP = 1
    GEN = 2
    SIMP = 3


class Vat(Enum):
    NONDS = 1
    NDS20 = 2


class PaymentType(Enum):
    CASH = 1
    NON_CASH = 2


class DocumentType(Enum):
    receipt = 1
    correction = 8
