import sbol2
SBH_USER = 'sd2e'
SBH_PASSWORD = 'jWJ1yztJl2f7RaePHMtXmxBBHwNt'

sbh = sbol2.PartShop('https://hub.sd2e.org')
sbh.login(SBH_USER, SBH_PASSWORD)
doc = sbol2.Document()
uri = ('https://hub.sd2e.org/user/sd2e/' +
       'UCSB_GBW_LandingSiteDesignv0_1through36/' +
       'UCSB_GBW_LandingSiteDesignv0_1through36_collection/1')

# Fetch this many at a time
step = 5
query = sbol2.SearchQuery(sbol2.SBOL_SEQUENCE, limit=step)
query[sbol2.SBOL_COLLECTION] = uri

# Find out how many there are
count = sbh.search_count_advanced(query)
print(f'There are {count} sequences to pull')

# Now fetch them a chunk at a time
for offset in range(0, count, step):
    print(f'pulling from offset {offset}')
    query.offset = offset
    result = sbh.search_advanced(query)
    identities = [item.identity for item in result]
    sbh.pull(identities, doc, recursive=False)
print(doc)
