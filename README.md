<<<<<<< HEAD
# AMD_Slingshot_Demo
=======

<p align="center">
 	<img src="https://www.amd.com/system/files/styles/992x200/public/2023-12/slingshot-hackathon-banner.png" alt="AMD Slingshot Hackathon"/>
</p>

# A2S – AI Interior Design Product Recommendation Agent

**Project for AMD Slingshot Hackathon 2026**

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Hackathon Relevance & Vision](#hackathon-relevance--vision)
3. [Architecture](#architecture)
4. [Features](#features)
5. [Innovation Highlights](#innovation-highlights)
6. [Judging Criteria Mapping](#judging-criteria-mapping)
7. [Project Structure](#project-structure)
8. [Setup & Installation](#setup--installation)
9. [Usage Guide](#usage-guide)
10. [Team & Credits](#team--credits)
11. [Appendix: Diagrams](#appendix-diagrams)

---

## Project Overview

A2S (AI-to-Suggest) is an intelligent conversational agent that helps users discover the perfect furniture, lighting, and decor for their spaces. It leverages advanced AI (Google Gemini), a robust backend (Spring Boot), and a modern React frontend to deliver:
- Personalized product recommendations
- Context-aware design advice
- Seamless, natural language chat experience
- Real-time filtering and ranking from a curated catalog

**Demo:** [Add your demo link or screenshots here]

---

## Hackathon Relevance & Vision

**Why AMD Slingshot?**
- Harnesses AMD’s vision for AI-driven, user-centric solutions
- Showcases scalable, cross-platform architecture (Java, Python, JS)
- Demonstrates real-world impact in e-commerce and smart living

**Vision:**
> To empower users to design beautiful, functional spaces with AI-powered recommendations, making interior design accessible and delightful for everyone.

---

## Architecture

```

┌─────────────────────────────────────────────┐

│           FRONTEND (React + Vite)           │

│  Chat UI  │  Product Cards  │  Sidebar     │

└──────────────────┬──────────────────────────┘

&nbsp;									 │

┌──────────────────▼──────────────────────────┐

│            AI AGENT CORE (Python)           │

│  Context Manager → Gemini LLM → Filter      │

│  (Accumulates)    (Extracts)   (Queries)    │

└──────────────────┬──────────────────────────┘

&nbsp;									 │

┌──────────────────▼──────────────────────────┐

│            DATA LAYER (Pandas, Excel)       │

│  Loader → Filter Engine → Ranker → Results  │

└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐

│           BACKEND (Spring Boot)             │

│  REST APIs, Auth, Orchestration             │

└─────────────────────────────────────────────┘

```

**See full diagrams in [`LLM/docs/architecture/`](LLM/docs/architecture/).**

---

## Features

### Core Features
- **Conversational AI**: Natural language queries for room, style, budget, color, and more
- **Context Awareness**: Remembers and accumulates user preferences across turns
- **Smart Product Cards**: Images, prices, dimensions, tags, and direct buy links
- **Filter Relaxation**: Automatically relaxes filters if no exact matches
- **Design Tips**: Paint color and decor suggestions
- **Product Comparison**: Compare multiple products or categories

### UI Features
- **Modern Chat Interface**: Responsive, user-friendly, and accessible
- **Sidebar Dashboard**: Catalog stats, active filters, context summary
- **Suggested Queries**: One-click starter queries
- **Reset & Refresh**: Easy session management
- **Gallery & 3D Views**: Visualize products in context

---

## Innovation Highlights
- **Multi-Modal AI**: Integrates LLM (Gemini) with structured data filtering and ranking
- **Cross-Stack Integration**: Java (backend), Python (AI), JS (frontend)
- **Real-Time Personalization**: Dynamic, context-driven recommendations
- **Scalable & Modular**: Easily extendable for new product types, data sources, or AI models
- **Hackathon-Ready**: Rapid prototyping, clear separation of concerns, and robust error handling

---

## Judging Criteria Mapping

| Criteria                | How We Address It                                                                 |
|-------------------------|----------------------------------------------------------------------------------|
| Innovation              | Multi-modal AI, context-aware chat, filter relaxation, 3D visualization           |
| Technical Complexity    | Multi-language stack, LLM integration, real-time ranking/filtering                |
| Impact & Usefulness     | Makes interior design accessible, fast, and fun for all users                     |
| Scalability             | Modular architecture, easy to add new data sources or AI models                   |
| User Experience         | Modern, intuitive UI; seamless chat; visual product cards                         |
| AMD Tech Utilization    | [Add details if using AMD hardware, ROCm, or other AMD-specific tech]             |

---

## Project Structure

```

root/

├── backend/      # Spring Boot backend (Java)

├── frontend/     # React + Vite frontend (JS)

├── LLM/          # Python AI agent, data, and docs

├── run.bat       # Startup script

├── README.md     # This file

└── ...           # Configs, datasets, etc.

```

---

## Setup & Installation

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- Java (17+)
- Maven

### 1. Clone the Repository
```sh

git clone https://github.com/Asha0509/AMD\_Slingshot\_Demo.git

cd AMD\_Slingshot\_Demo

```

### 2. Frontend Setup
```sh

cd frontend

npm install

npm run dev

```

### 3. Backend Setup
```sh

cd backend

mvn clean install

mvn spring-boot:run

```

### 4. LLM (AI Agent) Setup
```sh

cd LLM

pip install -r requirements.txt

python app.py

```

---

## Usage Guide
- Access the frontend at [http://localhost:5173](http://localhost:5173)
- Use the chat to describe your room, style, budget, etc.
- Explore product cards, gallery, and 3D views
- Refine your search with natural language or sidebar filters
- [Add screenshots, demo GIFs, or video links here]

---

## Team & Credits
- **Team Name:** [Your Team Name]
- **Members:** [List all contributors]
- **Mentors/Support:** [Add if any]
- **Special Thanks:** AMD, hackathon organizers, and open-source contributors

---

## Appendix: Diagrams
- See `LLM/docs/architecture/` for detailed system, flow, and data pipeline diagrams
- [Embed or link to key diagrams here]

---

## License
[Specify your license here]

---

## Contact
- [Your email/contact info]
- [Project website or LinkedIn]

>>>>>>> e3b9a6e (Add detailed README for AMD Slingshot Hackathon)