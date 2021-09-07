from easy3dmol import view
from rdkit import Chem
from rdkit.Chem import AllChem

a = view()
m = Chem.AddHs(Chem.MolFromSmiles("C"))
AllChem.EmbedMolecule(m)
m = Chem.MolToMolBlock(m)
a.add.Model(m, format="mol")
a.view()
print(a.js())
