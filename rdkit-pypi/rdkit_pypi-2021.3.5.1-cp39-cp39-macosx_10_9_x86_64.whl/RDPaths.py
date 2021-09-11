import os
# unset so to trigger exceptions and track use: RDBaseDir=os.environ['RDBASE']
RDCodeDir=os.path.join(r'/private/var/folders/24/8k48jl6d249_n_qfxwsl6xvm0000gn/T/pip-req-build-5qxn53fs/build/temp.macosx-10.9-x86_64-3.9/rdkit_install/lib/python3.9/site-packages','rdkit')
# not really hard-coded alternative RDCodeDir=os.path.dirname(__file__)
_share = os.path.dirname(__file__)
RDDataDir=os.path.join(_share,'Data')
RDDocsDir=os.path.join(_share,'Docs')
RDProjDir=os.path.join(_share,'Projects')
RDContribDir=os.path.join(_share,'Contrib')
