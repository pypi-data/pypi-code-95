from llcsciencesdk.llc_api import ScienceSdk

llc_api = ScienceSdk(environment="staging")
llc_api.login("xxxx", "xxxx")
model_input = llc_api.get_model_inputs_json(11)
print(model_input)