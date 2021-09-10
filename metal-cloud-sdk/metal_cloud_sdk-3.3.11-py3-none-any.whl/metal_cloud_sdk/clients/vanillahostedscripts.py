from jsonrpc2_base.client import Client
from metal_cloud_sdk.objects.utils.deserializer import Deserializer
from metal_cloud_sdk.objects.utils.serializer import Serializer
from jsonrpc2_base.jsonrpc_exception import JSONRPCException

class VanillaHostedScripts(Client):
	__instance = None

	def __init__(self, dictParams, arrFilterPlugins = []):
		super(VanillaHostedScripts, self).__init__(dictParams, arrFilterPlugins)

	@staticmethod
	def getInstance(dictParams, arrFilterPlugins = []):
		"""
		This is a static function for using the VanillaHostedScripts class as a singleton.
		In order to work with only an instance, instead of instantiating the class,
		call this method.

		@return object VanillaHostedScripts.__instance. It will return the same instance, no matter
		how many times this function is called.
		"""
		if VanillaHostedScripts.__instance is None :
			VanillaHostedScripts.__instance = VanillaHostedScripts(dictParams, arrFilterPlugins)

		return VanillaHostedScripts.__instance


	""" 8 functions available on endpoint. """

	def scripts(self, nUserID, arrScriptsIDs = None):

		arrParams = [
			nUserID,
			arrScriptsIDs,
		]

		self.rpc("scripts", arrParams)


	def getLoggedInUser(self):

		arrParams = [
		]

		self.rpc("getLoggedInUser", arrParams)


	def getCustomPDOInstance(self):

		arrParams = [
		]

		self.rpc("getCustomPDOInstance", arrParams)


	def createScript(self, nUserID, objScript):

		objScript = Serializer.serialize(objScript)

		arrParams = [
			nUserID,
			objScript,
		]

		return Deserializer.deserialize(self.rpc("createScript", arrParams))

	def updateScript(self, nScriptID, objScript):

		objScript = Serializer.serialize(objScript)

		arrParams = [
			nScriptID,
			objScript,
		]

		return self.rpc("updateScript", arrParams)


	def deleteScript(self, nScriptID):

		arrParams = [
			nScriptID,
		]

		self.rpc("deleteScript", arrParams)


	def ownerScriptsIDs(self, nUserID):

		arrParams = [
			nUserID,
		]

		return self.rpc("ownerScriptsIDs", arrParams)


	def getScript(self, nScriptID):

		arrParams = [
			nScriptID,
		]

		return Deserializer.deserialize(self.rpc("getScript", arrParams))

