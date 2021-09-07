from localstack.utils.aws import aws_models
yHKBo=super
yHKBO=None
yHKBc=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  yHKBo(LambdaLayer,self).__init__(arn)
  self.cwd=yHKBO
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.yHKBc.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,yHKBc,env=yHKBO):
  yHKBo(RDSDatabase,self).__init__(yHKBc,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,yHKBc,env=yHKBO):
  yHKBo(RDSCluster,self).__init__(yHKBc,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,yHKBc,env=yHKBO):
  yHKBo(AppSyncAPI,self).__init__(yHKBc,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,yHKBc,env=yHKBO):
  yHKBo(AmplifyApp,self).__init__(yHKBc,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,yHKBc,env=yHKBO):
  yHKBo(ElastiCacheCluster,self).__init__(yHKBc,env=env)
class TransferServer(BaseComponent):
 def __init__(self,yHKBc,env=yHKBO):
  yHKBo(TransferServer,self).__init__(yHKBc,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,yHKBc,env=yHKBO):
  yHKBo(CloudFrontDistribution,self).__init__(yHKBc,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,yHKBc,env=yHKBO):
  yHKBo(CodeCommitRepository,self).__init__(yHKBc,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
