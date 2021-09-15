from localstack.utils.aws import aws_models
OVfnK=super
OVfnX=None
OVfnu=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  OVfnK(LambdaLayer,self).__init__(arn)
  self.cwd=OVfnX
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.OVfnu.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,OVfnu,env=OVfnX):
  OVfnK(RDSDatabase,self).__init__(OVfnu,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,OVfnu,env=OVfnX):
  OVfnK(RDSCluster,self).__init__(OVfnu,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,OVfnu,env=OVfnX):
  OVfnK(AppSyncAPI,self).__init__(OVfnu,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,OVfnu,env=OVfnX):
  OVfnK(AmplifyApp,self).__init__(OVfnu,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,OVfnu,env=OVfnX):
  OVfnK(ElastiCacheCluster,self).__init__(OVfnu,env=env)
class TransferServer(BaseComponent):
 def __init__(self,OVfnu,env=OVfnX):
  OVfnK(TransferServer,self).__init__(OVfnu,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,OVfnu,env=OVfnX):
  OVfnK(CloudFrontDistribution,self).__init__(OVfnu,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,OVfnu,env=OVfnX):
  OVfnK(CodeCommitRepository,self).__init__(OVfnu,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
