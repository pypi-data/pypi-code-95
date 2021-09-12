import json
OUjnh=staticmethod
OUjnI=None
OUjnM=classmethod
OUjnW=type
from localstack.services.cloudformation.service_models import REF_ID_ATTRS,GenericBaseModel
from localstack.utils.aws import aws_stack
from localstack.utils.common import select_attributes,short_uid
class ApiGatewayV2VpcLink(GenericBaseModel):
 @OUjnh
 def cloudformation_type():
  return "AWS::ApiGatewayV2::VpcLink"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("apigatewayv2")
  links=client.get_vpc_links()["Items"]
  link_name=self.resolve_refs_recursively(stack_name,self.props["Name"],resources)
  result=[e for e in links if e["Name"]==link_name]
  return(result or[OUjnI])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("VpcLinkId")
 @OUjnh
 def get_deploy_templates():
  return{"create":{"function":"create_vpc_link"},"delete":{"function":"delete_vpc_link","parameters":["VpcLinkId"]}}
class ApiGatewayV2DomainName(GenericBaseModel):
 @OUjnh
 def cloudformation_type():
  return "AWS::ApiGatewayV2::DomainName"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("apigatewayv2")
  apis=client.get_domain_names()["Items"]
  domain_name=self.resolve_refs_recursively(stack_name,self.props["DomainName"],resources)
  result=([a for a in apis if a["DomainName"]==domain_name]or[OUjnI])[0]
  return result
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("DomainName")
 @OUjnh
 def get_deploy_templates():
  return{"create":{"function":"create_domain_name"},"delete":{"function":"delete_domain_name","parameters":["DomainName"]}}
class ApiGatewayV2Authorizer(GenericBaseModel):
 @OUjnh
 def cloudformation_type():
  return "AWS::ApiGatewayV2::Authorizer"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("apigatewayv2")
  props=self.props
  api_id=self.resolve_refs_recursively(stack_name,props["ApiId"],resources)
  auth_name=self.resolve_refs_recursively(stack_name,props["Name"],resources)
  apis=client.get_authorizers(ApiId=api_id)["Items"]
  result=([a for a in apis if a["Name"]==auth_name]or[OUjnI])[0]
  return result
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("AuthorizerId")
 @OUjnh
 def get_deploy_templates():
  return{"create":{"function":"create_authorizer"}}
class ApiGatewayV2Api(GenericBaseModel):
 @OUjnh
 def cloudformation_type():
  return "AWS::ApiGatewayV2::Api"
 def fetch_state(self,stack_name,resources):
  props=self.props
  api_name=(props["Body"].get("info",{}).get("title")if props.get("Body")else props["Name"])
  return self.fetch_details(api_name)
 @OUjnM
 def fetch_details(cls,api_name):
  client=aws_stack.connect_to_service("apigatewayv2")
  apis=client.get_apis()["Items"]
  result=([a for a in apis if a["Name"]==api_name]or[OUjnI])[0]
  return result
 def get_physical_resource_id(self,attribute,**kwargs):
  if attribute in REF_ID_ATTRS:
   return self.props.get("ApiId")
 @OUjnh
 def get_deploy_templates():
  def create_resource(resource_id,resources,resource_type,func,stack_name,*args):
   resource=resources[resource_id]
   resource_props=resource["Properties"]
   client=aws_stack.connect_to_service("apigatewayv2")
   body=resource_props.get("Body")
   if body:
    base_path=resource_props.get("Basepath")
    body.setdefault("info",{}).setdefault("title","api-%s"%short_uid())
    body=json.dumps(body)
    kwargs={"Basepath":base_path}if base_path else{}
    return client.import_api(Body=body,**kwargs)
   params=select_attributes(resource_props,("ApiKeySelectionExpression","CorsConfiguration","CredentialsArn","Description","DisableSchemaValidation","Name","ProtocolType","RouteKey","RouteSelectionExpression","Tags","Target","Version"))
   return client.create_api(**params)
  return{"create":{"function":create_resource}}
class ApiGatewayV2IntegrationResponse(GenericBaseModel):
 @OUjnh
 def cloudformation_type():
  return "AWS::ApiGatewayV2::IntegrationResponse"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("apigatewayv2")
  props=self.props
  api_id=self.resolve_refs_recursively(stack_name,props["ApiId"],resources)
  int_id=self.resolve_refs_recursively(stack_name,props["IntegrationId"],resources)
  resp_key=self.resolve_refs_recursively(stack_name,props["IntegrationResponseKey"],resources)
  responses=client.get_integration_responses(ApiId=api_id).get("Items",[])
  result=[r for r in responses if r["ApiId"]==api_id and r["IntegrationId"]==int_id and r["IntegrationResponseKey"]==resp_key]
  return(result or[OUjnI])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("IntegrationResponseId")
 @OUjnh
 def get_deploy_templates():
  return{"create":{"function":"create_integration_response"}}
class ApiGatewayV2Integration(GenericBaseModel):
 @OUjnh
 def cloudformation_type():
  return "AWS::ApiGatewayV2::Integration"
 def get_physical_resource_id(self,attribute,**kwargs):
  if attribute in REF_ID_ATTRS:
   return self.props.get("IntegrationId")
 @OUjnM
 def fetch_details(cls,api_id,OUjnW,method,uri=OUjnI):
  client=aws_stack.connect_to_service("apigatewayv2")
  resp=client.get_integrations(ApiId=api_id)
  if "Items" not in resp:
   return OUjnI
  integrations=[r for r in resp["Items"]if OUjnW==r.get("IntegrationType")and uri in[OUjnI,r.get("IntegrationUri")]and method in[OUjnI,r.get("IntegrationMethod")]]
  return(integrations or[OUjnI])[0]
class ApiGatewayV2Deployment(GenericBaseModel):
 @OUjnh
 def cloudformation_type():
  return "AWS::ApiGatewayV2::Deployment"
 def get_physical_resource_id(self,attribute,**kwargs):
  if attribute in REF_ID_ATTRS:
   return self.props.get("DeploymentId")
 @OUjnM
 def fetch_details(cls,api_id,stage_name,description):
  client=aws_stack.connect_to_service("apigatewayv2")
  apis=client.get_deployments(ApiId=api_id)["Items"]
  apis=[a for a in apis if a.get("StageName")==stage_name or a.get("Description")==description]
  return(apis or[OUjnI])[0]
class ApiGatewayV2Stage(GenericBaseModel):
 @OUjnh
 def cloudformation_type():
  return "AWS::ApiGatewayV2::Stage"
 @OUjnM
 def fetch_details(cls,api_id,stage_name):
  client=aws_stack.connect_to_service("apigatewayv2")
  return client.get_stage(ApiId=api_id,StageName=stage_name)or OUjnI
 def get_physical_resource_id(self,attribute,**kwargs):
  if attribute in REF_ID_ATTRS:
   return self.props.get("StageName")
class ApiGatewayV2RouteResponse(GenericBaseModel):
 @OUjnh
 def cloudformation_type():
  return "AWS::ApiGatewayV2::RouteResponse"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("apigatewayv2")
  props=self.props
  api_id=self.resolve_refs_recursively(stack_name,props["ApiId"],resources)
  route_id=self.resolve_refs_recursively(stack_name,props["RouteId"],resources)
  response_key=self.resolve_refs_recursively(stack_name,props["RouteResponseKey"],resources)
  responses=client.get_route_responses(ApiId=api_id,RouteId=route_id).get("Items",[])
  result=[r for r in responses if r["RouteResponseKey"]==response_key]
  return(result or[OUjnI])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("RouteResponseId")
 @OUjnh
 def get_deploy_templates():
  return{"create":{"function":"create_route_response"},"delete":{"function":"delete_route_response","parameters":["ApiId","RouteId","RouteResponseId"]}}
class ApiGatewayV2Route(GenericBaseModel):
 @OUjnh
 def cloudformation_type():
  return "AWS::ApiGatewayV2::Route"
 @OUjnM
 def fetch_details(cls,api_id,route_key):
  client=aws_stack.connect_to_service("apigatewayv2")
  routes=client.get_routes(ApiId=api_id).get("Items",[])
  result=[r for r in routes if r["RouteKey"]==route_key]
  return(result or[OUjnI])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("RouteId")
# Created by pyminifier (https://github.com/liftoff/pyminifier)
