import sbol2

doc = sbol2.Document()
igem = sbol2.PartShop('https://synbiohub.org/public/igem')
igem.pull('BBa_I719005', doc)

composition = doc.componentDefinitions.create('composition')
composition.assemblePrimaryStructure(['BBa_I719005', 'BBa_I719005'])
doc.write("minimal_example.xml")
