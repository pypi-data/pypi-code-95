from localstack.utils.aws import aws_models
mKOaf=super
mKOaC=None
mKOaL=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  mKOaf(LambdaLayer,self).__init__(arn)
  self.cwd=mKOaC
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.mKOaL.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,mKOaL,env=mKOaC):
  mKOaf(RDSDatabase,self).__init__(mKOaL,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,mKOaL,env=mKOaC):
  mKOaf(RDSCluster,self).__init__(mKOaL,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,mKOaL,env=mKOaC):
  mKOaf(AppSyncAPI,self).__init__(mKOaL,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,mKOaL,env=mKOaC):
  mKOaf(AmplifyApp,self).__init__(mKOaL,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,mKOaL,env=mKOaC):
  mKOaf(ElastiCacheCluster,self).__init__(mKOaL,env=env)
class TransferServer(BaseComponent):
 def __init__(self,mKOaL,env=mKOaC):
  mKOaf(TransferServer,self).__init__(mKOaL,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,mKOaL,env=mKOaC):
  mKOaf(CloudFrontDistribution,self).__init__(mKOaL,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,mKOaL,env=mKOaC):
  mKOaf(CodeCommitRepository,self).__init__(mKOaL,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
