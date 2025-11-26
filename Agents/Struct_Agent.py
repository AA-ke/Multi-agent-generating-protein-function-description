import requests
from Bio.PDB import PDBParser, DSSP
import biotite.structure as struc
import biotite.structure.io as bsio
import os
from math import sqrt

def get_pdb(seq):
    url = "https://api.esmatlas.com/foldSequence/v1/pdb/"
    os.makedirs("Structure_Agent", exist_ok=True)
    fallback_pdb = "Structure_Agent/model_1.pdb"
    # 长度>400时截断并记录标记
    truncated_flag_path = "Structure_Agent/.truncated"
    original_len = len(seq)
    if original_len > 400:
        try:
            with open(truncated_flag_path, "w") as f:
                f.write(str(original_len))
        except Exception:
            pass
        seq = seq[:400]
    else:
        if os.path.exists(truncated_flag_path):
            try:
                os.remove(truncated_flag_path)
            except Exception:
                pass
    try:
        response = requests.post(url, data=seq)
        if not response.ok:
            raise RuntimeError(f"ESM Atlas API request failed: {response.status_code} {response.text[:200]}")
        text = response.text
        # 有些情况下服务端返回错误页，但HTTP 200，需检测关键字
        if "Service Temporarily Unavailable" in text or "<html" in text.lower():
            raise RuntimeError("ESM Atlas API returned an error page content.")
        # 简单有效性检查：必须包含 ATOM 记录
        if "ATOM" not in text:
            raise ValueError("Retrieved PDB has no ATOM records; possibly an error or unsuitable sequence.")
        with open("Structure_Agent/result.pdb", "w") as f:
            f.write(text)
        return "Structure_Agent/result.pdb"
    except Exception as e:
        # 回退到本地模型（若存在）
        if os.path.exists(fallback_pdb):
            print(f"Warning: Using local fallback model due to API error: {e}")
            return fallback_pdb
        # 若无本地回退，抛出更友好的错误
        raise RuntimeError(
            f"Failed to obtain PDB from ESM Atlas and no fallback found. Original error: {e}"
        )

def extract_structure_features(pdb_file):
    # 1. 基本信息
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("protein", pdb_file)
    # 安全获取第一个模型
    models = list(structure.get_models())
    if len(models) == 0:
        raise ValueError("PDB中未找到任何模型（MODEL/ATOM 记录缺失或解析失败）。")
    model = models[0]
    chains = list(model.get_chains())
    num_chains = len(chains)
    chain_ids = [chain.id for chain in chains]
    residues = [res for res in model.get_residues() if res.get_id()[0] == ' ']
    num_residues = len(residues)

    # 2. pLDDT均值
    struct = bsio.load_structure(pdb_file, extra_fields=["b_factor"])
    try:
        plddt_mean = float(struct.b_factor.mean())
    except Exception:
        plddt_mean = None

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
        # 以3.0Å为阈值判断S-S键（欧氏距离）
        for i in range(len(cys_atoms)):
            for j in range(i+1, len(cys_atoms)):
                diff = (cys_atoms[i].coord - cys_atoms[j].coord)
                dist = ((diff ** 2).sum()) ** 0.5
                if dist <= 3.0:
                    disulfide_bonds += 1

    # 5. 疏水/亲水残基比例
    hydrophobic = {"ALA","VAL","ILE","LEU","MET","PHE","TRP","PRO"}
    hydrophilic = {"ARG","ASN","ASP","GLN","GLU","HIS","LYS","SER","THR","TYR","CYS"}
    hydrophobic_count = sum(1 for res in residues if res.get_resname() in hydrophobic)
    hydrophilic_count = sum(1 for res in residues if res.get_resname() in hydrophilic)
    hydrophobic_ratio = (hydrophobic_count / num_residues * 100) if num_residues > 0 else None
    hydrophilic_ratio = (hydrophilic_count / num_residues * 100) if num_residues > 0 else None

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

def find_binding_pockets(pdb_file):
    """使用简单几何方法识别结合口袋"""
    try:
        from Bio.PDB import PDBParser
        import numpy as np
        
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure("protein", pdb_file)
        
        pockets = []
        for model in structure:
            # 获取所有原子坐标
            atoms = []
            for chain in model:
                for residue in chain:
                    for atom in residue:
                        atoms.append(atom.get_coord())
            
            if len(atoms) < 10:
                return pockets
                
            atoms = np.array(atoms)
            
            # 简单的口袋识别：寻找表面凹陷
            # 计算每个原子的可及性
            accessible_atoms = []
            for i, atom in enumerate(atoms):
                distances = np.linalg.norm(atoms - atom, axis=1)
                neighbors = np.sum(distances < 10.0)  # 10Å内的邻居
                if neighbors < 15:  # 表面原子邻居较少
                    accessible_atoms.append(i)
            
            # 寻找凹陷区域
            if len(accessible_atoms) > 5:
                surface_coords = atoms[accessible_atoms]
                # 简单的聚类识别凹陷
                pocket_centers = find_pocket_centers(surface_coords)
                for center in pocket_centers:
                    pockets.append({
                        'center': center,
                        'size': estimate_pocket_size(center, atoms)
                    })
        
        return pockets
    except Exception as e:
        print(f"Warning: Binding pocket analysis failed: {e}")
        return []

def find_pocket_centers(surface_coords, min_distance=8.0):
    """寻找口袋中心"""
    import numpy as np
    from sklearn.cluster import DBSCAN
    
    if len(surface_coords) < 3:
        return []
    
    # 使用DBSCAN聚类找到凹陷区域
    clustering = DBSCAN(eps=min_distance, min_samples=3).fit(surface_coords)
    
    centers = []
    for cluster_id in set(clustering.labels_):
        if cluster_id != -1:  # 忽略噪声点
            cluster_points = surface_coords[clustering.labels_ == cluster_id]
            center = np.mean(cluster_points, axis=0)
            centers.append(center)
    
    return centers

def estimate_pocket_size(center, all_atoms, radius=8.0):
    """估算口袋大小"""
    import numpy as np
    distances = np.linalg.norm(all_atoms - center, axis=1)
    nearby_atoms = np.sum(distances < radius)
    return nearby_atoms

def analyze_flexibility(pdb_file):
    """基于B-factor分析结构柔性"""
    try:
        import biotite.structure.io as bsio
        import numpy as np
        
        struct = bsio.load_structure(pdb_file, extra_fields=["b_factor"])
        b_factors = struct.b_factor
        
        if len(b_factors) == 0:
            return {}
        
        # 计算柔性指标
        mean_bfactor = float(np.mean(b_factors))
        std_bfactor = float(np.std(b_factors))
        
        # 识别高/低柔性区域
        high_flex_threshold = mean_bfactor + 2 * std_bfactor
        low_flex_threshold = mean_bfactor - 2 * std_bfactor
        
        high_flexibility_count = np.sum(b_factors > high_flex_threshold)
        low_flexibility_count = np.sum(b_factors < low_flex_threshold)
        
        flexibility_metrics = {
            'mean_bfactor': mean_bfactor,
            'std_bfactor': std_bfactor,
            'high_flexibility_regions': int(high_flexibility_count),
            'low_flexibility_regions': int(low_flexibility_count),
            'flexibility_score': min(1.0, max(0.0, (mean_bfactor - 20) / 80))  # 归一化到0-1
        }
        
        return flexibility_metrics
    except Exception as e:
        print(f"Warning: Flexibility analysis failed: {e}")
        return {}

def find_catalytic_sites(pdb_file):
    """识别潜在的催化残基"""
    try:
        from Bio.PDB import PDBParser
        import numpy as np
        
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure("protein", pdb_file)
        
        catalytic_residues = []
        catalytic_types = ['HIS', 'ASP', 'GLU', 'SER', 'THR', 'CYS', 'LYS', 'ARG']
        
        for model in structure:
            for chain in model:
                chain_residues = list(chain.get_residues())
                
                for residue in chain_residues:
                    if residue.get_resname() in catalytic_types:
                        # 检查是否在活性位点区域
                        if is_in_active_site_region(residue, chain_residues):
                            catalytic_residues.append({
                                'residue': residue.get_resname(),
                                'position': residue.get_id()[1],
                                'chain': chain.id,
                                'confidence': calculate_catalytic_confidence(residue, chain_residues)
                            })
        
        return catalytic_residues
    except Exception as e:
        print(f"Warning: Catalytic site analysis failed: {e}")
        return []

def is_in_active_site_region(residue, chain_residues):
    """判断残基是否在活性位点区域"""
    try:
        import numpy as np
        
        # 获取残基坐标
        if 'CA' not in residue:
            return False
        
        ca_coord = residue['CA'].get_coord()
        
        # 检查周围是否有其他催化残基
        catalytic_neighbors = 0
        for other_residue in chain_residues:
            if other_residue.get_resname() in ['HIS', 'ASP', 'GLU', 'SER', 'THR', 'CYS', 'LYS', 'ARG']:
                if 'CA' in other_residue:
                    other_coord = other_residue['CA'].get_coord()
                    distance = np.linalg.norm(ca_coord - other_coord)
                    if distance < 15.0:  # 15Å内的催化残基
                        catalytic_neighbors += 1
        
        return catalytic_neighbors >= 2  # 至少2个催化残基邻居
    except Exception:
        return False

def calculate_catalytic_confidence(residue, chain_residues):
    """计算催化残基的置信度"""
    try:
        import numpy as np
        
        confidence = 0.5  # 基础置信度
        
        # 基于残基类型调整
        resname = residue.get_resname()
        if resname in ['HIS', 'ASP', 'GLU']:  # 常见催化残基
            confidence += 0.2
        elif resname in ['SER', 'CYS']:  # 亲核残基
            confidence += 0.1
        
        # 基于周围环境调整
        if 'CA' in residue:
            ca_coord = residue['CA'].get_coord()
            nearby_hydrophobic = 0
            for other_residue in chain_residues:
                if other_residue.get_resname() in ['ALA', 'VAL', 'ILE', 'LEU', 'MET', 'PHE', 'TRP']:
                    if 'CA' in other_residue:
                        distance = np.linalg.norm(ca_coord - other_residue['CA'].get_coord())
                        if distance < 8.0:
                            nearby_hydrophobic += 1
            
            if nearby_hydrophobic >= 3:  # 周围有疏水环境
                confidence += 0.1
        
        return min(1.0, confidence)
    except Exception:
        return 0.5

def calc_surface_area_and_volume(pdb_file):
    struct = bsio.load_structure(pdb_file)
    # 计算表面积
    area = struc.sasa(struct)
    total_area = area.sum()
    # 体积估算（粗略，精确需用MSMS等工具）
    atom_volumes = {"C": 20.6, "N": 15.6, "O": 14.7, "S": 33.5, "H": 5.2}
    total_volume = sum(atom_volumes.get(atom.element, 18.0) for atom in struct)
    return total_area, total_volume

def calculate_structure_confidence(pdb_file, features, metals, area, volume) -> float:
    """
    计算结构分析的置信度
    
    Args:
        pdb_file: PDB文件路径
        features: 结构特征字典
        metals: 金属结合位点列表
        area: 表面积
        volume: 体积
    
    Returns:
        置信度分数 (0-1)
    """
    try:
        # 1. 基于pLDDT的置信度 (pLDDT越高置信度越高)
        plddt_val = features.get('plddt_mean', 0)
        plddt = 0 if plddt_val is None else plddt_val
        if plddt >= 90:
            plddt_confidence = 1.0
        elif plddt >= 70:
            plddt_confidence = 0.8
        elif plddt >= 50:
            plddt_confidence = 0.6
        else:
            plddt_confidence = 0.3
        
        # 2. 基于结构完整性的置信度
        num_residues = features.get('num_residues', 0)
        if num_residues >= 100:
            completeness_confidence = 1.0
        elif num_residues >= 50:
            completeness_confidence = 0.8
        else:
            completeness_confidence = 0.6
        
        # 3. 基于二级结构信息的置信度
        if features.get('helix_percent') is not None:
            structure_info_confidence = 1.0
        else:
            structure_info_confidence = 0.5
        
        # 4. 基于金属结合位点的置信度 (有金属结合位点可能表明功能更明确)
        if metals:
            metal_confidence = 0.9
        else:
            metal_confidence = 0.7
        
        # 5. 基于分子大小的置信度 (中等大小蛋白质置信度较高)
        if 50 <= num_residues <= 500:
            size_confidence = 0.9
        elif num_residues < 50:
            size_confidence = 0.6
        else:
            size_confidence = 0.7
        
        # 综合置信度
        confidence = (plddt_confidence * 0.4 + 
                     completeness_confidence * 0.2 + 
                     structure_info_confidence * 0.2 + 
                     metal_confidence * 0.1 + 
                     size_confidence * 0.1)
        
        return min(1.0, max(0.0, confidence))
        
    except Exception as e:
        print(f"Warning: Error calculating structure confidence: {e}")
        return 0.5  # 默认中等置信度

def structure_features_to_text(features, metals, area, volume, pockets=None, flexibility=None, catalytic_sites=None):
    text = f"This protein contains {features['num_chains']} chain(s) (Chain ID: {', '.join(features['chain_ids'])}), with a total of {features['num_residues']} amino acid residues."
    if features.get('plddt_mean') is not None:
        text += f" The average pLDDT confidence of structure prediction is {features['plddt_mean']:.1f}."
    if features['helix_percent'] is not None:
        text += f" Secondary structure composition: α-helix accounts for {features['helix_percent']:.1f}%, β-sheet accounts for {features['sheet_percent']:.1f}%, and random coil accounts for {features['coil_percent']:.1f}%."
    if features.get('hydrophobic_ratio') is not None and features.get('hydrophilic_ratio') is not None:
        text += f" Hydrophobic residues account for {features['hydrophobic_ratio']:.1f}%, hydrophilic residues account for {features['hydrophilic_ratio']:.1f}%."
    text += f" Number of disulfide bonds detected: {features['disulfide_bonds']}."
    if metals:
        text += f" Metal binding sites detected: {', '.join([f'{m[0]}(Chain {m[1]} Residue {m[2]})' for m in metals])}."
    text += f" Molecular surface area is approximately {area:.1f} Å², volume is approximately {volume:.1f} Å³."
    
    # 添加新的结构特征信息
    if pockets and len(pockets) > 0:
        text += f" Binding pockets detected: {len(pockets)} potential binding sites identified."
        for i, pocket in enumerate(pockets[:3]):  # 只显示前3个
            text += f" Pocket {i+1} has an estimated size of {pocket['size']} atoms."
    
    if flexibility and flexibility.get('flexibility_score') is not None:
        flex_score = flexibility['flexibility_score']
        if flex_score > 0.7:
            text += f" The protein shows high structural flexibility (score: {flex_score:.2f}), with {flexibility.get('high_flexibility_regions', 0)} highly flexible regions."
        elif flex_score < 0.3:
            text += f" The protein shows low structural flexibility (score: {flex_score:.2f}), indicating a rigid structure with {flexibility.get('low_flexibility_regions', 0)} highly stable regions."
        else:
            text += f" The protein shows moderate structural flexibility (score: {flex_score:.2f})."
    
    if catalytic_sites and len(catalytic_sites) > 0:
        text += f" Potential catalytic sites identified: {len(catalytic_sites)} residues with catalytic potential."
        for site in catalytic_sites[:3]:  # 只显示前3个
            text += f" {site['residue']} at position {site['position']} (Chain {site['chain']}, confidence: {site['confidence']:.2f})."
    
    return text

from dotenv import load_dotenv
from google import genai

load_dotenv()
google_client = genai.Client()

def generate(query_seq, docs) -> str:
    prompt = f"""
    You are a protein structure expert. Please provide a comprehensive functional prediction based on the following protein structure information:

    Protein sequence:
    {query_seq}

    Protein structure information:
    {docs}

   Please generate a comprehensive, accurate, and fluent natural language functional description from three aspects:
    1. Molecular Function (MF) - Biochemical activity of the protein
    2. Biological Process (BP) - Biological processes the protein participates in
    3. Cellular Component (CC) - Cellular localization of the protein

    Please provide detailed and accurate functional descriptions, including:
    - Main functional characteristics
    - Possible biological roles
    - Related metabolic pathways
    - Potential disease associations
    - Domain and functional site analysis
    
    """

    try:
        response = google_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text
    except Exception:
        # 网络/SSL异常时降级为直接返回结构文本，避免中断
        return "[Structure LLM generation temporarily unavailable, returning structure summary]\n" + docs

def structure_agent(state: dict) -> dict:
    seq = state["input"]
    pdb_file = get_pdb(seq)
    features = extract_structure_features(pdb_file)
    metals = find_metal_binding_sites(pdb_file)
    area, volume = calc_surface_area_and_volume(pdb_file)
    
    # 新增的结构分析功能
    pockets = find_binding_pockets(pdb_file)
    flexibility = analyze_flexibility(pdb_file)
    catalytic_sites = find_catalytic_sites(pdb_file)
    
    base_text = structure_features_to_text(features, metals, area, volume, pockets, flexibility, catalytic_sites)
    
    # 如果存在截断标记，提示并降权
    truncated_flag_path = "Structure_Agent/.truncated"
    if os.path.exists(truncated_flag_path):
        try:
            with open(truncated_flag_path, "r") as f:
                orig_len = f.read().strip()
        except Exception:
            orig_len = "unknown"
        base_text = (
            f"Note: Input sequence exceeds ESM Atlas limit, structure prediction performed only on first 400 aa (original length: {orig_len}).\n" + base_text
        )
    
    structure_nl = generate(seq, base_text)
    structure_confidence = calculate_structure_confidence(pdb_file, features, metals, area, volume)
    
    # 根据新特征调整置信度
    if pockets and len(pockets) > 0:
        structure_confidence = min(1.0, structure_confidence + 0.1)  # 有结合口袋增加置信度
    
    if catalytic_sites and len(catalytic_sites) > 0:
        structure_confidence = min(1.0, structure_confidence + 0.05)  # 有催化位点增加置信度
    
    if os.path.exists(truncated_flag_path):
        structure_confidence = max(0.0, min(1.0, structure_confidence * 0.7))
        try:
            os.remove(truncated_flag_path)
        except Exception:
            pass
    
    return {
        "structure_nl": structure_nl,
        "structure_confidence": structure_confidence
    }
