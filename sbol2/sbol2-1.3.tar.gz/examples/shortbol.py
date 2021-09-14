import sbol2

sbol2.setHomespace('http://me.name/test#')
seq = sbol2.Sequence('seq', 'agct')

cmp = sbol2.ComponentDefinition('cmp')
cmp.sequences = seq.identity

prom = sbol2.ComponentDefinition('prom')
prom.roles = [sbol2.SO_PROMOTER]
prom.displayId = "p1"
prom.name = "Promoter 1"
prom.description = "The first promoter"

doc = sbol2.Document()
doc.add_list([seq, cmp, prom])
doc.write('shortbol.xml')
