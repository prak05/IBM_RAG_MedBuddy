nano README.md# 🩺 MedBuddy | IBM Watsonx RAG Assistant
> **KTU S6 CSD 334 Mini Project** > **Strategic AI Implementation for Medical Knowledge Retrieval**

<div align="center">
  <a href="https://github.com/prak05/IBM_RAG_MedBuddy">
    <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=700&size=40&duration=3000&pause=1000&color=0F62FE&background=FFFFFF00&center=true&vCenter=true&width=600&lines=MEDBUDDY+RAG+ASSISTANT;POWERED+BY+IBM+WATSONX;KTU+S6+MINI+PROJECT" alt="Typing SVG" />
  </a>
</div>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![IBM Watsonx](https://img.shields.io/badge/AI-IBM_Watsonx-be95ff?style=for-the-badge&logo=ibm&logoColor=white)](https://www.ibm.com/watsonx)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Kali Linux](https://img.shields.io/badge/OS-Kali_Linux-557C94?style=for-the-badge&logo=kali-linux&logoColor=white)](https://www.kali.org/)

<br/>

![GitHub last commit](https://img.shields.io/github/last-commit/prak05/IBM_RAG_MedBuddy?style=flat-square&color=FF6B6B)
![GitHub repo size](https://img.shields.io/github/repo-size/prak05/IBM_RAG_MedBuddy?style=flat-square&color=4ECDC4)
![Visitors](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fprak05%2FIBM_RAG_MedBuddy&count_bg=%23C84BFF&title_bg=%23555555&title=LIVE+VIEWS&edge_flat=false)

</div>

<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif" width="100%">

## ⚡ 📖 Overview & Core Tech

**MedBuddy** is an intelligent assistant designed to eliminate hallucinations in medical Q&A. By grounding **IBM Granite LLMs** with specific medical documentation (`data/cd.pdf`) via a **RAG (Retrieval-Augmented Generation)** pipeline, it delivers accurate, context-aware insights.

### 🚀 The Edge
* **Zero Hallucination Aim:** Answers are strictly bound to the provided medical text.
* **Enterprise Grade:** Leveraging IBM Watsonx's robust infrastructure.
* **Sleek UI:** A reactive Streamlit interface running on Kali Linux.

<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif" width="100%">

## 🧠 🏗️ Architecture Flow

The system follows a high-performance ingestion and retrieval path.

```mermaid
graph LR
    A[📄 data/cd.pdf] -- Ingestion --> B(⚙️ Text Splitter)
    B -- Chunks --> C{🧠 IBM Watsonx Embeddings}
    C -- Vectors --> D[(🗄️ ChromaDB Vector Store)]
    E[👤 User Query] --> F{🔎 Semantic Search}
    D -- Context Match --> F
    F -- Augmented Prompt --> G[🤖 IBM Granite LLM]
    G --> H[💬 Streamlit UI Response]
<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif" width="100%">

📊 📂 Project Vitals
Directory Structure
Plaintext
IBM_RAG_MedBuddy/
├── 📦 data/
│   └── cd.pdf                # 🏥 The Knowledge Source
├── ⚡ src/
│   ├── app.py                # 🖥️ Frontend User Interface
│   └── rag_engine.py         # 🧠 The AI Brain (Watsonx Integration)
├── 📜 requirements.txt       # 🐍 Dependency Manifest
└── ⚙️ .gitignore              # 🐧 Linux Optimization
Live Dev Analytics
<div align="center"> <img src="https://www.google.com/search?q=https://github-readme-stats.vercel.app/api/pin/%3Fusername%3Dprak05%26repo%3DIBM_RAG_MedBuddy%26theme%3Dradical%26border_radius%3D10" alt="Repo Stats" /> </div>

<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif" width="100%">

🚀 🛠️ Installation & Launch
1. Clone & Prep
Bash
git clone [https://github.com/prak05/IBM_RAG_MedBuddy.git](https://github.com/prak05/IBM_RAG_MedBuddy.git)
cd IBM_RAG_MedBuddy
pip install -r requirements.txt
2. Credentials
Ensure your environment holds your IBM secrets:

Bash
export WATSONX_APIKEY="your_key"
export PROJECT_ID="your_id"
3. Ignite
Bash
streamlit run src/app.py
<img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif" width="100%">

<div align="center">


<h3>👨‍💻 Developed for KTU S6 CSD 334</h3> <img src="https://www.google.com/search?q=https://github-readme-stats.vercel.app/api%3Fusername%3Dprak05%26show_icons%3Dtrue%26theme%3Dradical%26hide_border%3Dtrue%26count_private%3Dtrue" width="400" />



<b>Developer:</b> Prakhar Sharma | <b>Institution:</b> RIET | <b>Colleague:</b> Adithya Baiju



<img src="https://www.google.com/search?q=https://img.shields.io/badge/Built%2520With-IBM%2520Watsonx-0f62fe%3Fstyle%3Dfor-the-badge%26logo%3Dibm"> </div># IBM_RAG_MedBuddy
