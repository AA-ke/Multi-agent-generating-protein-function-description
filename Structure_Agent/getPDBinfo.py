from Bio.PDB import PDBParser, DSSP
import biotite.structure as struc
import biotite.structure.io as bsio
import os

def extract_structure_features(pdb_file):
    # 1. 基本信息
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("protein", pdb_file)
    model = structure[0]
    chains = list(model.get_chains())
    num_chains = len(chains)
    chain_ids = [chain.id for chain in chains]
    residues = [res for res in model.get_residues() if res.get_id()[0] == ' ']
    num_residues = len(residues)

    # 2. pLDDT均值
    struct = bsio.load_structure(pdb_file, extra_fields=["b_factor"])
    plddt_mean = struct.b_factor.mean()

    # 3. 二级结构比例（需DSSP和mkdssp可用）
    try:
        dssp = DSSP(model, pdb_file)
        helix = sum(1 for aa in dssp if aa[2] in ('H', 'G', 'I'))  # α-螺旋
        sheet = sum(1 for aa in dssp if aa[2] in ('E', 'B'))        # β-折叠
        coil = sum(1 for aa in dssp if aa[2] == ' ')                # 无规卷曲
        total = len(dssp)
        helix_percent = helix / total * 100
        sheet_percent = sheet / total * 100
        coil_percent = coil / total * 100
    except Exception as e:
        helix_percent = sheet_percent = coil_percent = None

    # 4. 二硫键数量
    disulfide_bonds = 0
    cys_atoms = [atom for atom in struct if atom.element == "S" and atom.res_name == "CYS"]
    # 简单统计，严格方法需空间距离判断
    if len(cys_atoms) >= 2:
        # 以5Å为阈值判断S-S键
        for i in range(len(cys_atoms)):
            for j in range(i+1, len(cys_atoms)):
                if (cys_atoms[i].coord - cys_atoms[j].coord).sum()**2 < 25:
                    disulfide_bonds += 1

    # 5. 疏水/亲水残基比例
    hydrophobic = {"ALA","VAL","ILE","LEU","MET","PHE","TRP","PRO"}
    hydrophilic = {"ARG","ASN","ASP","GLN","GLU","HIS","LYS","SER","THR","TYR","CYS"}
    hydrophobic_count = sum(1 for res in residues if res.get_resname() in hydrophobic)
    hydrophilic_count = sum(1 for res in residues if res.get_resname() in hydrophilic)
    hydrophobic_ratio = hydrophobic_count / num_residues * 100
    hydrophilic_ratio = hydrophilic_count / num_residues * 100

    return {
        "num_chains": num_chains,
        "chain_ids": chain_ids,
        "num_residues": num_residues,
        "plddt_mean": plddt_mean,
        "helix_percent": helix_percent,
        "sheet_percent": sheet_percent,
        "coil_percent": coil_percent,
        "disulfide_bonds": disulfide_bonds,
        "hydrophobic_ratio": hydrophobic_ratio,
        "hydrophilic_ratio": hydrophilic_ratio
    }

def find_metal_binding_sites(pdb_file):
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("protein", pdb_file)
    metals = []
    for model in structure:
        for chain in model:
            for residue in chain:
                if residue.id[0] == "H":  # HETATM
                    resname = residue.get_resname()
                    if resname in ["ZN", "MG", "CA", "FE", "CU", "MN", "CO", "NI"]:
                        metals.append((resname, chain.id, residue.id[1]))
    return metals

def calc_surface_area_and_volume(pdb_file):
    struct = bsio.load_structure(pdb_file)
    # 计算表面积
    area = struc.sasa(struct)
    total_area = area.sum()
    # 体积估算（粗略，精确需用MSMS等工具）
    atom_volumes = {"C": 20.6, "N": 15.6, "O": 14.7, "S": 33.5, "H": 5.2}
    total_volume = sum(atom_volumes.get(atom.element, 18.0) for atom in struct)
    return total_area, total_volume

def structure_features_to_text(features, metals, area, volume):
    text = f"该蛋白包含{features['num_chains']}条链（链ID: {', '.join(features['chain_ids'])}），共{features['num_residues']}个氨基酸残基。"
    text += f" 结构预测平均pLDDT置信度为{features['plddt_mean']:.1f}。"
    if features['helix_percent'] is not None:
        text += f" 二级结构组成：α-螺旋占比{features['helix_percent']:.1f}%，β-折叠占比{features['sheet_percent']:.1f}%，无规卷曲占比{features['coil_percent']:.1f}%。"
    text += f" 疏水性残基占比{features['hydrophobic_ratio']:.1f}%，亲水性残基占比{features['hydrophilic_ratio']:.1f}%。"
    text += f" 检测到二硫键数：{features['disulfide_bonds']}。"
    if metals:
        text += f" 检测到金属结合位点：{', '.join([f'{m[0]}(链{m[1]} 残基{m[2]})' for m in metals])}。"
    text += f" 分子表面积约为{area:.1f} Å²，体积约为{volume:.1f} Å³。"
    return text


pdb_file = "Structure_Agent/result.pdb"
features = extract_structure_features(pdb_file)
metals = find_metal_binding_sites(pdb_file)
area, volume = calc_surface_area_and_volume(pdb_file)
print(structure_features_to_text(features, metals, area, volume))

from dotenv import load_dotenv
from google import genai


load_dotenv()
google_client = genai.Client()

seq = "MASGQGPGPPRQECGEPALPSASEEQVAQDTEEVFRSYVFYRHQQEQEAEGVAAPADPEMVTLPLQPSSTMGQVGRQLAIIGDDINRRYDSEFQTMLQHLQPTAENAYEYFTKIATSLFESGINWGRVVALLGFGYRLALHVYQHGLTGFLGQVTRFVVDFMLHHCIARWIAQRGGWVAALNLGNGPILNVLVVLGVVLLGQFVVRRFFKS"

def generate(query_seq, docs) -> str:

    prompt = f"""
    你是一名蛋白质结构专家，请根据以下蛋白的结构信息进行功能预测：

    蛋白质序列：
    {query_seq}

    蛋白质结构信息：
    {docs}

    总结此蛋白可能的功能、参与的通路、结构域和潜在疾病联系。
    """

    print(f"{prompt}\n\n---\n")

    response = google_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text


answer = generate(seq,structure_features_to_text(features, metals, area, volume))
print(answer)