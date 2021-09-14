import sbol2

sbh = sbol2.PartShop('https://hub.sd2e.org')
sbh.login('sd2e')

doc = sbol2.Document()
uri = 'https://hub.sd2e.org/user/sd2e/design/MG1655_LPV3_LacI_Sensor_pTac_AmeR_Network/1'
sbh.pull(uri, doc, True)

print(len(doc.moduleDefinitions[uri].modules.value))
