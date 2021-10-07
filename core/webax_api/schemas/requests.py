class WebaxRequest:
    def __init__(self, uid):
        self.action = uid


class UpdateStatusRequest(WebaxRequest):
    def __init__(self, rec_id, status, uid):
        self.status = status
        self.rec_id = rec_id
        WebaxRequest.__init__(self, uid)


class GetInnKppByPartyIdRequest(WebaxRequest):
    def __init__(self, party_id, uid):
        self.partyId = party_id
        WebaxRequest.__init__(self, uid)


class GetInnKppByRoute(WebaxRequest):
    def __init__(self, route_id, region, uid, release_date):
        self.routeId = int(route_id)
        self.releaseDate = str(release_date)
        self.region = region
        WebaxRequest.__init__(self, uid)