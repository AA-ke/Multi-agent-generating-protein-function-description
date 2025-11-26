import json
from dotenv import load_dotenv
from google import genai

load_dotenv()
google_client = genai.Client()

def convert_to_natural_language(data):
    """
    Convert JSON data to natural language description
    
    Args:
        data: Dictionary containing protein information
    
    Returns:
        Natural language description string
    """
    prompt = f"""
    You are a protein function description expert. Please convert the following protein information into a natural and fluent functional description:

    Protein ID: {data['id']}
    Protein sequence: {data['sequence']}
    Function description: {data['document']}
    
    Gene name: {data['metadata']['gene']}
    Species: {data['metadata']['species']}
    
    GO Terms:
    {chr(10).join([f"- {term}" for term in data['metadata']['go_terms']])}
    
    GO Descriptions:
    {chr(10).join([f"- {desc}" for desc in data['metadata']['go_descriptions']])}
    
    Pfam Domains:
    {chr(10).join([f"- {pfam}" for pfam in data['metadata']['pfam']])}
    
    Functional Keywords:
    {chr(10).join([f"- {keyword}" for keyword in data['metadata']['functional_keywords']])}

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
    
    response = google_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

def process_eval_data():
    """
    Process evaluation data and generate standard answer
    """
    # Read evaluation data
    with open("Agents/eval_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"Processing protein: {data['id']} ({data['metadata']['gene']})")
    print(f"Species: {data['metadata']['species']}")
    print(f"Sequence length: {len(data['sequence'])} amino acids")
    print("-" * 60)
    
    # Generate natural language description
    natural_description = convert_to_natural_language(data)
    
    print("Generated standard answer:")
    print("=" * 60)
    print(natural_description)
    print("=" * 60)
    
 
    with open("Agents/standard_answer_A0A087X1C5.txt", "w", encoding="utf-8") as f:
        json.dump(natural_description, f, ensure_ascii=False, indent=2)
    
    print(f"\nStandard answer saved to: Agents/standard_answer_A0A087X1C5.txt")

if __name__ == "__main__":
     process_eval_data()
