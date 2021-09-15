from localstack.utils.aws import aws_models
kDzVM=super
kDzVf=None
kDzVP=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  kDzVM(LambdaLayer,self).__init__(arn)
  self.cwd=kDzVf
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.kDzVP.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,kDzVP,env=kDzVf):
  kDzVM(RDSDatabase,self).__init__(kDzVP,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,kDzVP,env=kDzVf):
  kDzVM(RDSCluster,self).__init__(kDzVP,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,kDzVP,env=kDzVf):
  kDzVM(AppSyncAPI,self).__init__(kDzVP,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,kDzVP,env=kDzVf):
  kDzVM(AmplifyApp,self).__init__(kDzVP,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,kDzVP,env=kDzVf):
  kDzVM(ElastiCacheCluster,self).__init__(kDzVP,env=env)
class TransferServer(BaseComponent):
 def __init__(self,kDzVP,env=kDzVf):
  kDzVM(TransferServer,self).__init__(kDzVP,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,kDzVP,env=kDzVf):
  kDzVM(CloudFrontDistribution,self).__init__(kDzVP,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,kDzVP,env=kDzVf):
  kDzVM(CodeCommitRepository,self).__init__(kDzVP,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
