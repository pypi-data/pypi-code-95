import json
from pathlib import Path

from rasa.nlu.convert import convert_training_data

cvt = convert_training_data(
    "../../data/Online-Shopping", "./nlu.json", "json", language="en"
)

with open(Path("./nlu.json")) as f:
    data = json.load(f)

final_data = data["rasa_nlu_data"]

with open(Path("./dialog_to_ns.json"), "w") as f:
    json.dump(final_data, f, indent=4)

print(final_data)

#  ----  regex  ----
# list_of_values = []
# regex_entity = []
# language = "en"
# for values in final_data['regex_features']:
#     if values['name'] not in list_of_values:
#         list_of_values.append(values['name'])
#         regex_entity.append({"entity": values['name'],
#                              "examples": [],
#                              "language": language,
#                              "entityType": "regex"})
#     index = list_of_values.index(values['name'])
#     regex_entity[index]["examples"].append(values['pattern'])
# print("\n\n\n\n\n")
# print(regex_entity)

# lookups

# list_of_lookup = []
# language = "en"
# for values in final_data['lookup_tables']:
#     values['entity'] = values.pop('name')
#     values['examples'] = values.pop('elements')
#     values['language'] = language
#     values['entityType'] = "lookup"
#     list_of_lookup.append(values)
#
# print('\n\n\n\n\n')
# print(list_of_lookup)

# ---- synonyms ----
#
# language = "en"
# list_of_synonyms = []
# for values in final_data['entity_synonyms']:
#     values['entity'] = values.pop('value')
#     values['examples'] = values.pop('synonyms')
#     values['language'] = language
#     values['entityType'] = "synonym"
