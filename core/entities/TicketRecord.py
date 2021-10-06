from core.Ticket import Ticket


class TicketRecord:
    pass


class BULRecord:
    def __init__(self, record):
        self.date = record['DATE']
        self.route_id = record['ROUTEID']
        self.spool_id = record['SPOOLID'].upper()
        self.ticket_number_from = record['TICKETNUMBERFROM']
        self.ticket_number_to = record['TICKETNUMBERTO']
        self.release = record['RELEASE']
        self.id = record['RECID']
        self.vat = "NONDS" if record['VAT'] == 6 else "NDS20"
        # self.release_type = record['RELEASETYPE']
        # self.driver_id = record['DRIVERID']
        self.created_dt = record['CREATEDDATETIME']
        self.inn = record['INN_RU']
        self.kpp = record['KPP_RU']
        # self.is_rolling = bool(record['ROLLING'])
        # self.fiscal_type = record['FISCALTYPE']

    def get_tickets(self):
        tickets = set()
        for i in range(self.ticket_number_from, self.ticket_number_to):
            ticket = Ticket()
            ticket.date_trip = self.date
            ticket.date_ins = self.created_dt
            series_split = self.spool_id.split('-')
            ticket.price = int(float(series_split[3]) * 100)
            ticket.ticket_series = f"{series_split[0]}-{series_split[1]}-{ticket.price}"
            if i == 1000:
                tmpnum = '000'
            else:
                tmpnum = f"{'0' * (3 - len(str(i)))}{i}"
            ticket.ticket_number = f"{series_split[2]}{tmpnum}"
            ticket.ticket_series = ticket.ticket_series.upper()
            ticket.payment_type = 1
            ticket.inn = self.inn.strip()
            ticket.kpp = self.kpp.strip()
            # ticket.type = self.fiscal_type
            
            ticket.id = self.id
            ticket.route_id = self.route_id
            ticket.vat = self.vat
            # ticket.driver_id = self.driver_id
            ticket.release = self.release
            # ticket.is_rolling = self.is_rolling
            ticket.spool_id = self.spool_id
            tickets.add(ticket)
        return tickets


class BufferRecord:
    def __init__(self, record, company):
        self.spool_id = record['TICKETSPOOLID'].upper()
        self.date = record['RELEASEDATE']
        self.ticket_number_from = record['NUMBERFROM']
        self.ticket_number_to = record['NUMBERTO']
        self.id = record['RECID']
        self.vat = "NONDS" if record['VAT'] == 6 else "NDS20"
        self.created_dt = record['CREATEDDATETIME']
        self.party_id = record['PARTYID']
        self.price = record['VALUE']
        self.company_id = company.id
        self.inn = company.inn
        self.kpp = company.kpp

    def get_tickets(self):
        tickets = []
        for i in range(self.ticket_number_from, self.ticket_number_to):
            ticket = Ticket()
            ticket.dateTrip = self.date
            ticket.dateIns = self.created_dt
            series_split = self.spool_id.split('-')
            ticket.ticketSeries = f"{series_split[0]}-{series_split[1]}"
            if i == 1000:
                tmpnum = '000'
            else:
                tmpnum = f"{'0' * (3 - len(str(i)))}{i}"
            ticket.ticketNum = f"{series_split[2]}{tmpnum}"
            ticket.ticketSeries = ticket.ticketSeries.upper()
            ticket.payType = 1
            ticket.inn = self.inn.strip()
            ticket.kpp = self.kpp.strip()
            # ticket.type = self.fiscal_type
            ticket.price = int(float(series_split[3]) * 100)
            ticket.ticketSeries = f"{series_split[0]}-{series_split[1]}-{ticket.price}"
            ticket.id = self.id
            ticket.vat = self.vat
            ticket.spool_id = self.spool_id
            ticket.company_id = self.company_id
            tickets.append(ticket)
        return tickets
