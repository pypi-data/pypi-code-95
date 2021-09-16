from localstack.utils.aws import aws_models
trLxi=super
trLxK=None
trLxC=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  trLxi(LambdaLayer,self).__init__(arn)
  self.cwd=trLxK
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.trLxC.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,trLxC,env=trLxK):
  trLxi(RDSDatabase,self).__init__(trLxC,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,trLxC,env=trLxK):
  trLxi(RDSCluster,self).__init__(trLxC,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,trLxC,env=trLxK):
  trLxi(AppSyncAPI,self).__init__(trLxC,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,trLxC,env=trLxK):
  trLxi(AmplifyApp,self).__init__(trLxC,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,trLxC,env=trLxK):
  trLxi(ElastiCacheCluster,self).__init__(trLxC,env=env)
class TransferServer(BaseComponent):
 def __init__(self,trLxC,env=trLxK):
  trLxi(TransferServer,self).__init__(trLxC,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,trLxC,env=trLxK):
  trLxi(CloudFrontDistribution,self).__init__(trLxC,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,trLxC,env=trLxK):
  trLxi(CodeCommitRepository,self).__init__(trLxC,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
