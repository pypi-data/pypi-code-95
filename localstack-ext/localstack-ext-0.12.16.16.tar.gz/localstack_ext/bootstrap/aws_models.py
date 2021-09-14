from localstack.utils.aws import aws_models
ERtMu=super
ERtMV=None
ERtMJ=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  ERtMu(LambdaLayer,self).__init__(arn)
  self.cwd=ERtMV
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.ERtMJ.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,ERtMJ,env=ERtMV):
  ERtMu(RDSDatabase,self).__init__(ERtMJ,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,ERtMJ,env=ERtMV):
  ERtMu(RDSCluster,self).__init__(ERtMJ,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,ERtMJ,env=ERtMV):
  ERtMu(AppSyncAPI,self).__init__(ERtMJ,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,ERtMJ,env=ERtMV):
  ERtMu(AmplifyApp,self).__init__(ERtMJ,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,ERtMJ,env=ERtMV):
  ERtMu(ElastiCacheCluster,self).__init__(ERtMJ,env=env)
class TransferServer(BaseComponent):
 def __init__(self,ERtMJ,env=ERtMV):
  ERtMu(TransferServer,self).__init__(ERtMJ,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,ERtMJ,env=ERtMV):
  ERtMu(CloudFrontDistribution,self).__init__(ERtMJ,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,ERtMJ,env=ERtMV):
  ERtMu(CodeCommitRepository,self).__init__(ERtMJ,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
