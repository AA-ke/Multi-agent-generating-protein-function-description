This is a LLM-based multi-agent system for generating protein function description in natural language. The system will automatically analyze and summarize information in various modals(sequence, structure and function), outputting an end-to-end protein function description for scientist to refer to.
<img width="1806" height="823" alt="image" src="https://github.com/user-attachments/assets/eb03539a-43d8-4eae-83f0-bde093122d3f" />
The system is composed of 4 main agents based on a default LLM(Gemini-2.5-flash):Sequence Agent, Structure Agent, Function Agent and Scientific Critic.
For Sequence Agent, it will use ESM embedding as distance for RAG, retrieve top-5 sequence-neighboring proteins，referring to their functions to generating function description from sequence information.
<img width="1709" height="625" alt="image" src="https://github.com/user-attachments/assets/59826fdb-1222-4c6f-8657-a54a701cae21" />
For Structure Agent,it will use ESMFold to get the structure of the query protein which stores in PDB file，then calling function of relative bioinformatics Python packages to analyze the PDB and get structure information for function predicting.
<img width="1749" height="621" alt="image" src="https://github.com/user-attachments/assets/7e77ffa6-2cb2-4333-869b-98751cdb5567" />
For Function Agent, it will use DEEPGOPlus, directly get GO predictions of the query, and then analyze and summarize the GO predicted.

Agents communicate in natural language. Each agent will give out a confidence of its answer. 

In the end, Scientific Critic will summarize all agents' answer, give a comprehensive protein function description in natural language.
