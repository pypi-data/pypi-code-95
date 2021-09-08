from localstack.utils.aws import aws_models
qiJaQ=super
qiJaC=None
qiJaf=id
class LambdaLayer(aws_models.LambdaFunction):
 def __init__(self,arn):
  qiJaQ(LambdaLayer,self).__init__(arn)
  self.cwd=qiJaC
  self.runtime=""
  self.handler=""
  self.envvars={}
  self.versions={}
class BaseComponent(aws_models.Component):
 def name(self):
  return self.qiJaf.split(":")[-1]
class RDSDatabase(BaseComponent):
 def __init__(self,qiJaf,env=qiJaC):
  qiJaQ(RDSDatabase,self).__init__(qiJaf,env=env)
class RDSCluster(BaseComponent):
 def __init__(self,qiJaf,env=qiJaC):
  qiJaQ(RDSCluster,self).__init__(qiJaf,env=env)
class AppSyncAPI(BaseComponent):
 def __init__(self,qiJaf,env=qiJaC):
  qiJaQ(AppSyncAPI,self).__init__(qiJaf,env=env)
class AmplifyApp(BaseComponent):
 def __init__(self,qiJaf,env=qiJaC):
  qiJaQ(AmplifyApp,self).__init__(qiJaf,env=env)
class ElastiCacheCluster(BaseComponent):
 def __init__(self,qiJaf,env=qiJaC):
  qiJaQ(ElastiCacheCluster,self).__init__(qiJaf,env=env)
class TransferServer(BaseComponent):
 def __init__(self,qiJaf,env=qiJaC):
  qiJaQ(TransferServer,self).__init__(qiJaf,env=env)
class CloudFrontDistribution(BaseComponent):
 def __init__(self,qiJaf,env=qiJaC):
  qiJaQ(CloudFrontDistribution,self).__init__(qiJaf,env=env)
class CodeCommitRepository(BaseComponent):
 def __init__(self,qiJaf,env=qiJaC):
  qiJaQ(CodeCommitRepository,self).__init__(qiJaf,env=env)
# Created by pyminifier (https://github.com/liftoff/pyminifier)
