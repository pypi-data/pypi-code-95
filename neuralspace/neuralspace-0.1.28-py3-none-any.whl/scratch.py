from rasa.shared.importers.utils import training_data_from_paths

data = training_data_from_paths(["example_rasa_bot/data/nlu.yml"], language="en")
examples = []
entity = []

for ex in data.nlu_examples:
    examples.append(ex.as_dict())


# -- lookup --
# lookup = data.lookup_tables
# list_of_lookups = []
# language = "en"
# for value in lookup:
#     value['entity'] = value.pop('name')
#     value['examples'] = value.pop('elements')
#     value['language'] = language
#     value['entityType'] = "lookup"
#     list_of_lookups.append(value)
# print(list_of_lookups)


# -- regex --
# regex = data.regex_features
# language = "en"
# list_of_regex = []
# list_of_values = []
# for value in regex:
#     if value['name'] not in list_of_values:
#         list_of_values.append(value['name'])
#         value['entity'] = value.pop('name')
#         value['examples'] = [value.pop('pattern')]
#         value['language'] = language
#         value['entityType'] = "regex"
#         list_of_regex.append(value)
#     else:
#         index = list_of_values.index(value['name'])
#         list_of_regex[index]['examples'].append(value['pattern'])


# -- synonym --
# synonyms = data.entity_synonyms
# keys = list(synonyms.keys())
# print(synonyms.values())
# language = "en"
# list_of_synonyms = []
# list_of_values = []
# for value, key in zip(synonyms.values(), list(synonyms.keys())):
#     if value not in list_of_values:
#         list_of_values.append(value)
#         list_of_synonyms.append({"entity": value,
#                                  "examples": [],
#                                  "language": language,
#                                  "entityType": "synonym"})
#
#     index = list_of_values.index(value)
#     list_of_synonyms[index]["examples"].append(key)
# print(list_of_synonyms)


# #
# entitity = data.regex_features
# print(entitity)
#
# with open("./converted_dataset/rasa_to_ns.json", 'w') as f:
#     json.dump(
#         examples, f, indent=4
#     )
# with open("./converted_dataset/entity.json", 'w') as f:
#     json.dump(
#         entitity, f, indent=4
#     )

# cvt = convert_training_data('../../data/sample', "./nlu.json", 'json', language='en')
