from datetime import datetime

import pymssql
import adodbapi

from core.TicketRecord import *
from core.Company import Company
from core.ValidatorTransaction import ValidatorTrans
from core.utils import strip


class MSSql:
    def __init__(self, server, database, user, password):
        self.database = database
        self.user = user
        self.password = password
        self.server = server
        self.connection = None
        self.cursor = None
    
    def open_connection(self):
        self.connection = pymssql.connect(self.server, self.user, self.password, self.database)
        self.cursor = self.connection.cursor()
    
    def close_connection(self):
        self.connection.close()
    
    def execute(self, command, has_result=True):
        answer = []
        self.open_connection()
        self.cursor.execute(command)
        if has_result:
            rows = self.cursor.fetchall()
            for row in rows:
                record_dict = {}  # каждой записи сопоставляем словарь, типа {Имя колонки : значение}
                for i in range(len(self.cursor.description)):
                    record_dict[self.cursor.description[i][0]] = strip(row[i])
                answer.append(record_dict)
            return answer
        self.close_connection()
    
    def get_company_intervals(self, company: Company):
        answer = []
        command = f"select DATE, f.ROUTEID, f.SPOOLID, TICKETNUMBERFROM, TICKETNUMBERTO, VAT, " \
                  f"RELEASE, f.RECID, f.CREATEDDATETIME, INN_RU, KPP_RU, s.PRICE from dbo.fiscalticketsforbul f" \
                  f" join dbo.A_TICKETSPOOL s on (s.SPOOLID = f.SPOOLID and s.DATAAREAID = f.DATAAREAID) " \
                  f" join dbo.RouteReleaseTypeExtLink link on (link.ROUTEID = f.ROUTEID and link.DATEFROM <= f.DATE " \
                  f" and (link.DATETO > f.DATE or link.DATETO = '1900-01-01 00:00:00') and link.DATAAREAID = " \
                  f"f.DATAAREAID) " \
                  f" join dbo.FiscalFIReleaseTypeTaxLink flink on (flink.FIReleaseType = link.ReleaseTypeExt)"
        command += f" where INN_RU = '{company.inn}' and KPP_RU = '{company.kpp}' and FiscalStatus = 0 " \
                   f"and Date > '2021-03-01 '"
        command += ' order by RECID'
        rows = self.execute(command)
        for row in rows:
            bul_record = BULRecord(row)
            bul_record.companyid = company.id
            answer.append(bul_record)
        return answer
    
    def get_intervals_on_date(self, date_from: datetime, date_to: datetime):
        date_from_str = date_from.strftime("%Y-%m-%dT%H:%M:%S")
        date_to_str = date_to.strftime("%Y-%m-%dT%H:%M:%S")
        answer = []
        command = f"select DATE, f.ROUTEID, f.SPOOLID, TICKETNUMBERFROM, TICKETNUMBERTO, VAT, " \
                  f"RELEASE, f.RECID, f.CREATEDDATETIME, INN_RU, KPP_RU, s.PRICE from dbo.fiscalticketsforbul f" \
                  f" join dbo.A_TICKETSPOOL s on (s.SPOOLID = f.SPOOLID and s.DATAAREAID = f.DATAAREAID) " \
                  f" join dbo.RouteReleaseTypeExtLink link on (link.ROUTEID = f.ROUTEID and link.DATEFROM <= f.DATE " \
                  f" and (link.DATETO > f.DATE or link.DATETO = '1900-01-01 00:00:00') and link.DATAAREAID = " \
                  f"f.DATAAREAID) " \
                  f" join dbo.FiscalFIReleaseTypeTaxLink flink on (flink.FIReleaseType = link.ReleaseTypeExt)"
        command += f" where f.CREATEDDATETIME >= '{date_from_str}' and f.CREATEDDATETIME < '{date_to_str}'"
        command += ' order by RECID'
        rows = self.execute(command)
        for row in rows:
            bul_record = BULRecord(row)
            answer.append(bul_record)
        return answer
    
    def test(self):
        answer = []
        command = f"select top 10 * from  ValidatorTransImported"
        rows = self.execute(command)
        for row in rows:
            answer.append(row)
        return answer
    
    def get_buffer_intervals(self):
        answer = []
        command = f"select TOP 25 DATE, b.TICKETSPOOLID, NUMBERFROM, NUMBERTO, VAT, " \
                  f"b.RECID, b.CREATEDDATETIME, b.PARTYID, VALUE from dbo.FiscalTicketsBuffer b" \
                  f" join dbo.FiscalFIReleaseTypeTaxLink flink on (flink.FIReleaseType = b.ReleaseTypeExt)"
        command += f" where !isFiscalized"
        command += ' order by b.RECID'
        rows = self.execute(command)
        for row in rows:
            bufferRecord = BufferRecord(row)
            answer.append(bufferRecord)
        return answer
    
    def get_sum(self, date, inn, kpp):
        command = f"select sum((TICKETNUMBERTO - TICKETNUMBERFROM) * PRICE ) as sum from dbo.fiscalticketsforbul f" \
                  f" join dbo.A_TICKETSPOOL s on (s.SPOOLID = f.SPOOLID and s.DATAAREAID = f.DATAAREAID) where " \
                  f" DATE = '{date.strftime('%Y-%m-%d')}' and INN_RU = '{inn}' and KPP_RU = '{kpp}'"
        rows = self.execute(command)
        if len(rows) == 0 or rows[0]['sum'] is None:
            return 0
        return float(rows[0]['sum'])
    
    def get_count(self, date, inn, kpp, price):
        command = f"select  sum(TICKETNUMBERTO - TICKETNUMBERFROM) as count from dbo.fiscalticketsforbul f" \
                  f" join dbo.A_TICKETSPOOL s on (s.SPOOLID = f.SPOOLID and s.DATAAREAID = f.DATAAREAID) where " \
                  f" DATE = '{date.strftime('%Y-%m-%d')}' and INN_RU = '{inn}' and KPP_RU = '{kpp}' and PRICE = {price}"
        rows = self.execute(command)
        if len(rows) == 0 or rows[0]['count'] is None:
            return 0
        return int(rows[0]['count'])
    
    def get_prices(self, date, inn, kpp):
        command = f"select PRICE * 100 as PRICE from dbo.fiscalticketsforbul f" \
                  f" join dbo.A_TICKETSPOOL s on (s.SPOOLID = f.SPOOLID and s.DATAAREAID = f.DATAAREAID) where" \
                  f" DATE = '{date.strftime('%Y-%m-%d')}' and INN_RU = '{inn}' and KPP_RU = '{kpp}' " \
                  f"group by PRICE"
        rows = self.execute(command)
        if len(rows) == 0:
            return []
        return [int(n['PRICE']) for n in rows]



class MSsqlOLEDB:
    def __init__(self, host, db_name):
        self.host = host
        self.db_name = db_name
        self.connection = None

    def open_connection(self):
        self.connection = adodbapi.connect("PROVIDER=SQLOLEDB;Data Source={0};Database={1};"
                                           "trusted_connection=yes;Timeout=500;ConnectTimeout=500;".format(self.host, self.db_name))
        self.connection.CommandTimeout = 5000
        self.connection.timeout = 5000

    def close_connection(self):
        self.connection.close()

    def execute(self, command, has_answer=True):
        self.open_connection()
        answer = None
        cursor = self.connection.cursor()
        cursor.execute(command)
        if has_answer:
            col_names = [i[0] for i in cursor.description]
            rows = cursor.fetchall()
            answer = [dict(zip(col_names, record)) for record in rows]
        self.connection.commit()
        self.close_connection()
        return answer

    def get_new_transactions(self):
        answer = []
        command = f"select top 350 axRecId, rrTransDateTimeUtc0, rrAmountTerminal, rrTerminalId, rrPaymentERN, " \
                  f" axRouteId, rrTransRouteNum, axDateRelease, axTimeAbs, axRouteId, axINN_RU, axKPPU_RU, " \
                  f"rrRegDateTimeUtc0 from  dbo.v_SberES_ValidatorTransImportView where" \
                  f" axIsFiscalized is null order by axRecId"
        rows = self.execute(command)
        for row in rows:
            trans = ValidatorTrans(row)
            answer.append(trans)
        return answer

    def set_transactions_fiscalized(self, ids, status):
        command = f"update dbo.SberES_ValidatorTransImported set axIsFiscalized = {status} where axRecId in {ids}"
        self.execute(command, False)
