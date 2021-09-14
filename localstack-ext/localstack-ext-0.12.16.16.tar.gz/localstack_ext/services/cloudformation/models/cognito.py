from localstack.constants import TEST_AWS_ACCOUNT_ID
yxODY=staticmethod
yxODd=super
yxODq=classmethod
yxODT=None
yxODG=int
yxODu=isinstance
yxODJ=str
yxODI=Exception
yxODh=True
from localstack.services.cloudformation.service_models import(REF_ATTRS,REF_ID_ATTRS,GenericBaseModel)
from localstack.utils.aws import aws_stack
from localstack_ext.services.cognito.cognito_idp_api import get_issuer_url
from localstack_ext.utils.aws import aws_utils
class CognitoUserPool(GenericBaseModel):
 @yxODY
 def cloudformation_type():
  return "AWS::Cognito::UserPool"
 def get_cfn_attribute(self,attribute_name):
  if attribute_name in REF_ATTRS:
   return self.get_physical_resource_id(attribute_name)
  pool_id=self._get_id()
  if attribute_name=="Arn":
   return aws_utils.cognito_userpool_arn(pool_id)
  if attribute_name=="ProviderName":
   return "cognito-idp.{r}.amazonaws.com/{r}_{a}".format(r=aws_stack.get_region(),a=TEST_AWS_ACCOUNT_ID)
  if attribute_name=="ProviderURL":
   return get_issuer_url(pool_id=pool_id)
  return yxODd(CognitoUserPool,self).get_cfn_attribute(attribute_name)
 def get_physical_resource_id(self,attribute,**kwargs):
  pool_id=self._get_id()
  if not pool_id:
   return pool_id
  if attribute in REF_ATTRS:
   return pool_id
  return aws_utils.cognito_userpool_arn(pool_id)
 def get_resource_name(self):
  return self.props.get("PoolName")
 def _get_id(self):
  props=self.props
  return props.get("UserPoolId")or props.get("Id")
 @yxODq
 def fetch_details(cls,pool_name):
  client=aws_stack.connect_to_service("cognito-idp")
  pools=client.list_user_pools(MaxResults=100)["UserPools"]
  return([p for p in pools if p["Name"]==pool_name]or[yxODT])[0]
 def get_deploy_templates():
  def get_user_pool_params(params,**kwargs):
   attr_list=["Policies","LambdaConfig","AutoVerifiedAttributes","AliasAttributes","UsernameAttributes","VerificationMessageTemplate","EmailVerificationMessage","EmailVerificationSubject","SmsVerificationMessage","SmsAuthenticationMessage","DeviceConfiguration","EmailConfiguration","SmsConfiguration","UserPoolTags","AdminCreateUserConfig","Schema","UserPoolAddOns"]
   attr_map={attr:attr for attr in attr_list}
   attr_map["PoolName"]="UserPoolName"
   result={k:params.get(v)for k,v in attr_map.items()}
   policies=result.get("Policies")or{}
   if(policies.get("PasswordPolicy")or{}).get("MinimumLength"):
    policies["PasswordPolicy"]["MinimumLength"]=yxODG(policies["PasswordPolicy"]["MinimumLength"])
   if yxODu(result.get("AutoVerifiedAttributes"),yxODJ):
    result["AutoVerifiedAttributes"]=[result["AutoVerifiedAttributes"]]
   for schema_attr in result.get("Schema")or[]:
    attr_constr=schema_attr.get("StringAttributeConstraints")
    if attr_constr:
     attr_constr["MinLength"]=yxODJ(attr_constr.get("MinLength",1))
     attr_constr["MaxLength"]=yxODJ(attr_constr.get("MaxLength",50))
   return result
  return{"create":{"function":"create_user_pool","parameters":get_user_pool_params}}
class UserPoolGroup(GenericBaseModel):
 @yxODY
 def cloudformation_type():
  return "AWS::Cognito::UserPoolGroup"
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("GroupName")
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("cognito-idp")
  props=self.props
  group_name=self.resolve_refs_recursively(stack_name,props.get("GroupName"),resources)
  pool_id=self.resolve_refs_recursively(stack_name,props.get("UserPoolId"),resources)
  groups=client.list_groups(UserPoolId=pool_id)["Groups"]
  result=[g for g in groups if g["GroupName"]==group_name]
  return(result or[yxODT])[0]
 @yxODY
 def get_deploy_templates():
  return{"create":{"function":"create_group"},"delete":{"function":"delete_group","parameters":["GroupName","UserPoolId"]}}
class IdentityPool(GenericBaseModel):
 @yxODY
 def cloudformation_type():
  return "AWS::Cognito::IdentityPool"
 def get_cfn_attribute(self,attribute_name):
  try:
   return yxODd(IdentityPool,self).get_cfn_attribute(attribute_name)
  except yxODI:
   if attribute_name in REF_ID_ATTRS:
    return self.get_physical_resource_id(attribute_name)
   if attribute_name=="ProviderName":
    return "cognito.{r}.amazonaws.com/{r}_{a}".format(r=aws_stack.get_region(),a=TEST_AWS_ACCOUNT_ID)
   raise
 def get_physical_resource_id(self,attribute,**kwargs):
  if attribute in REF_ID_ATTRS:
   return self.props.get("IdentityPoolId")
 @yxODq
 def fetch_details(cls,pool_name):
  client=aws_stack.connect_to_service("cognito-identity")
  pools=client.list_identity_pools(MaxResults=100)["IdentityPools"]
  result=[p for p in pools if p["IdentityPoolName"]==pool_name]
  return(result or[yxODT])[0]
class CognitoUserPoolClient(GenericBaseModel):
 @yxODY
 def cloudformation_type():
  return "AWS::Cognito::UserPoolClient"
 def get_cfn_attribute(self,attribute_name):
  if attribute_name in REF_ID_ATTRS:
   return self.get_physical_resource_id(attribute_name)
  return yxODd(CognitoUserPoolClient,self).get_cfn_attribute(attribute_name)
 def get_physical_resource_id(self,attribute,**kwargs):
  if attribute in REF_ID_ATTRS:
   return self.props.get("ClientId")
 @yxODq
 def fetch_details(cls,pool_id,client_name):
  client=aws_stack.connect_to_service("cognito-idp")
  clients=client.list_user_pool_clients(UserPoolId=pool_id)["UserPoolClients"]
  return([c for c in clients if c["ClientName"]==client_name]or[yxODT])[0]
class CognitoUserPoolDomain(GenericBaseModel):
 @yxODY
 def cloudformation_type():
  return "AWS::Cognito::UserPoolDomain"
 def get_physical_resource_id(self,attribute,**kwargs):
  if attribute in REF_ID_ATTRS:
   return self.props.get("Domain")
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("cognito-idp")
  domain_name=self.resolve_refs_recursively(stack_name,self.props.get("Domain"),resources)
  domain=client.describe_user_pool_domain(Domain=domain_name)["DomainDescription"]
  return domain or yxODT
 @yxODY
 def get_deploy_templates():
  return{"create":{"function":"create_user_pool_domain"},"delete":{"function":"delete_user_pool_domain","parameters":{"UserPoolId":"UserPoolId","Domain":"Domain"}}}
class CognitoIdentityPoolRoleAttachment(GenericBaseModel):
 @yxODY
 def cloudformation_type():
  return "AWS::Cognito::IdentityPoolRoleAttachment"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("cognito-identity")
  pool_id=self.resolve_refs_recursively(stack_name,self.props.get("IdentityPoolId"),resources)
  roles=client.get_identity_pool_roles(IdentityPoolId=pool_id)
  if roles:
   roles["_deployed"]=yxODh
  return roles or yxODT
 def get_physical_resource_id(self,attribute,**kwargs):
  props=self.props
  return props.get("_deployed")and "cognito-pool-roles-%s"%props.get("IdentityPoolId")
 @yxODY
 def get_deploy_templates():
  return{"create":{"function":"set_identity_pool_roles"}}
class CognitoUserPoolIdentityProvider(GenericBaseModel):
 @yxODY
 def cloudformation_type():
  return "AWS::Cognito::UserPoolIdentityProvider"
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("ProviderName")
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("cognito-idp")
  props=self.props
  pool_id=self.resolve_refs_recursively(stack_name,props.get("UserPoolId"),resources)
  prov_name=self.resolve_refs_recursively(stack_name,props.get("ProviderName"),resources)
  providers=client.list_identity_providers(UserPoolId=pool_id)["Providers"]
  provider=[p for p in providers if p["ProviderName"]==prov_name]
  return(provider or[yxODT])[0]
 @yxODY
 def get_deploy_templates():
  return{"create":{"function":"create_identity_provider"},"delete":{"function":"delete_identity_provider","parameters":{"UserPoolId":"UserPoolId","ProviderName":"ProviderName"}}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
