# A2S - Aesthetics To Spaces 
 
India design execution infrastructure for home interiors. 
 
## A2S Brief 
A2S helps users go from design intent to real products faster. 
Users select room type, budget, and aesthetic, then get curated products with source links. 
 
At launch, A2S focuses on three outcomes: 
- Structured room-wise catalog discovery 
- Cross-platform price visibility 
- AI-assisted shortlisting based on constraints 
 
## Setup 
 
### Prerequisites 
- Node.js 18+ 
- Java 17+ 
- Maven 3.9+ 
- Python 3.10+ 
 
### 1. Clone 
```bash 
git clone https://github.com/Asha0509/A2S_beta_v1.git 
cd A2S_beta_v1 
```
 
### 2. Frontend 
```bash 
cd frontend 
npm install 
npm run dev 
``` 
 
### 3. Backend 
```bash 
cd backend 
mvn clean install 
mvn spring-boot:run 
``` 
 
### 4. LLM Service 
```bash 
cd LLM 
pip install -r requirements.txt 
python app.py 
``` 
 
### Environment Files 
Create local env files as required: 
- .env 
- backend/.env 
- frontend/.env or frontend/.env.local 
Keep secrets out of version control.
 
## A2S in Detail 
 
### Problem A2S Solves 
- Discovery is fragmented across many furniture platforms. 
- Price comparison is manual and time-consuming. 
- Users struggle to map budget to complete room shortlists. 
 
### Product Strategy 
Phase 1 builds the intelligence foundation; Phase 2 adds execution infrastructure. 
 
#### Phase 1: Intelligence Foundation 
- Room-specific product catalog (28,000+ at launch) 
- Budget and aesthetic filters 
- Cross-platform price intelligence 
- AI design consultant for natural-language planning 
- Source-and-shop links for direct purchase intent 
 
#### Phase 2: Execution Intelligence 
- Video-to-3D spatial reconstruction 
- Verified vendor sourcing engine (50+ vendors) 
- Artisan cloud for custom work 
- AR live placement and turnkey execution workflows 
 
### Revenue Model 
- Early stage: affiliate commissions, premium AI features, data insights 
- Scale stage: sourcing fees, artisan commissions, execution management fees 
 
### Roadmap Highlights 
- March 2026: 28,000+ product launch 
- Q2 2026: price intelligence engine 
- Q3 2026: AI consultant v1 
- Q1 2027: 3D staging integration 
- Q3 2027 onward: sourcing and execution modules 
 
### Repository Architecture 
- frontend/: React + Vite product experience 
- backend/: Spring Boot APIs and orchestration 
- LLM/: AI agent, data modules, and scrapers 
- cleaned_dataset.xlsx: current curated catalog dataset 
 
### Notes 
- This README reflects startup positioning for A2S - Aesthetics To Spaces. 
- Strategic market and roadmap figures are based on your executive summary document.
