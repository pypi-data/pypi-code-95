class Paging:
    fullTextFilter = ""
    filters = {}
    fields = ""
    offset = 0
    limit = 0
    sortBy = "id"
    sortOrder = "ASCENDING"  # "ASCENDING" or "DESCENDING"
    totalNumberOfRecords = 0
    loadReferenceDepth = 0

    def __init__(self, fullTextFilter="", filters={}, fields="", offset=0, limit=0,
                 sortBy="id", sortOrder="ASCENDING", totalNumberOfRecords=0,
                 loadReferenceDepth=0):
        self.fullTextFilter = fullTextFilter
        self.filters = filters
        self.fields = fields
        self.offset = offset
        self.limit = limit
        self.sortBy = sortBy
        self.sortOrder = sortOrder
        self.totalNumberOfRecords = totalNumberOfRecords
        self.loadReferenceDepth = loadReferenceDepth
