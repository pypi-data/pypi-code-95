import sbol2
sbol2.setHomespace('http://sys-bio.org')
doc = sbol2.Document()
doc.read('parts.xml')
for obj in doc:
    print(obj.displayId, obj.type)
len(doc)

igem = sbol2.PartShop('https://synbiohub.org/public/igem')
records = igem.search('promoter')
for r in records:
    print(r.identity)

igem.pull('https://synbiohub.org/public/igem/BBa_R0040/1', doc)

promoter_uri = 'https://synbiohub.org/public/igem/BBa_R0040/1'
promoter = doc.componentDefinitions[promoter_uri]
rbs = doc.componentDefinitions['Q2']
cds = doc.componentDefinitions['LuxR']
term = doc.componentDefinitions['ECK120010818']
my_device = doc.componentDefinitions.create('my_device')
my_device.assemblePrimaryStructure([promoter, rbs, cds, term],
                                   sbol2.IGEM_STANDARD_ASSEMBLY)
