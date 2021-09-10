#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import copy
from jinja2 import Template
from datetime import date, datetime
from distutils.util import strtobool

class ConditionFHIR:
    resource_type = "Condition"
    default_coding_system = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary'
    default_coding_version = '1.0.0'
    agent_url = "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#condition/agent"

    def __init__(self, resource=None) -> None:
        self.patient = None
        self.code = None
        self.category = None
        self.extension = []
        self.from_dict(cat_dict=resource)
    
    def from_dict(self, cat_dict=None):
        if cat_dict is None:
            return
        if 'extension' in cat_dict and cat_dict['extension']:
            for extension in cat_dict['extension']:
                self.extension.append(extension)
        if 'patient' in cat_dict and cat_dict['patient']:
            if 'reference' in cat_dict['patient']:
                self.patient = cat_dict['patient']
            elif 'resourceType' in cat_dict['patient'] and cat_dict['patient']['resourceType'] == 'Patient':
                self.patient = PatientFHIR(patient_dict=cat_dict['patient'])
        if 'code' in cat_dict and cat_dict['code']:
            self.code = cat_dict['code']
        if 'category' in cat_dict and cat_dict['category']:
            self.category = cat_dict['category']
        
    def get_code(self, system=None, version=None):
        if system is None:
            system = self.default_coding_system
        if version is None:
            version = self.default_coding_version
        for coding in self.code['coding']:
            if coding['system'] == system and coding['version'] == version:
                return coding
        return self.code['coding'][0]

    def get_category(self, system=None, version=None):
        if system is None:
            system = self.default_coding_system
        if version is None:
            version = self.default_coding_version
        for coding in self.category['coding']:
            if coding['system'] == system and coding['version'] == version:
                return coding
        return self.category['coding'][0]

    def get_agent(self, system=None, version=None):
        if system is None:
            system = self.default_coding_system
        if version is None:
            version = self.default_coding_version

        for extension in self.extension:
            if 'url' in extension and extension['url'] == self.agent_url and "valueCodeableConcept" in extension:
                for coding in extension['valueCodeableConcept']['coding']:
                    if coding['system'] == system and coding['version'] == version:
                        return coding
                if len(extension['valueCodeableConcept']['coding']) > 0:     
                    return extension['valueCodeableConcept']['coding'][0]


class OperationOutcomeFHIR:
    resource_type = "OperationOutcome"
    issues = []
    default_coding_system = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary'
    default_coding_version = '1.0.0'

    def __init__(self, resource=None) -> None:
        self.issues = []
        self.from_dict(oo_dict=resource)

    def from_dict(self, oo_dict=None):
        if oo_dict is None:
            return
        if 'issue' in oo_dict and oo_dict['issue']:
            for issue in oo_dict['issue']:
                self.issues.append(issue)

    def getFhirResource(self):
        res = {}
        res['resourceType'] = self.resource_type
        res['issue'] = self.issues
        return res

    def get_issue_count(self):
        return len(self.issues)

    def get_issue_code(self, index=0):
        return self.issues[index]['code']

    def get_issue_severity(self, index=0):
        return self.issues[index]['code']

    def get_issue_details(self, index=0, system=None, version=None):
        if system is None:
            system = self.default_coding_system
        if version is None:
            version = self.default_coding_version

        for coding in self.issues[index]['details']['coding']:
            if system in coding and coding['system'] == system and version in coding and coding['version'] == version:
                return coding
        return self.issues[index]['details']['coding'][0]
        
class ParameterFHIR:
    resource_type = "Parameters"
    parameters = []
    def __init__(self, resource=None):
        self.parameters = []
        self.fromFhirResource(resource=resource)

    def add_parameter(self, resource, name='resource'):
        parameter = {}
        parameter['name'] = name
        parameter['resource'] = resource
        self.parameters.append(parameter)

    def getFhirResource(self):
        res = {}
        res['resourceType'] = self.resource_type
        res['parameter'] = []
        for param in self.parameters:
            param_dict = {}
            param_dict['name'] = param['name']
            if type (param['resource']) is dict:
                param_dict['resource'] = param['resource']
            else:
                param_dict['resource'] = param['resource'].getFhirResource()
            res['parameter'].append(param_dict)
        return res

    def fromFhirResource(self, resource):
        if resource is not None:
            if type(res) is str:
                res = json.loads(resource)
            self.resource_type = res['resourceType']
            for param in res['parameter']:
                self.add_parameter(resource=res['parameter'])

class BundleFHIR:
    resource_type = "Bundle"
    type = None
    entries = []
    def __init__(self, resource=None):
        self.resource = {}
        self.resource['resourceType'] = self.resource_type
        self.resource['entry'] = []
        self.entries = []
        if resource is not None:
            if 'type' in resource:
                self.type = resource['type']
            if 'entry' in resource and resource['entry']:
                for entry in resource['entry']:
                    entry_response = entry['response'] if "response" in entry else None
                    self.add_entry(resource=entry['resource'], response=entry_response)

    def add_entry(self, resource, response=None):
        entry = {}
        if type(resource) is dict:
            entry['resource'] = resource
        else:
            entry['resource'] = resource.getFhirResource()
        if response is not None:
            entry['response'] = response
        self.resource['entry'].append(entry)
        self.add_object_to_entries(resource=resource, response=response)

    def add_object_to_entries(self, resource, response=None):
        entry = {}
        if type(resource) is dict and resource['resourceType'] == 'Patient':
            entry['resource'] = PatientFHIR(patient_dict=resource)
        elif type(resource) is dict and resource['resourceType'] == 'Bundle':
            entry['resource'] = BundleFHIR(resource=resource)
        elif type(resource) is dict and resource['resourceType'] == 'Immunization':
            entry['resource'] = ImmunizationFHIR(imm_dict=resource)
        elif type(resource) is dict and resource['resourceType'] == 'OperationOutcome':
            entry['resource'] = OperationOutcomeFHIR(resource=resource)
        elif type(resource) is dict and resource['resourceType'] == 'Condition':
            entry['resource'] = ConditionFHIR(resource=resource)
        else:
            entry['resource'] = resource
        if response is not None:
            entry['response'] = response
        self.entries.append(entry)

    def getFhirResource(self):
        if self.type is not None:
            self.resource['type'] = self.type
        return self.resource

    def fromFhirResource(self, resource):
        res = json.loads(resource)
        self.resource_type = res['resourceType']
        self.entry = res['entry'] if 'entry' in res else None
        self.type = res['type'] if 'type' in res else None
        

    def count_entries(self, recurse=False, resource_type=None):
        if recurse:
            total = 0
            for entry in self.entries:
                if resource_type is None or entry['resource'].resource_type == resource_type:
                    total += 1
                if entry['resource'].resource_type == 'Bundle':
                    nb_entries = entry['resource'].count_entries(recurse=True, resource_type=resource_type)
                    total += nb_entries
            return total
        else:
            return len(self.entries)

    def get_entries(self, recurse=False, resource_type=None):
        entries = []
        if recurse:
            for entry in self.entries:
                if resource_type is None or entry['resource'].resource_type == resource_type:
                     entries.append(entry['resource'])
                if entry['resource'].resource_type == 'Bundle':
                    sub_entries = entry['resource'].get_entries(recurse=True, resource_type=resource_type)
                    for e in sub_entries:
                        entries.append(e)
            return entries
        else:
            for entry in self.entries:
                if resource_type is None or entry['resource'].resource_type == resource_type:
                    entries.append(entry['resource'])

class ImmunizationFHIR:
    resource_type = 'Immunization'
    id = None
    updated_by = None
    creation_date = None
    created_by = None
    version_id = 1
    last_updated = None
    profile = ['http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/profiles/InspqImmunization.structuredefinition.xml']
    organization = None
    override_status_id = None
    override_status_code = None
    override_status_display = None
    lot_id = None
    lot_number = None
    expiration_date = None
    antigen_status = {
        'url': 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/antigenstatus',
        'extension': []
    }
    antigen_extension_dose_number = {
        'url': 'doseNumber'
    }
    antigen_id = None
    antigen_code = None
    antigen_display = None
    antigen_dose_number = 0
    antigen_status_id = None
    antigen_status_code = None
    antigen_status_display = None
    trade_name = None
    status = None
    date = None
    vaccine_code_id = None
    vaccine_code_code = None
    vaccine_code_display = None
    patient = None
    patient_reference = None
    reported = False
    performer = None
    performer_reference = None
    performer_display = None
    location = None
    location_reference = None
    location_display = None
    
    site_id = None
    site_code = None
    site_display = None
    route_id = None
    route_code = None
    route_display = None
    coding_system = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary'
    coding_version = '1.0.0'

    dose_quantity_value = 0.0
    dose_quantity_unit = None
    dose_quantity_code = None
    reason = None
    response_status = None
    response_etag = None
    response_last_modified = None

    def __init__(self, imm_dict=None) -> None:
        self.coding_struct = {
            'coding': [
                {
                    'system': self.coding_system,
                    'version': self.coding_version
                }
            ]
        }
        self.dose_quantity_struct = {
            'system': copy.deepcopy(self.coding_struct)
        }
        self.antigen_extension_antigen_struct = {
            'url': 'antigen',
            'valueCodeableConcept': copy.deepcopy(self.coding_struct)
        }
        self.override_status_struct = {
            'url': 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/overridestatus',
            'valueCodeableConcept': copy.deepcopy(self.coding_struct)
        }
        self.antigen_extension_status_struct = {
            'url': 'status',
            'valueCodeableConcept': copy.deepcopy(self.coding_struct)
        }
        self.vaccine_code_struct = copy.deepcopy(self.coding_struct)
        self.site_struct = copy.deepcopy(self.coding_struct)
        self.route_struct = copy.deepcopy(self.coding_struct)
        if imm_dict is None:
            self.resource = {}
            self.resource['resourceType'] = self.resource_type
            self.creation_date = date.today()
            self.last_updated = datetime.now()
            self.date = datetime.now()
        else: 
            self.from_dict(imm_dict=imm_dict)
    
    def getFhirResource(self):
        resource = {}
        resource['resourceType'] = self.resource_type
        resource['id'] = self.id
        resource['meta'] = {}
        resource['meta']['extension'] = []
        if self.updated_by is not None:
            ext = {}
            ext['url'] = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#common/updatedby'
            ext['valueString'] = self.updated_by
            resource['meta']['extension'].append(ext)
        ext = {}
        ext['url'] = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#common/creationdate'
        ext['valueDate'] = self.creation_date
        resource['meta']['extension'].append(ext)
        if self.created_by is not None:
            ext = {}
            ext['url'] = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#common/createdby'
            ext['valueString'] = self.created_by
            resource['meta']['extension'].append(ext)
        resource['meta']['versionId'] = self.version_id
        resource['meta']['lastUpdated'] = self.last_updated
        resource['meta']['profile'] = [ self.profile ]
        if self.organization is not None:
            resource['contained'] = []
            resource['contained'].append(self.organization.getFhirResource())
        resource['extension'] = []
        if self.override_status_code is not None:
            self.override_status_struct['valueCodeableConcept']['coding'][0]['code'] = self.override_status_code
            if self.override_status_display is not None:
                self.override_status_struct['valueCodeableConcept']['coding'][0]['display'] = self.override_status_display
            if self.override_status_id is not None:
                self.override_status_struct['valueCodeableConcept']['coding'][0]['id'] = self.override_status_id
            resource['extension'].append(self.override_status_struct)
        if self.lot_id is not None:
            lot = {}
            lot['url'] = 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/lotid'
            lot['valueString'] = self.lot_id
            resource['extension'].append(lot)
        if self.antigen_code is not None:
            self.antigen_extension_antigen_struct['valueCodeableConcept']['coding'][0]['code'] = self.antigen_code
            if self.antigen_display is not None:
                self.antigen_extension_antigen_struct['valueCodeableConcept']['coding'][0]['display'] = self.antigen_display
            if self.antigen_id is not None:
                self.antigen_extension_antigen_struct['valueCodeableConcept']['coding'][0]['id'] = self.antigen_id
            self.antigen_status['extension'].append(self.antigen_extension_antigen_struct)
        if self.antigen_dose_number != 0:
            self.antigen_extension_dose_number['valueInteger'] = self.antigen_dose_number
            self.antigen_status['extension'].append(self.antigen_extension_dose_number)
        if self.antigen_status_code is not None:
            self.antigen_extension_status_struct['valueCodeableConcept']['coding'][0]['code'] = self.antigen_status_code
            if self.antigen_status_display is not None:
                self.antigen_extension_status_struct['valueCodeableConcept']['coding'][0]['display'] = self.antigen_status_display
            if self.antigen_status_id is not None:
                self.antigen_extension_status_struct['valueCodeableConcept']['coding'][0]['id'] = self.antigen_status_id
            self.antigen_status['extension'].append(self.antigen_extension_status_struct)
        resource['extension'].append(self.antigen_status)
        if self.trade_name is not None:
            tradename = {
                'url': 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/tradename',
                'valueString': self.trade_name
            }
            resource['extension'].append(tradename)
        if self.status is not None:
            resource['status'] = self.status
        if self.date is not None:
            resource['date'] = self.date
        if self.vaccine_code_code is not None:
            self.vaccine_code_struct['coding'][0]['code'] = self.vaccine_code_code
            if self.vaccine_code_display is not None:
                self.vaccine_code_struct['coding'][0]['display'] = self.vaccine_code_display
            if self.vaccine_code_id is not None:
                self.vaccine_code_struct['coding'][0]['id'] = self.vaccine_code_id
            resource['vaccineCode'] = self.vaccine_code_struct
        if self.patient is not None:
            resource['patient'] = self.patient.getFhirResource()
        elif self.patient_reference is not None:
            resource['patient'] = {
                'reference': self.patient_reference
            }
        resource['reported'] = self.reported
        if self.performer is not None:
            resource['performer'] = self.performer.getFhirResource()
        elif self.performer_reference is not None:
            resource['performer'] = {
                'reference': self.performer_reference
            }
            if self.performer_display is not None:
                resource['performer']['display'] = self.performer_display
        if self.location is not None:
            resource['location'] = self.location.getFhirResource()
        elif self.location_reference is not None:
            resource['location'] = {
                'reference': self.location_reference
            }
            if self.location_display is not None:
                resource['location']['display'] = self.location_display
        if self.lot_number is not None:
            resource['lotNumber'] = self.lot_number
        if self.expiration_date is not None:
            resource['expirationDate'] = self.expiration_date
        if self.site_code is not None:
            self.site_struct['coding'][0]['code'] = self.site_code
            if self.site_display is not None:
                self.site_struct['coding'][0]['display'] = self.site_display
            if self.site_id is not None:
                self.site_struct['coding'][0]['id'] = self.site_id
            resource['site'] = self.site_struct
        if self.route_code is not None:
            self.route_struct['coding'][0]['code'] = self.route_code
            if self.route_display is not None:
                self.route_struct['coding'][0]['display'] = self.route_display
            if self.route_id is not None:
                self.route_struct['coding'][0]['id'] = self.route_id
            resource['route'] = self.route_struct
        if self.dose_quantity_value != 0.0:
            self.dose_quantity_struct['value'] = self.dose_quantity_value
            if self.dose_quantity_code is not None:
                self.dose_quantity_struct['code'] = self.dose_quantity_code
            if self.dose_quantity_unit is not None:
                self.dose_quantity_struct['unit'] = self.dose_quantity_unit
            resource['doseQuantity'] = self.dose_quantity_struct
        if self.reason is not None and self.reason:
            explanation = {}
            explanation['reason'] = []
            for reason in self.reason:
                new_reason = copy.deepcopy(self.coding_struct)
                if "code" in reason:
                    new_reason['coding'][0]['code'] = reason['code']
                if "display" in reason:
                    new_reason['coding'][0]['display'] = reason['display']
                if "id" in reason:
                    new_reason['coding'][0]['id'] = reason['id']
                explanation['reason'].append(new_reason)
            resource['explanation'] = explanation
        return resource

    def from_dict(self, imm_dict=None):
        if imm_dict is None or "resourceType" not in imm_dict or imm_dict['resourceType'] != 'Immunization':
            return
        if "id" in imm_dict:
            self.id = imm_dict['id']
        if "meta" in imm_dict and "extension" in imm_dict['meta']:
            for ext in imm_dict['meta']['extension']:
                if ext['url'] == "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#common/updatedby":
                    self.updated_by = ext['valueString']
                elif ext['url'] == "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#common/creationdate":
                    self.creation_date = ext['valueDate']
                elif ext['url'] == "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#common/createdby":
                    self.created_by = ext['valueString']
            if "versionId" in imm_dict['meta']:
                self.version_id = int(imm_dict['meta']['versionId'])
            if "lastUpdated" in imm_dict['meta']:
                self.last_updated = imm_dict['meta']['lastUpdated']
            if "profile" in imm_dict['meta']:
                self.profile = imm_dict['meta']['profile']
        # TODO traiter contained
        if "extension" in imm_dict:
            for ext in imm_dict['extension']:
                if (ext['url'] == "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/overridestatus"
                        and 'valueCodeableConcept' in ext 
                        and "coding" in ext['valueCodeableConcept']):
                    for coding in ext['valueCodeableConcept']['coding']:
                        if coding['system'] == "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary":
                            if "code" in coding:
                                self.override_status_code = coding['code']
                            if "display" in coding:
                                self.override_status_display = coding['display']
                            if "id" in coding:
                                self.override_status_id = coding['id']
                elif (ext['url'] == "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/lotid"
                        and "valueString" in ext):
                    self.lot_id = ext['valueString']
                elif (ext['url'] == "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/antigenstatus"
                        and "extension" in ext):
                    for antigen_status_ext in ext['extension']:
                        if (antigen_status_ext['url'] == "antigen"
                                and "valueCodeableConcept" in antigen_status_ext
                                and "coding" in antigen_status_ext['valueCodeableConcept']):
                            for coding in antigen_status_ext['valueCodeableConcept']['coding']:
                                if coding['system'] == "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary":
                                    if 'id' in coding:
                                        self.antigen_id = coding['id']
                                    if 'code' in coding:
                                        self.antigen_code = coding['code']
                                    if 'display' in coding:
                                        self.antigen_display = coding['display']
                        elif (antigen_status_ext['url'] == "doseNumber"
                                and "valueInteger" in antigen_status_ext):
                            self.antigen_dose_number = int(antigen_status_ext['valueInteger'])
                        elif (antigen_status_ext['url'] == 'status'
                                and "valueCodeableConcept" in antigen_status_ext
                                and "coding" in antigen_status_ext['valueCodeableConcept']):
                            for coding in antigen_status_ext['valueCodeableConcept']['coding']:
                                if "id" in coding:
                                    self.antigen_status_id = coding['id']
                                if "code" in coding:
                                    self.antigen_status_code = coding['code']
                                if "display" in coding:
                                    self.antigen_status_display = coding['display']
                elif (ext['url'] == "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#immunization/tradename"
                        and "valueString" in ext):
                    self.trade_name = ext['valueString']
        if "status" in imm_dict:
            self.status = imm_dict['status']
        if "date" in imm_dict:
            self.date = imm_dict['date']
        if "vaccineCode" in imm_dict and "coding" in imm_dict["vaccineCode"]:
            for coding in imm_dict["vaccineCode"]['coding']:
                if coding['system'] == "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary":
                    if "code" in coding:
                        self.vaccine_code_code = coding['code']
                    if "display" in coding:
                        self.vaccine_code_display = coding['display']
                    if "id" in coding:
                        self.vaccine_code_id = coding['id']
        if "patient" in imm_dict and "reference" in imm_dict['patient']:
            self.patient_reference = imm_dict['patient']['reference']
        if "reported" in imm_dict:
            self.reported = imm_dict['reported']
        if "performer" in imm_dict:
            if "reference" in imm_dict['performer']:
                self.performer_reference = imm_dict['performer']['reference']
            if "display" in imm_dict['performer']:
                self.performer_display = imm_dict['performer']['display']
        if "location" in imm_dict:
            if "reference" in imm_dict['location']:
                self.location_reference = imm_dict['location']['reference']
            if "display" in imm_dict['location']:
                self.location_display = imm_dict['location']['display']
        if "lotNumber" in imm_dict:
            self.lot_number = imm_dict['lotNumber']
        if "expirationDate" in imm_dict:
            self.expiration_date = imm_dict['expirationDate']
        if "site" in imm_dict and "coding" in imm_dict["site"]:
            for coding in imm_dict["site"]['coding']:
                if coding['system'] == "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary":
                    if "code" in coding:
                        self.site_code = coding['code']
                    if "display" in coding:
                        self.site_display = coding['display']
                    if "id" in coding:
                        self.site_id = coding['id']
        if "route" in imm_dict and "coding" in imm_dict["route"]:
            for coding in imm_dict["route"]['coding']:
                if coding['system'] == "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary":
                    if "code" in coding:
                        self.route_code = coding['code']
                    if "display" in coding:
                        self.route_display = coding['display']
                    if "id" in coding:
                        self.route_id = coding['id']
        if "doseQuantity" in imm_dict:
            if "value" in imm_dict['doseQuantity']:
                self.dose_quantity_value = imm_dict['doseQuantity']['value']
            if "code" in imm_dict['doseQuantity']:
                self.dose_quantity_code = imm_dict['doseQuantity']['code']
            if "unit" in imm_dict['doseQuantity']:
                self.dose_quantity_unit = imm_dict['doseQuantity']['unit']
        if ("explanation" in imm_dict
                and "reason" in imm_dict['explanation']
                and imm_dict["explanation"]['reason']):
            self.reason = []
            for reason in imm_dict["explanation"]['reason']:
                if "coding" in reason:
                    for coding in reason['coding']:
                        if coding['system'] == self.coding_system:
                            new_reason = {}
                            if "code" in coding:
                                new_reason['code'] = coding['code']
                            if "display" in coding:
                                new_reason['display'] = coding['display']
                            if "id" in coding:
                                new_reason['id'] = coding['id']
                            self.reason.append(new_reason)
        

class PatientFHIR:
    resource_type = 'Patient'
    id = None
    user_name = None
    creation_date = None
    update_timestamp = None
    matchramq = None
    active = True
    nam = None
    niu = None
    family_name = None
    given_name = None
    phone_number = None
    gender = None
    birth_date = None
    deceased_boolean = False
    address_line = None
    address_city = None
    address_state = None
    address_postal_code = None
    address_country = None
    mother_given_name = None
    mother_family_name = None
    father_given_name = None
    father_family_name = None
    base_url = ""
    patient_endpoint = "{0}/Patient"
    patient_id_endpoint = "{0}/Patient/{1}"
    patient_match_endpoint = "{0}/Patient/$match"
    patient_definir_niu_endpoint = patient_id_endpoint + "/$definir-niu"

    base_headers = {
        "Content-type": "application/json+fhir"
    }
    headers = {}
    patient_template = """{
  "resourceType": "{{ ressource_type }}",
{% if id is defined and id is not none %}
  "id": "{{ id }}",
{% endif %}
  "identifier": [
{% if nam is defined and nam is not none %}
    {
      "extension": [
        {
          "url": "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#patient/healthcardorigin",
          "valueCodeableConcept": {
            "coding": [
              {
                "system": "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary",
                "version": "1.0.0",
                "code": "QC"
              }
            ]
          }
        }
      ],
      "type": {
        "coding": [
          {
            "system": "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary",
            "version": "1.0.0",
            "code": "NAM"
          }
        ]
      },
      "system": "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary/identifierType?code=NAM",
      "value": "{{ nam }}"
{% if niu is defined and niu is not none %}
    },
{% else %}
    }
{% endif %}
{% else %}
    {
      "type": {
        "coding": [
          {
            "system": "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary",
            "version": "1.0.0",
            "code": "AUCUN",
            "display": "Aucun identifiant"
          }
        ]
      },
      "system": "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary/identifierType?code=AUCUN"
{% if niu is defined and niu is not none %}
    },
{% else %}
    }
{% endif %}
{% endif %}
{% if niu is defined and niu is not none %}
    {
      "type": {
        "coding": [
          {
            "system": "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary",
            "version": "1.0.0",
            "code": "NIUU",
            "display": "NIU"
          }
        ]
      },
        "system": "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary/identifierType?code=NIUU",
        "value": "{{ niu }}"
      }
{% endif %}
  ],
  "active": {{ active | default('true') }},
{% if (family_name is defined and family_name is not none) or (given_name is defined and given_name is not none) %}
  "name": [
    {
{% if family_name is defined and family_name is not none %}
      "family": [
        "{{ family_name }}"
{% if given_name is defined and given_name is not none %}
      ],
{% else %}
      ]
{% endif %}
{% endif %}
{% if given_name is defined and given_name is not none %}
      "given": [
        "{{ given_name }}"
      ]
{% endif %}
    }
{% endif %}
  ],
{% if phone_number is defined and phone_number is not none %}
  "telecom": [
    {
      "system": "phone",
      "value": "+1{{ phone_number }}"
    }
  ],
{% endif %}
{% if gender is defined and gender is not none %}
  "gender": "{{ gender }}",
{% endif %}
{% if birth_date is defined and birth_date is not none %}
  "birthDate": "{{ birth_date }}",
{% endif %}
  "deceasedBoolean": {{ deceased_boolean | default('false') }},
{% if (address_line is defined and address_line is not none) or (address_city is defined and address_city is not none) or (address_state is defined and address_state is not none) or (address_postal_code is defined and address_postal_code is not none) or (address_country is defined and address_country is not none) %}
  "address": [
    {
{% if address_line is defined and address_line is not none %}    
      "line": [
        "{{ address_line }}"
{% if (address_city is defined and address_city is not none) or (address_state is defined and address_state is not none) or (address_postal_code is defined and address_postal_code is not none) or (address_country is defined and address_country is not none) %}
      ],
{% else %}
      ]
{% endif %}
{% endif %}
{% if address_city is defined and address_city is not none %}    
{% if (address_state is defined and address_state is not none) or (address_postal_code is defined and address_postal_code is not none) or (address_country is defined and address_country is not none) %}
      "city": "{{ address_city }}",
{% else %}
      "city": "{{ address_city }}"
{% endif %}
{% endif %}
{% if address_state is defined and address_state is not none %}    
{% if (address_postal_code is defined and address_postal_code is not none) or (address_country is defined and address_country is not none) %}
      "state": "{{ address_state }}",
{% else %}
      "state": "{{ address_state }}"
{% endif %}
{% endif %}
{% if address_postal_code is defined and address_postal_code is not none %}    
{% if address_country is defined and address_country is not none %}
      "postalCode": "{{ address_postal_code }}",
{% else %}
      "postalCode": "{{ address_postal_code }}"
{% endif %}
{% endif %}
{% if address_country is defined and address_country is not none %}    
      "country": "{{ address_country }}"
{% endif %}
    }
  ],
{% endif %}
  "contact": [
{% if mother_family_name is defined and mother_given_name is defined and mother_family_name is not none and mother_given_name is not none %}
    {
      "relationship": [
        {
          "coding": [
            {
              "system": "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary",
              "version": "1.0.0",
              "code": "MERE"
            }
          ]
        }
      ],
      "name": {
        "family": [
          "{{ mother_family_name }}"
        ],
        "given": [
          "{{ mother_given_name }}"
        ]
      }
{% if father_given_name is defined and father_family_name is defined and father_given_name is not none and father_family_name is not none %}
    },
{% else %}
    }
{% endif %}
{% endif %}
{% if father_given_name is defined and father_family_name is defined and father_given_name is not none and father_family_name is not none %}
    {
      "relationship": [
        {
          "coding": [
            {
              "system": "http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/vocabulary",
              "version": "1.0.0",
              "code": "PERE"
            }
          ]
        }
      ],
      "name": {
        "family": [
          "{{ father_family_name }}"
        ],
        "given": [
          "{{ father_given_name }}"
        ]
      }
    }
{% endif %}
  ]
}"""

    def __init__(self, base_url=None, patient_dict=None, token=None):
        if base_url is not None:
            self.base_url = base_url
        if patient_dict is not None:
            self.from_dict(patient_dict)
        self.setHeaders(token=token)

    def from_dict(self, patient_dict):
        self.id = patient_dict['id'] if 'id' in patient_dict else None
        self.given_name = patient_dict['given_name'] if 'given_name' in patient_dict else None
        self.family_name = patient_dict['family_name'] if 'family_name' in patient_dict else None
        self.active = patient_dict['active'] if 'active' in patient_dict else True
        self.gender = patient_dict['gender'] if 'gender' in patient_dict else None
        self.birth_date = patient_dict['birth_date'] if 'birth_date' in patient_dict else None
        self.niu = patient_dict['niu'] if 'niu' in patient_dict else None
        self.nam = patient_dict['nam'] if 'nam' in patient_dict else None
        self.address_line = patient_dict['address_line'] if 'address_line' in patient_dict else None
        self.address_city = patient_dict['address_city'] if 'address_city' in patient_dict else None
        self.address_state = patient_dict['address_state'] if 'address_state' in patient_dict else None
        self.address_postal_code = patient_dict['address_postal_code'] if 'address_postal_code' in patient_dict else None
        self.address_country = patient_dict['address_country'] if 'address_country' in patient_dict else None
        self.mother_given_name = patient_dict['mother_given_name'] if 'mother_given_name' in patient_dict else None
        self.mother_family_name = patient_dict['mother_family_name'] if 'mother_family_name' in patient_dict else None
        self.father_given_name = patient_dict['father_given_name'] if 'father_given_name' in patient_dict else None
        self.father_family_name = patient_dict['father_family_name'] if 'father_family_name' in patient_dict else None
        self.phone_number = patient_dict['phone_number'] if 'phone_number' in patient_dict else None

    def from_json(self, resource):
        data = json.loads(resource)
        self.id = data["id"] if "id" in data else None
        self.nam = None
        if 'identifier' in data:
            for identifier in data["identifier"]:
                if 'type' in identifier and "coding" in identifier["type"]:
                    for coding in identifier["type"]["coding"]:
                        if "code" in coding and coding["code"] == "NAM":
                            self.nam = identifier["value"]
                        elif "code" in coding and coding["code"] == "NIUU":
                            self.niu = identifier["value"]

        if 'extension' in data:
            matchramq_extension = list(filter(
                lambda ext: ext['url'] == 'http://www.santepublique.rtss.qc.ca/sipmi/fa/1.0.0/extensions/#patient/matchramq', data['extension']))
            self.matchramq = matchramq_extension[0]["valueBoolean"]
        self.active = False if 'active' in data and str(data['active']).lower() in [
            'false', 'faux', 'no', 'non'] else True
        self.family_name = data["name"][0]["family"][0] if 'name' in data and 'family' in data['name'][0] else None
        self.given_name = data["name"][0]["given"][0] if 'name' in data and 'given' in data['name'][0] else None
        self.phone_number = data["telecom"][0]["value"] if 'telecom' in data else None
        self.gender = data["gender"] if 'gender' in data else None
        self.birth_date = data["birthDate"] if 'birthDate' in data else None
        self.deceased_boolean = True if 'deceasedBoolean' in data and str(
            data["deceasedBoolean"]).lower() in ['true', 'vrai', 'yes', 'oui'] else False
        self.address_line = data["address"][0]["line"][0] if 'address' in data and 'line' in data["address"][0] else None
        self.address_city = data["address"][0]["city"] if 'address' in data and 'city' in data["address"][0] else None
        self.address_state = data["address"][0]["state"] if 'address' in data and 'state' in data["address"][0] else None
        self.address_postal_code = data["address"][0][
            "postalCode"] if 'address' in data and 'postalCode' in data["address"][0] else None
        self.address_country = data["address"][0]["country"] if 'address' in data and 'country' in data["address"][0] else None
        self.mother_family_name = None
        self.mother_given_name = None
        self.father_given_name = None
        self.father_family_name = None
        if "contact" in data:
            for contact in data["contact"]:
                if "relationship" in contact and "coding" in contact["relationship"][0]:
                    for coding in contact["relationship"][0]["coding"]:
                        if "code" in coding and coding["code"] == "MERE" and "name" in contact:
                            self.mother_family_name = contact["name"]["family"][
                                0] if "family" in contact["name"] else None
                            self.mother_given_name = contact["name"]["given"][0] if "given" in contact["name"] else None
                        elif "code" in coding and coding["code"] == "PERE" and "name" in contact:
                            self.father_family_name = contact["name"]["family"][
                                0] if "family" in contact["name"] else None
                            self.father_given_name = contact["name"]["given"][0] if "given" in contact["name"] else None

    def getFhirResource(self):
        template = Template(self.patient_template)
        strRes = template.render(
            ressource_type=self.resource_type,
            id=self.id,
            nam=self.nam,
            active=str(self.active).lower(),
            niu=self.niu,
            family_name=self.family_name,
            given_name=self.given_name,
            phone_number=self.phone_number,
            gender=self.gender,
            birth_date=self.birth_date,
            deceased_boolean=str(self.deceased_boolean).lower(),
            address_line=self.address_line,
            address_city=self.address_city,
            address_state=self.address_state,
            address_postal_code=self.address_postal_code,
            address_country=self.address_country,
            mother_family_name=self.mother_family_name,
            mother_given_name=self.mother_given_name,
            father_given_name=self.father_given_name,
            father_family_name=self.father_family_name)
        return json.loads(strRes)

    def getFhirResourceParameter(self):
        param = ParameterFHIR()
        #param.add_parameter(self.getFhirResource())
        param.add_parameter(self)
        return param.getFhirResource()

    def setHeaders(self, headers={}, token=None):
        newHeaders = {**headers, **self.base_headers}
        if token is not None:
            if 'Content-type' in token:
                del token['Content-type']
            if 'Content-Type' in token:
                del token['Content-Type']
            headersWithAuth = {**newHeaders, **token}
            self.headers = headersWithAuth
        else:
            self.headers = newHeaders
        return self.headers

    def Create(self):
        res = self.getFhirResource()
        response = requests.post(url=self.patient_endpoint.format(
            self.base_url), data=json.dumps(res), headers=self.headers)
        self.from_json(resource=response.content.decode())
        if self.niu is not None:
            res = self.getFhirResourceParameter()
            requests.post(url=self.patient_definir_niu_endpoint.format(
                self.base_url, self.id), data=json.dumps(res), headers=self.headers)
        return response

    def GetById(self, patient_id=None):
        response = requests.get(url=self.patient_id_endpoint.format(
            self.base_url, patient_id), headers=self.headers)
        self.from_json(resource=response.content.decode())
        return response

    def Match(self):
        res = self.getFhirResourceParameter()
        response = requests.post(url=self.patient_match_endpoint.format(
            self.base_url), data=json.dumps(res), headers=self.headers)
        if response.status_code == 200:
            parameter = json.loads(response.content.decode())
            if "parameter" in parameter and len(parameter["parameter"]) > 0 and "resource" in parameter["parameter"][0]:
                resource = json.dumps(parameter["parameter"][0]["resource"])
                self.from_json(resource=resource)
        return response

    def Search(self, identifier=None, given=None, family=None, gender=None, birthdate=None):
        params = {}
        if identifier is not None:
            params['identifier'] = identifier
        elif self.nam is not None:
            params['identifier'] = "code=NAM|{}".format(self.nam)
        if given is not None:
            params['given'] = given
        elif self.given_name is not None:
            params['given'] = self.given_name
        if family is not None:
            params['family'] = family
        elif self.family_name is not None:
            params['family'] = self.family_name
        if gender is not None:
            params['gender'] = gender
        elif self.gender is not None:
            params['gender'] = self.gender
        if birthdate is not None:
            params['birthdate'] = birthdate
        elif self.birth_date is not None:
            params['birthdate'] = self.birth_date
        response = requests.get(url=self.patient_endpoint.format(
            self.base_url), params=params, headers=self.headers)

        return response
