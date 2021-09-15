from localstack.utils.aws import aws_models
zsjmB=super
zsjmi=None
zsjmg=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  zsjmB(LambdaLayer,self).__init__(arn)
  self.cwd=zsjmi
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.zsjmg.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,zsjmg,env=zsjmi):
  zsjmB(RDSDatabase,self).__init__(zsjmg,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,zsjmg,env=zsjmi):
  zsjmB(RDSCluster,self).__init__(zsjmg,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,zsjmg,env=zsjmi):
  zsjmB(AppSyncAPI,self).__init__(zsjmg,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,zsjmg,env=zsjmi):
  zsjmB(AmplifyApp,self).__init__(zsjmg,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,zsjmg,env=zsjmi):
  zsjmB(ElastiCacheCluster,self).__init__(zsjmg,env=env)
class TransferServer(BaseComponent):
 def __init__(self,zsjmg,env=zsjmi):
  zsjmB(TransferServer,self).__init__(zsjmg,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,zsjmg,env=zsjmi):
  zsjmB(CloudFrontDistribution,self).__init__(zsjmg,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,zsjmg,env=zsjmi):
  zsjmB(CodeCommitRepository,self).__init__(zsjmg,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
