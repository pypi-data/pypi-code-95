from localstack.utils.aws import aws_models
eIRbD=super
eIRbv=None
eIRbC=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  eIRbD(LambdaLayer,self).__init__(arn)
  self.cwd=eIRbv
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.eIRbC.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,eIRbC,env=eIRbv):
  eIRbD(RDSDatabase,self).__init__(eIRbC,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,eIRbC,env=eIRbv):
  eIRbD(RDSCluster,self).__init__(eIRbC,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,eIRbC,env=eIRbv):
  eIRbD(AppSyncAPI,self).__init__(eIRbC,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,eIRbC,env=eIRbv):
  eIRbD(AmplifyApp,self).__init__(eIRbC,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,eIRbC,env=eIRbv):
  eIRbD(ElastiCacheCluster,self).__init__(eIRbC,env=env)
class TransferServer(BaseComponent):
 def __init__(self,eIRbC,env=eIRbv):
  eIRbD(TransferServer,self).__init__(eIRbC,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,eIRbC,env=eIRbv):
  eIRbD(CloudFrontDistribution,self).__init__(eIRbC,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,eIRbC,env=eIRbv):
  eIRbD(CodeCommitRepository,self).__init__(eIRbC,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
