import os
# unset so to trigger exceptions and track use: RDBaseDir=os.environ['RDBASE']
RDCodeDir=os.path.join(r'/tmp/pip-req-build-lhykq60r/build/temp.linux-x86_64-3.8/rdkit_install/lib/python3.8/site-packages','rdkit')
# not really hard-coded alternative RDCodeDir=os.path.dirname(__file__)
_share = os.path.dirname(__file__)
RDDataDir=os.path.join(_share,'Data')
RDDocsDir=os.path.join(_share,'Docs')
RDProjDir=os.path.join(_share,'Projects')
RDContribDir=os.path.join(_share,'Contrib')
