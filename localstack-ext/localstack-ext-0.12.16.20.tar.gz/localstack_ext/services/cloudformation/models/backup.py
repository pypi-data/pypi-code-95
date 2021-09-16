from localstack.services.cloudformation.service_models import GenericBaseModel
SysWt=staticmethod
SysWF=None
from localstack.utils.aws import aws_stack
class BackupPlan(GenericBaseModel):
 @SysWt
 def cloudformation_type():
  return "AWS::Backup::BackupPlan"
 def fetch_state(self,stack_name,resources):
  client=aws_stack.connect_to_service("backup")
  plans=client.list_backup_plans().get("BackupPlansList",[])
  plan_name=self.resolve_refs_recursively(stack_name,self.props["BackupPlanName"],resources)
  result=[p for p in plans if p["BackupPlanName"]==plan_name]
  return(result or[SysWF])[0]
 def get_physical_resource_id(self,attribute,**kwargs):
  return self.props.get("BackupPlanId")
 @SysWt
 def get_deploy_templates():
  return{"create":{"function":"create_backup_plan"},"delete":{"function":"delete_backup_plan","parameters":["BackupPlanId"]}}
# Created by pyminifier (https://github.com/liftoff/pyminifier)
