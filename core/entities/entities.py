import datetime
from enum import Enum
from typing import List, Dict

from dataclasses import dataclass, field

from core.entities.Enums import PaymentType, Tax, Vat, DocumentType


class SourceType(Enum):
    Oracle_ASUOP = 1
    MySql = 2
    MSSQL_BUL = 3
    MSSQL_Trans = 4
    AxValidatorTrans = 5


class Cashbox:
    def __init__(self,
                 ip=None,
                 company_id=None,
                 port=None,
                 fn_number=None,
                 location_id=None,
                 registry_number=None,
                 factory_number=None,
                 ofd_inn=None,
                 auto_device_number=None
                 ):
        self.id = factory_number
        self.ip = ip
        self.company_id = company_id
        self.port = port
        self.fn_number = fn_number
        self.location_id = location_id
        self.registry_number = registry_number
        self.factory_number = factory_number
        self.ofd_inn = ofd_inn
        self.auto_device_number = auto_device_number


class Company:
    def __init__(self, id=None,
                 inn=None, kpp=None,
                 name=None,
                 full_name=None,
                 region=None,
                 payment_place=None,
                 authorized_person_name=None,
                 agent_agent=None,
                 tax=None,
                 provider_name=None,
                 provider_phone=None,
                 provider_inn=None,
                 additional_field_meaning=None,
                 additional_field_value=None,
                 timezone=None,
                 divisions=None,
                 ofd_login=None,
                 ofd_password=None
                 ):
        self.id = id
        self.inn = inn
        self.kpp = kpp
        self.name = name
        self.timezone = timezone
        self.full_name = full_name
        self.region = region
        self.payment_place = payment_place
        self.authorized_person_name = authorized_person_name
        self.agent_agent = agent_agent
        self.tax = tax
        self.provider_name = provider_name
        self.provider_phone = provider_phone
        self.provider_inn = provider_inn
        self.additional_field_meaning = additional_field_meaning
        self.additional_field_value = additional_field_value
        self.divisions = divisions
        self.ofd_login = ofd_login
        self.ofd_password = ofd_password


class InstallPlace:
    def __init__(self, id, address):
        self.id = id
        self.address = address


class Ofd:
    def __init__(self, inn=None, ip=None, port=None, domain=None, name=None, email=None):
        self.id = inn
        self.inn = inn
        self.ip = ip
        self.port = port
        self.domain = domain
        self.name = name
        self.email = email


@dataclass
class Ticket:
    ticket_series: str = None
    ticket_number: str = None
    price: int = None
    payment_type: PaymentType = None
    date_trip: datetime.datetime = None
    date_ins: datetime.datetime = None
    tax: Tax = None
    vat: Vat = None
    dbf_id: int = None
    asuop_id: str = None
    client_email: str = None
    company_id: str = None


@dataclass
class Document:
    fiscal_storage_number: int
    fiscal_number: int
    fiscal_sign: int
    fiscal_date: datetime.datetime
    document_type: DocumentType
    session_num: int
    num_in_session: int
    tax: Tax
    vat: Vat
    payment_type: PaymentType
    price: int
    ticket_id: int = None
    company_id: str = None
    cashbox_id: int = None
    additional_prop: str = None
    dbf_id: int = None
    ofd_id: str = None


@dataclass
class SourceSettings:
    id: str
    type: SourceType
    address: str
    port: int
    database_name: str
    login: str
    password: str
    timezone: str
    query_new_tickets: str
    query_revise: str
    query_by_id: str


@dataclass
class Route:
    route_num: str
    vat: Vat


@dataclass
class Division:
    id: int
    source_id: str
    routes: List[Route]


@dataclass
class CompanyAsuop:
    """Класс для хранения настроек АСУОП по компании"""
    id: str
    inn: str
    kpp: str
    tax: Tax
    divisions: List[Division] = field(default_factory=list)


class AsuopSettings:
    """Класс для настроек выгрузки из АСУОПа Оркал"""

    def __init__(self, companies: List[CompanyAsuop] = None):
        if companies is None:
            companies = []
        self.companies = companies

    def get_divisions(self, source_id: str) -> list:
        answer = []
        for company in self.companies:
            for division in company.divisions:
                if division.source_id == source_id:
                    answer.append(str(division.id))

        return answer

    def get_divisions_to_company_dict(self, source_id: str) -> Dict[int, CompanyAsuop]:
        answer = dict()
        for company in self.companies:
            for division in company.divisions:
                if division.source_id == source_id:
                    answer[division.id] = company
        return answer

    def get_routes_to_vat_dict(self, source_id: str) -> dict:
        answer = dict()
        for company in self.companies:
            for division in company.divisions:
                if division.source_id == source_id:
                    for route in division.routes:
                        answer[route.route_num] = route.vat

        return answer

