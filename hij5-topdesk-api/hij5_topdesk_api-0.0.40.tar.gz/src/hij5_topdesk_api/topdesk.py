import json

import requests
import datetime

from .exceptions.exceptions import IncidentNotExistsException, ProcessingStatusDoesNotExistException



class TopdeskConnector:
	def __init__(self, baseURL: str, authkey: str):
		"""
		Base URL example: https://example.topdesk.com/tas/api/
		"""
		self.authkey = authkey
		self.headers = {
			'Authorization': authkey,
			'Accept': 'application/json',
			'Content-Type': 'application/json',
		}
		self.baseURL = baseURL

	def make_request(self, method, url_extension, params=None, headers=None, files=None, json_data=None,
					 auto_parse=True):
		"""
		Make a request to the API and return the repsonse content

		:param auto_parse: bool: Wether the response should be automatically parsed from json. Disable this for requests like filereponses.
		:param method: [string] HTTP method e.g. "POST", "GET"
		:param url_extension: [string] extension of the base url. e.g. incidents/
		:param params: [dict] parameters to be added to the request
		:param headers: [dict] headers to be added to the request
		:param files: [dict] files to be added to the request
		:param: json_data [dict] Body data.
		:return: [dict] response body

		"""
		url = self.baseURL + url_extension
		# get default headers if not set.
		if headers is None:
			headers = self.headers
		response = requests.request(method, url, params=params, headers=headers, files=files, json=json_data)
		if 200 <= response.status_code <= 299:
			if response.content:
				if auto_parse:
					return json.loads(response.content)
				else:
					return response
			else:
				return ""
		else:
			print("Status code:", response.status_code)
			print("content:", response.content)

	def valid_connection(self):
		"""
		Test de verbinding met Topdesk
		:return: bool
		"""
		response = self.make_request('get', 'version', auto_parse=False)
		if response:
			if response.status_code == 200:
				return True
		return False

	def incident(self, incident_id: str):
		"""
		Verkrijg een incident op basis van het incident ID
		Args:
			incident_id:

		Returns: Incident

		"""
		params = {'id': f"{incident_id}"}
		incident = self.make_request('get', 'incidents/', params=params)
		if incident:
			return incident[0]
		return None

	def __incidents(self, params: dict = None):
		"""
		Verkrijg een lisjt van incidenten
		Args:
			params: paramters die gebruikt kunnen worden om te sorteren of filteren. https://developers.topdesk.com/documentation/index.html#api-Incident-GetListOfIncidents

		Returns:

		"""
		return self.make_request('get', 'incidents/', params=params)

	# def incidents_grouped_by_calltype(self, page_size: int = 10):
	# 	"""
	# 	Verkrijg een lijst van incidenten gegroepeerd op callType en geordend op prioriteit.
	#
	# 	Args:
	# 		page_size: hoeveelheid incidenten
	#
	# 	Returns: lisjt van incidenten
	# 	"""
	# 	params = {
	# 		"order_by": "target_date",
	# 		"processing_status": "95fcb25f-e1c3-4e89-a90d-81e563117086", # In behandeling
	# 	}
	# 	event_incidents = self.__incidents(params=params)
	# 	return event_incidents

	def get_incident_call_types(self):
		"""
		Returns a list of incident call types in the following format
		[
			{"id": "8e1ae455-88ba-493d-a110-99e0b0f8ee69", "name": "Complaint" },
		]
		"""
		return self.make_request('get', 'incidents/call_types')

	def incident_status(self, incident_id: str):
		"""
		Return de status string van een incident

		Args:
			incident_id:

		Returns: Status string

		"""
		incident = self.incident(incident_id)
		return incident.get('status')

	def update_incident(self, incident_id: str, modifications: dict):
		"""
		Update een incident.
		Args:
			incident_id: str
			modifications: dictionairy met de gewenste aanpassingen. bijvoorbeeld: {"processingStatus": {"name": "Gereed"}}

		Returns: Incident
		"""
		try:
			return self.make_request("PUT", f'incidents/id/{incident_id}', json_data=modifications, auto_parse=True)
		except json.JSONDecodeError as e:
			# If we get a message saying nothing has changed, just continue. If not, rethrow the error.
			if not e.doc == 'b\'[{"message":"No fields changed"}]\'':
				print(e.doc)
				raise json.JSONDecodeError(e.doc, e.doc, e.pos)
			return self.incident(incident_id=incident_id)

	def incident_status_to_done(self, incident_id: str):
		"""
		Update de processingStatus van een incident naar Gereed.

		Args:
			incident_id: str: Incident id

		Returns: None

		"""
		status = {"processingStatus": {"name": "Gereed"}}
		return self.update_incident(incident_id=incident_id, modifications=status)

	def set_expenses(self, incident_id: str, expenses: float):
		"""
		Update het onkosten veld van een incident.
		Args:
			incident_id: String
			expenses: Float

		Returns: incident.

		"""
		modifications = {'costs': str(expenses)}
		return self.update_incident(incident_id=incident_id, modifications=modifications)

	def incident_add_action(self, incident_id: str, text: str):
		"""
		Add een tekst in het actie veld in topdesk.
		Args:
			incident_id:
			text: Actie tekst die wordt vermeld in topdesk.

		Returns: Incident.
		"""
		modification = {"action": text}
		return self.update_incident(incident_id=incident_id, modifications=modification)

	def incident_actions(self, incident_id: str):
		"""
		Get incident actions op basis van een incident_id.

		Args:
			incident_id: [string]: incident id

		Returns:

		"""
		return self.make_request('get', f'/incidents/id/{incident_id}/actions')

	def incident_call_type(self, incident_id: str):
		"""
		Return de callType string van een incident

		Args:
			incident_id:

		Returns: Status string calltype

		"""
		incident = self.incident(incident_id)
		return incident.get('callType').get('name')

	def incidents_by_supplier(self, supplier_id, completed: bool or None = None):
		"""
		Get all incidents linked to a supplier id
		:param supplier_id: string
		:param completed: bool or None
		:return:
		"""
		# naam: Comparex Nederland B.V.
		if completed is None or completed is False:
			params = f"query=supplier.id=={supplier_id};processingStatus.name=in=('In behandeling','Toegewezen')"
		if completed:
			params = f'query=supplier.id=={supplier_id};processingStatus.name==Gereed'

		return self.make_request('GET', "incidents", params=params)

	def incidents_by_supplier_with_status(self, supplier_id: str, status_name: str):
		"""
		Verkrijg alle incidenten toebehorende aan een supplier, met een gegeven statusnaam

		Args:
			supplier_id: Supplier Id string
			status_name: status naam van incidenten

		Returns: incidents dict

		"""
		params = f"query=supplier.id=={supplier_id};processingStatus.name=='{status_name}'"
		return self.make_request('GET', "incidents", params=params)

	def newest_incidents(self, amount=5, start_offset=0, processing_status_id: str = None):
		"""
		Verkrijg een lijst van incidenten, gesorteerd op nieuw naar oud
				:param
		:return:
		Args:
			amount: [int]: Amount of incidents. Default = 5
			start_offset: [int] Start offset. Begin bij x
			processing_status: [string] Processing status ID. Als None, alle processing statuses

		Returns: [dictionary] - Lijst van incidenten

		"""
		params = {
			"order_by": "creation_date+DESC",
			"page_size": f"{amount}",
			"start": f"{start_offset}",
			"status": "secondLine"
		}
		if processing_status_id:
			params['processing_status'] = processing_status_id
		return self.make_request('get', 'incidents/', params=params)

	def processing_status_id(self, name: str):
		"""
		Verkrijg de processing status id op basis van een naam

		Args:
			name: naam van de processing status

		Returns: string | None: processing status id
		"""
		statuses = self.make_request('get', 'incidents/statuses')
		for status in statuses:
			if status["name"] == name:
				return status['id']
		raise ProcessingStatusDoesNotExistException

	def incident_attachments(self, id, start=0, page_size=10):
		"""
		Get attachments by incident ID
		:param id: incident id
		:param start: index start
		:param page_size: amount of elements per page
		:return: dict: dict of attachments
		"""
		params = {
			'start': start,
			'page_size': page_size
		}
		return self.make_request('GET', f"incidents/id/{id}/attachments")

	def incident_newest_attachment_grouped(self, incident_id: str, filter_list: list = None):
		"""
		Verrkijg incident attachments gegroepeerd in een dictionary op basis van de filter list. Filter list is een
		lijst van labels waar de attachments op worden gesorteerd. Als de filter_list niet wordt meegegeven, worden
		offerte, werkbon en factuur gebruikt als standaard waardes.

		Args:
			incident_id:
			filter_list: een list met labels waar op gezocht wordt. Alleen attachments die de naam van een label bevat
			wordt opgenomen in de dictionary. De items van deze list worden als keys van de dict gebruikt.
		Returns:

		"""
		files = self.incident_attachments(incident_id)
		files_dict = {}
		if filter_list is None:
			filter_list = ['offerte', 'werkbon', 'factuur']
		# Loop achteruit over de file heen, hierdoor worden de meest recente bestanden uiteindelijk gereturned.
		if files:
			for file in files[::-1]:
				for label in filter_list:
					if label in file.get('fileName'):
						files_dict[label] = file

		return files_dict

	def upload_attachment_to_incident(self, incident_id: int, file_handle):
		"""
		Upload een attachment naar een incident in topdesk.
		:param filename: string incl. extensie
		:param incident_id: int
		:param file_handle: File. Bijvoorbeeld zoals in request.FILES
		:return: response
		"""
		# Custom headers hiervoor om data-type te vermijden
		headers = {
			'Authorization': self.authkey,
			'Accept': 'application/json',
		}
		url = f"incidents/id/{incident_id}/attachments"
		params = {
			"invisibleForCaller": False,
		}
		files = {'file': file_handle}
		return self.make_request('post', url, params=params, files=files, headers=headers)

	def download_attachment(self, incident_id, attachment_id):
		"""
		Download a given attachment

		:param incident_id:
		:param attachment_id:

		:return: tuple: (content, filename)

		"""
		attachments = self.incident_attachments(incident_id)
		# Get attachment again to find original filename. This is not passed by the client because ideally this is stateless.
		filename = None
		for attachment in attachments:
			if attachment.get('id') == attachment_id:
				filename = attachment.get('fileName')
				break
		if filename is None:
			raise FileNotFoundError(
				"Attachment is niet gevonden tussen de lijst van attachments bij het downloaden. topdesk.py -> download_attachment()")
		response = self.make_request("GET", f"incidents/id/{incident_id}/attachments/{attachment_id}/download",
									 auto_parse=False)
		return response.content, filename

	def create_incident(
			self,
			request: str,
			short_description: str,
			action: str,
			status="secondLine",
			costs: int = 0,
			caller_name: str = "Enigma",
			call_type: str = "Storing",
			object_id: str = "",
			object_name: str = "",
			entry_type: str = "",
			operator_name: str = "",
			operator_group: str = "",
			supplier_id: str = "",
			category_name: str = "",
			subcategory_name: str = "",
			impact_name: str = "",
			urgency_name: str = "",
			priority_name: str = ""
	):
		""" Gebruik object_name OF object_id, niet beide. """
		if object_name and object_id:
			raise Exception("Gebruik object name of object_id, niet beide.")

		body = {
			"request": f"{request}",
			"action": f"{action}",
			"status": f"{status}",
			"caller": {"dynamicName": f"{caller_name}"},
			"briefDescription": f"{short_description}"
		}
		if call_type:
			body["callType"] = {
				"name": f"{call_type}"
			}
		if entry_type:
			body["entryType"] = {
				"name": f"{entry_type}"
			}
		if impact_name:
			body["impact"] = {
				"name": f"{impact_name}"
			}
		if object_id:
			body["object"] = {
				"id": f"{object_id}"
			}
		if object_name:
			body["object"] = {
				"name": f"{object_name}"
			}
		if urgency_name:
			body["urgency"] = {
				"name": f"{urgency_name}"
			}
		if priority_name:
			body["priority"] = {
				"name": f"{priority_name}"
			}
		if costs:
			body['costs'] = f"{costs}"
		if category_name:
			body["category"] = {
				"name": f"{category_name}"
			}
		if subcategory_name:
			body["subcategory"] = {
				"name": f"{subcategory_name}"
			}
		if operator_group:
			body["operatorGroup"] = {
				"name": f"{operator_group}"
			}
		if operator_name:
			body["operator"] = {
				"name": f"{operator_name}"
			}
		if supplier_id:
			body['supplier'] = {
				'id': supplier_id
			}

		return self.make_request('post', 'incidents/', json_data=body)

	def operators(self):
		"""
		Get all operators
		:return: [dict]: operators
		"""
		return self.make_request('get', 'operators/')

	def operators_as_tuples(self):
		"""
		Get all operators as a list of tuples. This is mainly used in the user model to link a user to an operator.
		:return: [list]: list of tuples containing ('operatorName', 'operatorId')
		"""
		operators = self.make_request('get', 'operators/', params={'page_size': 100})
		return [(operator.get('id'), operator.get('dynamicName')) for operator in operators]

	def suppliers(self, page_size: int = 100, start: int = 0, exaustive=False):
		"""
		Get all supplier contacts

		Args:
			page_size (int): Hoeveelheid suppliers om op te vragen in request (max = 100)
			start (int): start offset.
			exaustive (bool): Als deze True is, gebruik sliding window om alle suppliers op te halen als er meer dan 100+ zijn.

		:return: dict suppliers.
		"""
		if not exaustive:
			return self.make_request('GET', 'suppliers/', params={'page_size': page_size, 'start': start})
		else:
			output = []
			response = self.make_request('GET', 'suppliers/', auto_parse=False, params={'page_size': page_size, 'start': start})
			output.extend(json.loads(response.content))
			while response.status_code == 206:
				start = start + page_size -1
				response = self.make_request('GET', 'suppliers/', auto_parse=False, params={'page_size': page_size, 'start': start})
				output.extend(json.loads(response.content))
			return output


	def supplier(self, id):
		"""
		Get information of a specific supplier determined by ID
		Args:
			id: supplier ID

		Returns: supplier dict
		"""
		return self.make_request('GET', f'suppliers/{id}')

	def suppliers_as_tuples(self):
		"""
		Get all supplier contacts as a list of tuples
		:return: dict
		"""
		suppliers = self.make_request('GET', 'suppliers/')
		return [(supplier.get('id'), supplier.get('name')) for supplier in suppliers]

	# **************************
	# Operations management ****
	# **************************

	def operational_activities(self, ammount: int = 5) -> dict:
		"""
		Verkrijg een lijst van alle operationele activiteiten
		Params:
			ammount: hoeveelheid activiteiten om op te vragen.
		Returns: Dict

		"""
		params = {
			'pageSize': ammount
		}
		return self.make_request('get', 'operationalActivities', params=params).get('result', None)

	def operational_activities_by_type(self, activity_type: str = None, amount: int = 5, start_offset: int = 0) -> list:
		"""
		Verkrijg een lijst van alle operationele activiteiten op basis van soort
		Params
			activity_type: Soort operationele activiteit.
			ammount: hoeveelheid activiteiten om op te vragen.
		Returns: Dict

		"""
		params = f"query=type.name=='{activity_type}'&pageSize={amount}&pageStart={start_offset}&fields=all"
		print(params)
		headers = self.headers.copy()
		headers['Accept'] = "application/x.topdesk-om-activity-v1+json"
		result = self.make_request('get', 'operationalActivities', params=params, headers=headers)
		output = []
		if result is not None:
			for activity in result.get('results', []):
				output.append(self.make_request('get', f'operationalActivities/{activity.get("id")}'))
		return output

	def operational_activity_by_supplier(self, supplier_id: str, status_string: str, resolved: bool or None = None):
		"""
		Verkrijg operationele activiteiten op basis van supplier_id en status string.
		De API van topdesk is best guur in dit opzicht. de call vereist de Accept: application/x.topdesk-om-activity-v1+json header
		maar wanneer je deze set, krijg je alleen de id en number field terug. Dus moeten we deze nogmaals handmatig opvragen
		om over alle informatie te beschikken.
		Args:
			supplier_id: id van de supplier gekoppeld aan de operationele activiteit.
			status_string: string value van de status waarop gefilterd wordt
			resolved: filter op resolved of niet.
		"""
		params = f"query=supplier.id=='{supplier_id}';type.name=='{status_string}'"
		if resolved is not None:
			params += f";resolved.value=='{resolved}'"
		headers = self.headers.copy()
		headers['Accept'] = "application/x.topdesk-om-activity-v1+json"
		result = self.make_request('get', 'operationalActivities', params=params, headers=headers)
		output = []
		if result:
			for activity in result.get('results', []):
				output.append(self.make_request('get', f'operationalActivities/{activity.get("id")}'))
		return output

	def operational_activity_with_status(self, activity_id: str) -> dict:
		"""
		Verkrijg informatie over 1 operational activity. Er worden twee requests gestuurd, een zonder x.topdesk header en eentje
		met. Door een onhandigheid in de api van topdesk krijg je verschillende informatie terug afhankelijk van de header.
		Dus versturen we twee keer een request en joinen we die samen.

		Args:
			activity_id:

		Returns: dict

		"""
		other_headers = self.headers.copy()
		other_headers['Accept'] = "application/x.topdesk-om-activity-v1+json"
		params = {"fields": "all"}
		request1 = self.make_request('get', f'operationalActivities/{activity_id}/', headers=other_headers, params=params)
		request2 = self.make_request('get', f'operationalActivities/{activity_id}/', headers=self.headers, params=params)
		request1.update(request2)
		return request1

	def operational_activity(self, activity_id):
		"""
		Omdat de topdesk versie heel guur is, verschilt de output afhankelijk van welke header je gebruikt daaorm moet
		deze informatie apart opgehaald worden. Zonder Accept header (belangrijk!)
		Args:
			activity_id:

		Returns:

		"""
		return self.make_request('get', f'operationalActivities/{activity_id}')

	def operational_activity_add_action(self, activity_id: str, text: str, flag: bool=False):
		"""
		Creeer een action bij een operationele activiteit.

		Args:
			activity_id: id van de operationele activiteit
			text: Text van de actie.
			flag: Markeer de action met een vlag.

		Returns: str. Id van de actie die is aangemaakt.
		"""
		body = {
			"memoText": text,
			"flag": flag
		}
		return self.make_request('post', f'operationalActivities/{activity_id}/actions', json_data=body)

	def operational_activity_update(self, activity_id: str, status = None, resolved=None, resolved_datetime=None, operator_id=None, operator_group_id=None):
		"""
		Update een bestaande operationele activiteit
		Args:
			activity_id: Id van de operationele activiteit
			status: UUID van de nieuwe status van een status
			resolved: boolean tickbox om de operationele activiteit als resolved te markeren
			resolved_datetime: Optioneel datetime object voor resolved. Als datetime null is en resolved True, wordt datetime het moment van updaten.
			operator_id: Optionele operator_id
			operator_group_id: optionele operator_group_id

		Returns: None

		"""
		if resolved_datetime is None:
			resolved_datetime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%zZ")
		else:
			resolved_datetime = resolved_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f%zZ")

		body = {}
		if status:
			body['status'] = status
		if resolved:
			body['resolved'] = {
				'value': True,
				'dateTime': resolved_datetime
			}
		if operator_id:
			body['operator'] = operator_id
		if operator_group_id:
			body['operatorGroup'] = operator_group_id

		return self.make_request('POST', f'operationalActivities/{activity_id}', json_data=body)

	def operational_activity_upload_file(self, activity_id, file):
		"""
		UPload een file naar een operationele activiteit.
		Args:
			activity_id:
			file:

		Returns:

		"""
		headers = {
			'Authorization': self.authkey,
			'Accept': 'application/json',
		}
		files = {'file': file}
		return self.make_request('POST', f'operationalActivities/{activity_id}/attachments/upload', headers=headers, files=files)

	# **************************
	# **** Asset management ****
	# **************************

	def assets(self):
		"""
		Verkrijg een lijst van alle assets

		Returns: dict
		"""
		return self.make_request('get', 'assetmgmt/assets/')

	def asset(self, id):
		"""
		Verkrijg info over 1 asset.

		Args:
			id: asset id

		Returns: dict
		"""
		return self.make_request('get', f'assetmgmt/assets/{id}/')

	def asset_upload(self, file, asset_id):
		"""
		Upload een file naar een asset
		Args:
			file: File
			asset_id: string

		Returns:
		"""
		headers = {
			'Authorization': self.authkey,
			'Accept': 'application/json',
		}
		params = {
			'assetId': asset_id
		}
		files = {'file': file}
		return self.make_request('POST', 'assetmgmt/uploads', headers=headers, params=params, files=files)

	def asset_uploaded_files(self, asset_id):
		"""
		Return een lijst met uploads toebehorende aan een asset.
		"""
		params = {
			'assetId': asset_id
		}
		return self.make_request('GET', 'assetmgmt/uploads', params=params).get('dataSet')

	def assets_as_tuples(self):
		"""
		Get all assets as a tuple of id and name
		:return: list[tuple()]
		"""
		assets = self.make_request('GET', 'assetmgmt/assets/')
		return [(asset.get('id'), asset.get('text')) for asset in assets.get('dataSet')]

	def asset_download_file(self, asset_id, attachment_id):
		downloads = self.asset_uploaded_files(asset_id)
		# Vind de juiste URL bij de attachment. Er is momenteel geen endpoint voor directe download.
		for download in downloads:
			if download['id'] == attachment_id:
				url = download['url']
				# De url moet de eerste twee delen van de URL verwijderen. dus explode op /
				url = url.split('/')
				# Verwijder de eerste twee delen.
				url = url[3::]
				# Join ze weer bij elkaar met slashes. Maar zonder laatste slash
				url = "".join([el + "/" for el in url])[:-1:]
				return self.make_request('GET', url, auto_parse=False)
		return None

	def assets_name_as_tuple(self):
		"""
		Get all assets as a tuple of name and name
		:return: list[tuple()]
		"""
		assets = self.make_request('GET', 'assetmgmt/assets/')
		return [(asset.get('text'), asset.get('text')) for asset in assets.get('dataSet')]
