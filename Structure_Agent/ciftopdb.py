from Bio.PDB import MMCIFParser, PDBIO

parser = MMCIFParser()
structure = parser.get_structure("model", "Structure_Agent/A0A087X1C5.cif")

io = PDBIO()
io.set_structure(structure)
io.save("Structure_Agent/model_1.pdb")
