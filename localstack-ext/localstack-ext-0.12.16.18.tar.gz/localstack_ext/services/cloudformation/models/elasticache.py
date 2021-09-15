from localstack.services.cloudformation.service_models import GenericBaseModel
AlJDW=staticmethod
AlJDK=None
AlJDv=super
AlJDR=Exception
AlJDG=len
AlJDw=str
AlJDm=classmethod
from localstack.utils.aws import aws_stack
class ElastiCacheSubnetGroup(GenericBaseModel):
 @AlJDW
 def cloudformation_type():
  return "AWS::ElastiCache::SubnetGroup"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("elasticache")
  groups=client.describe_cache_subnet_groups().get("CacheSubnetGroups",[])
  grp_name=self.resolve_refs_recursively(stack_name,self.props["CacheSubnetGroupName"],resources)
  result=[e for e in groups if e["CacheSubnetGroupName"]==grp_name]
  return(result or[AlJDK])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("CacheSubnetGroupName")
 @AlJDW
 def get_deploy_templates():
  return{"create":{"function":"create_cache_subnet_group","parameters":{"CacheSubnetGroupName":"CacheSubnetGroupName","CacheSubnetGroupDescription":"Description","SubnetIds":"SubnetIds","Tags":"Tags"}},"delete":{"function":"delete_cache_subnet_group","parameters":["CacheSubnetGroupName"]}}
class ElastiCacheReplicationGroup(GenericBaseModel):
 @AlJDW
 def cloudformation_type():
  return "AWS::ElastiCache::ReplicationGroup"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("elasticache")
  groups=client.describe_replication_groups().get("ReplicationGroups",[])
  grp_desc=self.resolve_refs_recursively(stack_name,self.props["ReplicationGroupDescription"],resources)
  result=[e for e in groups if e.get("Description")==grp_desc]
  return(result or[AlJDK])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("ReplicationGroupId")
 @AlJDW
 def get_deploy_templates():
  return{"create":{"function":"create_replication_group"},"delete":{"function":"delete_replication_group","parameters":["ReplicationGroupId"]}}
class ElastiCacheSecurityGroup(GenericBaseModel):
 @AlJDW
 def cloudformation_type():
  return "AWS::ElastiCache::SecurityGroup"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("elasticache")
  groups=client.describe_cache_security_groups().get("CacheSecurityGroups",[])
  grp_desc=self.resolve_refs_recursively(stack_name,self.props["Description"],resources)
  result=[e for e in groups if e["Description"]==grp_desc]
  return(result or[AlJDK])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("CacheSecurityGroupName")
 @AlJDW
 def get_deploy_templates():
  return{"create":{"function":"create_cache_security_group"},"delete":{"function":"delete_cache_security_group","parameters":["CacheSecurityGroupName"]}}
class ElastiCacheParameterGroup(GenericBaseModel):
 @AlJDW
 def cloudformation_type():
  return "AWS::ElastiCache::ParameterGroup"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("elasticache")
  groups=client.describe_cache_parameter_groups().get("CacheParameterGroups",[])
  grp_name=self.resolve_refs_recursively(stack_name,self.props["CacheParameterGroupName"],resources)
  result=[e for e in groups if e["CacheParameterGroupName"]==grp_name]
  return(result or[AlJDK])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("CacheParameterGroupName")
 @AlJDW
 def get_deploy_templates():
  def _param_values(params,**kwargs):
   props_dict=params.get("Properties")or{}
   return[{"ParameterName":n,"ParameterValue":v}for n,v in props_dict.items()]
  return{"create":[{"function":"create_cache_parameter_group","parameters":["CacheParameterGroupName","CacheParameterGroupFamily","Description","Tags"]},{"function":"modify_cache_parameter_group","parameters":{"CacheParameterGroupName":"CacheParameterGroupName","ParameterNameValues":_param_values}}],"delete":{"function":"delete_cache_parameter_group","parameters":["CacheParameterGroupName"]}}
class ElastiCacheCluster(GenericBaseModel):
 @AlJDW
 def cloudformation_type():
  return "AWS::ElastiCache::CacheCluster"
 def get_cfn_attribute(self,attribute_name):
  try:
   result=AlJDv(ElastiCacheCluster,self).get_cfn_attribute(attribute_name)
   assert result is not AlJDK
   return result
  except AlJDR:
   props=self.props
   if attribute_name in["Port","Address"]:
    attribute_name="RedisEndpoint.%s"%attribute_name
   parts=attribute_name.split(".")
   candidates=["ConfigurationEndpoint","RedisEndpoint","Endpoint"]
   if parts[0]in candidates and AlJDG(parts)>1:
    key_name="ConfigurationEndpoint"
    if not props.get(key_name):
     self.state=self.fetch_details(props.get("ClusterName"))
    parent_obj=self.state.get(parts[0])or self.state.get(key_name)or{}
    result=parent_obj.get(parts[1])or props.get(parts[1])
    return AlJDw(result)
   return props.get(attribute_name)
 @AlJDm
 def fetch_details(cls,cluster_name):
  client=aws_stack.connect_to_service("elasticache")
  clusters=client.describe_cache_clusters(MaxRecords=500).get("CacheClusters",[])
  match=[c for c in clusters if c.get("CacheClusterId")==cluster_name]
  return(match or[AlJDK])[0]
# Created by pyminifier (https://github.com/liftoff/pyminifier)
