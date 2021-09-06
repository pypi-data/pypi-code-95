palette = [
        ('frame_header', 'white', 'dark red', 'bold'),
        ('banner', 'black', 'light gray'),
        ('streak', 'black', 'dark red'),
        ('blue_background', 'black', 'dark blue'),
]

chemical_categories = {
        "Secondary metabolite": (["Alkaloids", "Flavonoids", "Furanocoumarins", "Phenylpropanoids", "Polyketides", "Polyphenols", "Polyynes", "Saponins", "Terpenes_and_terpenoids"], "Metabolites not involved in growth and reproduction", True),
        "Alklaoids": (["Anticholinergic_alkaloids", "Diterpene_alkaloids", "Guanidine_alkaloids", "Halogen-containing_alkaloids", "Indole_alkaloids", "Isoquinoline_alkaloids", "Phenethylamine_alkaloids", "Piperidine_alkaloids", "Pyridine_alkaloids", "Pyrrolidine_alkaloids", "Pyrrolizidine_alkaloids", "Quinoline_alkaloids", "Quinolizidine_alkaloids", "Quinuclidine_alkaloids", "Sesquiterpene_alkaloids", "Steroidal_alkaloids", "Tropane_alkaloids", "Tryptamine_alkaloids", "Xanthines"], "Nitrogenous base(amine)", True),
        "Phenylpropanoids": (["Coumarins", "Coumestans", "Flavonoids", "Phenylpropanoid_glycosides", "Hydroxycinnamic_acids", "Lignans", "Monolignols", "O-Methylated_phenylpropanoids", "Phenylpropanoids_metabolism", "Phenylpropenes", "Phenylpropionate_esters", "Stilbenoids"], "Phenyl + Propene tail", True),
        "Phenethylamines": (["2-Aminoindanes", "2-Benzylpiperidines", "2,5-Dimethoxyphenethylamines", "5-Benzofuranethanamines", "6-Benzofuranethanamines", "Aminotetralins", "Catecholamines", "Cathinones", "Diphenylethylpiperazines", "Phenethylamine_alkaloids", "Phenylethanolamines", "Psychedelic_phenethylamines", "Substituted_amphetamines", "Tetrahydroisoquinolines"], "Phenylethyl amines", True),
        "Apocynaceae alkaloids": (["Iboga alklaoid", "Vinca alkaloids"], "Alkaloids of Apocynaceae", False),
}
drug_categories = {
        "Acetylcholine_receptors": (["Anticholinergics", "Cholinergics"], "Drugs type on acetylcholine", False),
        "Musacarinic_acetylcholine_receptors": (["Musacarininc agonists", "Musacarinic antagonists"], "Musacarinic agonist/antagonist", False),
        "Nicotinic_acetylcholine_receptors": (["Nicotinic agonists", "Nicotinic antagonists"], "Nicotinic agonist/antagonist", False),
        "Adrenergic_receptors": (["Alpha blockers", "Alpha-adrenergic agonists", "Beta blockers", "Beta-adrenergic agonists"], "Adrenergic agonist/antagonist", False),
        "Dopamine_receptors": (["Dopamine agonists", "Dopamine antagonists"], "Dopamine agonist/antagonist", False),
        "GABA_receptors": (["GABA_receptor_agonists", "GABA_receptor_antagonists"], "GABA agonist/antagonist", False),
        "Ionotropic_glutamate_receptors": (["AMPA_receptor_agonists", " AMPA_receptor_antagonists", "Kainate_receptor_agonists", "Kainate receptor_antagonist", "NMDA_receptor_agonists", "NMDA_receptor_antagonists", "NMDA_receptor_modulators"], "Ionotropic glutamate agonist/antagonist", False),
        "Metabotropic_glutamate_receptors": (["Metabotropic glutamate receptor agonists", "Metabotropic glutamate receptor antagonists"], "Metabotropic glutamate receptor agonist/antagonist", False),
        "Histamine_receptors": (["Histamine agonists", "Antihistamines"], "Histamine agonist/antagonist", False),
        "Serotonin_receptors": (["Serotonin agonists", "Serotonin antagonists"], "Serotonin agonist/antagonist", False),
        "Opioid_receptors": (["Delta-opioid agonists", "Delta-opioid antagonists", "Kappa agonists", "Kappa antagonists", "Mu-opioid agonists", "Mu-opioid antagonists", "Noiciceptin receptor agonists", "Noiciceptin receptor antagonists"], "Opioid agonist/antagonist", False),
}
"""Later: "https://en.wikipedia.org/wiki/Category:Monoamine_releasing_agents", "https://en.wikipedia.org/wiki/Category:Reuptake_inhibitors" """ 
stubs = ['Alkaloid-stub']
