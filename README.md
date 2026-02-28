# 🚀 Metadata-Powered Lineage Intelligence Engine​

## 👥 Team Details

- **Team Name:** Elite Techies  
- **Members:**  
  - Vamsi Dasari (Lead Developer) 
  - Annamalai V (Senior Developer)
  - Gayatri M (Senior Developer)
  - Manjusree T (Developer)
  - Shyam B (Developer)
- **Domain Category:** Metadata-Powered Lineage    
- **Demo Video:** https://pravaltech.sharepoint.com/:v:/s/PravalInfotech/IQDUD-18LRsxQK8iX5Co70O2AfFXHU8K3YA_P8omZ4sbjWE?e=YfWvD1  

---

## 🎯 Problem Statement

The lack of structured lineage management in continuous development leads to hidden dependencies and unreliable impact analysis. Consequently, developers are forced to invest considerable time in manual impact assessments before every deployment, increasing delivery timelines and risk.

---

## 💡 Solution Overview

We built a **Metadata-Powered Lineage Intelligence Engine** that has:

1. **Procedure & View Lineage Explorer**: It gives data lineage view of any stored procedure or view directly from the live Data Warehouse objects .
2. **Attribute-Level Lineage Tracker**: It gives the usage of a particular table & field in the Data Warehouse.
3. **PBI Semantic Columnar Lineage**: It gives the usage of a particular table & field in the PBI Semantic Model.

It helps in faster impact analysis.

---

## 🏗 Architecture

📁 Architecture Diagram: `/architecture/architecture.png`

### Components

- User Interface (Streamlit)  
- ODBC Driver  
- Python 3.14
- Azure Synapse  
- XMLA Endpoint 

### Flow

1. Open the home page
2. Select the module using navigator tab
3. Procedure & Views Engine:
    - Login to Synapse
    - Enter the procedure or view name
    - Enter the column name
  	- Click Generate
    - Table Display + CSV Export
4. Attributes Lineage Engine:
    - Enter the table name
    - Enter the column name
    - Login to Synapse
    - Click Generate
    - Table Display + Graphical Display + CSV Export
5. Semantic Model Engine:
	- Select the column name
	- Click Generate
	- Table Display + Graphical Display + CSV Export 

#### 🟣 MODULE 1 — Procedure & View Lineage Explorer
- Connected to:
Azure Synapse Analytics
- 🔗 Connection:
  - ODBC Driver 18
  - ActiveDirectoryInteractive
- ⚙ Supported Parsing: Below object types are supported
    - VIEW	✅
    - PROCEDURE	✅

- 📊 Architecture Flow:
```
Fetch View/Procedure Definitions
        ↓
Clean SQL
        ↓
Parse using sqlglot (T-SQL Dialect)
        ↓
Walk AST Nodes
        ↓
Extract:
   - Target Table
   - Target Column
   - Source Columns
        ↓
Display + CSV Export
```



#### 🟢 MODULE 2 — Attribute-Level Lineage Tracker
- 🎯 Purpose
    - Trace column usage from:
      - ODS Tables
      - Views
      - Stored Procedures
- 🔗 Connects To:
  - SQL Server Metadata
- Uses:
  - sys.sql_modules
  - sys.objects
  - sys.schemas
- ⚙ Processing Logic
  1. Fetch all SQL objects referencing table
  2. Parse SQL using:
      - sqlglot
  3. Extract:
      - SELECT projections
      - Column aliases
  4. Detect:
      - INSERT target tables
  5. Build structured lineage dataframe

- 📊 Architecture Flow:
```
User Input: SCHEMA.TABLE + COLUMN
        ↓
Query sys.sql_modules
        ↓
Parse SQL (AST using sqlglot)
        ↓
Detect Column Usage
        ↓
Map to Target Table (if procedure)
        ↓
Render Graph + Table
```

#### 🔵 MODULE 3 — PBI Semantic Columnar Lineage
- 🔗 Connects To:
    - XMLA Endpoint via:
      - Microsoft.AnalysisServices.AdomdClient.dll
      - Pyadomd
- 📌 Queries:
  - $SYSTEM.TMSCHEMA_TABLES
  - $SYSTEM.TMSCHEMA_COLUMNS
  - $SYSTEM.TMSCHEMA_MEASURES
  - $SYSTEM.TMSCHEMA_PARTITIONS
  - $SYSTEM.TMSCHEMA_RELATIONSHIPS
- ⚙ Processing:
  - Extract DAX dependencies
  - Parse RELATED
  - Parse M Query Source
  - Build Directed Graph (NetworkX)
  - Generate:
    - Tabular Flow View
    - Interactive Graphviz Tree

- Power BI Semantic Layer
  - Connected to:
    - Power BI
    - XMLA Endpoint (Premium / PPU workspace)

- 📊 Architecture Flow:
```
Power BI Dataset
      ↓
XMLA Metadata Extraction
      ↓
DAX Expression Parsing
      ↓
M Query Source Extraction
      ↓
Lineage Rows (Source → Target)
      ↓
NetworkX Graph
      ↓
Streamlit Visualization
```

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python |
| Frontend | Streamlit |
| Analytics | Power BI |
| Database | Synapse |

---

## 📂 Project Structure

```
Metadata-Powered Lineage Intelligence Engine/
│
├── home.py
├── vw_proc_app.py
├── lineage_service.py
├── lineage_builder.py
├── db_connection.py
├── config.py
├── attribute_app.py
├── app_semantic.py
├── Pages/
│     ├── 1_Procedures_&_Views_Engine.py
│     ├── 2_Attributes_Lineage_Engine.py
│     ├── 3_Semantic_Model_Lineage.py
│
├── requirements.txt
├── README.md

```
---


## ⚙️ Setup Instructions

## 1️ Verify Required Software

- Programming Language: Python
- Required Version: 3.14
- Package Manager: pip

### 1️⃣ Clone Repository

```bash
git clone https://github.com/bsk1999/Metadata-Powered-Lineage-Intelligence-Engine
cd Metadata-Powered-Lineage-Intelligence-Engine
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate:

**Windows**
```bash
venv\Scripts\activate
```

**Mac/Linux**
```bash
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create `.env` file from `config.py`

Example:

```
DB_HOST=localhost
DB_USER=postgres

```

---

## ▶️ Entry Point

Run the application:

```bash
streamlit run src/home.py
```

Application will start at:

```
http://localhost:8501
```

---

## 🔄 Application Flow

1. Open the home page
2. Select the module using navigator tab
3. Procedure & Views Engine:
    - Login to Synapse
    - Enter the procedure or view name
    - Enter the column name
  	- Click Generate
    - Table Display + CSV Export
4. Attributes Lineage Engine:
    - Enter the table name
    - Enter the column name
    - Login to Synapse
    - Click Generate
    - Table Display + Graphical Display + CSV Export
5. Semantic Model Engine:
	- Select the column name
	- Click Generate
	- Table Display + Graphical Display + CSV Export

 

---

## 🧪 How to Test

### Section 1 – Procedures & Views Engine

Login to Synapse Server and follow the below steps:

```
1. Provide the procedure name or view name('TFM.VW_BLDG_METRICS')
2. Provide the column name('LOAD_FACTOR')
3. Click Generate
```
---

### Section 2 – Attributes Lineage Engine

Login to Synapse Server and follow the below steps:

```
1. Provide the table name('ODS.FNT_CVIREP_DISCO_M')
2. Provide the column name('A_CFA_PANEL')
3. Click Generate
```

---

### Section 3 – Semantic Model Engine

Login to Synapse Server and follow the below steps:

```
1. Select the column name from the drop down('ANNUALIZED GAAP RENT')
2. Click Generate
```

---

## ⚠️ Known Limitations

- It is limited to Azure cloud  
- Application performance is average

---

## 🔮 Future Improvements

- Scale the same solution to other cloud platforms   
- Improve application performance  
- Add AI bot to assist the users

---
