from dg_ai_platform.example import HelloWorld
from dg_ai_platform.dg_platform import CaldronAI

ca = CaldronAI(HelloWorld, 'pid', 'pky')
ca.run()