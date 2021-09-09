import json
#import .fs_tools as fs_tools

def is_json(json_text):
  try:
    json_object = json.loads(json_text)
  except ValueError:
    return False
  return True    
  
def parse_json_text(body=None, return_fmt="dict"):
    assert return_fmt in ["dict", "text"], f"return_fmt [{return_fmt}] has to be either dict or text"
    
    if body is None: return body
    
    body_data = None
    body_text = None
    
    if type(body).__name__ == "str":
      assert is_json(body) == True, f"body is not json text"
      body_data = json.loads(body)
      body_text = pretty_json(body)
    elif type(body).__name__ == "dict":
      body_data = body
      body_text = pretty_json(body)      
    else:
      assert 1==0, f"invalid body type : {type(body).__name__}"
    
    if return_fmt == "dict" : return body_data
    if return_fmt == "text" : return body_text
      


def load_json(json_file):
  with open(json_file , encoding='utf-8') as json_fh:
    config = json.load(json_fh)
  return config    


def pretty_json(json_input) :
  if type(json_input).__name__ == "str" :
    return (json.dumps(json.loads(json_input), sort_keys=True, indent=2))
  
  if type(json_input).__name__ == "dict" :
    return (json.dumps(json_input, sort_keys=True, indent=2))
  
if __name__ == "__main__": 
  a  = '{"a":6}'
  a  = {"a":6}
  print (parse_json_text(body=a, return_fmt="text"))
  
  
  print 
  pass