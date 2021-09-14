from localstack.services.cloudformation.service_models import REF_ID_ATTRS,GenericBaseModel
zTaGM=staticmethod
zTaGN=None
from localstack.utils.aws import aws_stack
class CloudTrail(GenericBaseModel):
 @zTaGM
 def cloudformation_type():
  return "AWS::CloudTrail::Trail"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("cloudtrail")
  result=[t for t in client.list_trails()["Trails"]if t["Name"]==self.props["TrailName"]]
  return(result or[zTaGN])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  if attribute in REF_ID_ATTRS:
   return self.props["TrailName"]
 @zTaGM
 def get_deploy_templates():
  def put_event_selectors(resource_id,resources,*args,**kwargs):
   resource=resources[resource_id]
   props=resource.get("Properties",{})
   selectors=props.get("EventSelectors",[])
   if selectors:
    cloudtrail=aws_stack.connect_to_service("cloudtrail")
    cloudtrail.put_event_selectors(TrailName=props["TrailName"],EventSelectors=selectors)
   result={}
   return result
  return{"create":[{"function":"create_trail","parameters":{"Name":"TrailName","S3BucketName":"S3BucketName","S3KeyPrefix":"S3KeyPrefix","SnsTopicName":"SnsTopicName","IncludeGlobalServiceEvents":"IncludeGlobalServiceEvents","IsMultiRegionTrail":"IsMultiRegionTrail","EnableLogFileValidation":"EnableLogFileValidation","CloudWatchLogsLogGroupArn":"CloudWatchLogsLogGroupArn","CloudWatchLogsRoleArn":"CloudWatchLogsRoleArn","KmsKeyId":"KMSKeyId"}},{"function":put_event_selectors}],"delete":{"function":"delete_trail","parameters":{"Name":"TrailName"}}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
