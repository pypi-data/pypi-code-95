import sbol2

doc = sbol2.Document()
GFP = sbol2.ComponentDefinition("GFP")
doc.add(GFP)
collection = doc.collections.create("collection")
collection.members = [GFP.identity]
doc.write("Test_Collections.xml")
