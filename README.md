# 🚦 GRIDLOCK SENTINEL – AI Traffic Intelligence Command Center

GRIDLOCK SENTINEL is an AI-powered Traffic Intelligence and Incident Management Platform designed to assist traffic control centers in analyzing incidents, predicting road closures, estimating clearance times, recommending operational resources, and supporting decision-making through AI-powered insights.

The platform transforms raw traffic incident reports into actionable operational intelligence using machine learning, retrieval-augmented intelligence, and digital twin concepts.

---

## 🎥 Video Demonstration

Watch the complete project demo:

🔗 https://go.screenpal.com/watch/cO1rl9nuKOM

---

# 📌 Problem Statement

Traffic incidents often cause:

* Severe congestion
* Delayed emergency response
* Inefficient resource allocation
* Lack of situational awareness
* Poor coordination among traffic authorities

Traffic operators frequently rely on manual decision-making and fragmented information sources.

GRIDLOCK SENTINEL addresses these challenges by providing a unified AI-powered command center capable of real-time incident intelligence and decision support.

---

# 🎯 Key Features

## 🚧 Road Closure Prediction

Predicts whether an incident is likely to require road closure using machine learning.

### Output

* Closure Probability
* Closure Recommendation
* Confidence Score

---

## ⚡ Priority Intelligence Engine

Determines operational priority based on:

* Corridor Risk
* Zone Criticality
* Historical Incident Patterns

### Output

* High Priority
* Low Priority

---

## ⏱️ Clearance Time Estimation

Uses a Digital Twin Retrieval Engine to estimate incident clearance duration from similar historical incidents.

### Output

* Estimated Clearance Time
* Confidence Range
* Historical Evidence

---

## 🔍 Similar Incident Retrieval

Retrieves historical incidents most similar to the current event.

### Output

* Similar Cases
* Historical Clearance Times
* Resource Usage Patterns
* Resolution Outcomes

---

## 🚓 Resource Recommendation Engine

Recommends operational resources based on:

* Closure Probability
* Priority Level
* Incident Cause
* Clearance Duration

### Output

* Traffic Officers
* Barricades
* Tow Vehicles
* Emergency Support Units

---

## 📈 Risk Scoring Engine

Generates a unified incident severity score.

### Output

* Risk Score (0–100)
* Risk Category
* Operational Impact Level

---

## 🤖 AI Copilot

Generates command-center briefings and operational summaries using LLM-powered reasoning.

### Output

* Incident Summary
* Risk Assessment
* Recommended Actions
* Operational Briefing

---

# 🧠 AI Modules

| Module                  | Purpose                           |
| ----------------------- | --------------------------------- |
| Closure Prediction      | Predict road closure requirements |
| Priority Intelligence   | Determine incident priority       |
| Digital Twin Retrieval  | Find similar historical incidents |
| Clearance Estimation    | Estimate resolution duration      |
| Resource Recommendation | Recommend operational resources   |
| Risk Scoring            | Assess incident severity          |
| AI Copilot              | Generate operational briefings    |

---

# 🏗️ System Architecture

```text
                       ┌──────────────────┐
                       │     Frontend     │
                       │  Next.js + React │
                       └────────┬─────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │   FastAPI Backend   │
                     └────────┬────────────┘
                              │
      ┌───────────────┬───────┼────────┬───────────────┐
      ▼               ▼       ▼        ▼               ▼

Closure AI      Priority   Retrieval  Copilot     MongoDB
Prediction      Engine      Engine      AI         Atlas

      │               │       │
      ▼               ▼       ▼

 Resource      Risk Score   Clearance
 Recommendation            Estimation
```

---

# 🔄 AI Processing Pipeline

```text
Incident Report
       │
       ▼
Closure Prediction
       │
       ▼
Priority Intelligence
       │
       ▼
Historical Retrieval
       │
       ▼
Clearance Estimation
       │
       ▼
Resource Recommendation
       │
       ▼
Risk Score Generation
       │
       ▼
AI Copilot Briefing
       │
       ▼
Command Center Dashboard
```

---

# 🧪 Machine Learning Models

## 1. Closure Prediction Model

### Algorithm

XGBoost Classifier

### Objective

Predict whether an incident requires road closure.

### Performance

| Metric   | Value |
| -------- | ----- |
| Accuracy | 87.1% |
| F1 Score | 0.428 |
| AUC-ROC  | 0.773 |

### Features

* Event Type
* Event Cause
* Corridor
* Zone
* Vehicle Type
* Temporal Features
* Historical Closure Statistics

---

## 2. Priority Intelligence Engine

### Objective

Determine incident priority using historical operational patterns.

### Inputs

* Corridor
* Zone
* Event Cause
* Historical Risk Patterns

### Output

* High Priority
* Low Priority

---

## 3. Digital Twin Clearance Engine

### Objective

Estimate incident clearance duration.

### Technology

* Sentence Transformers
* Semantic Retrieval
* FAISS Vector Search
* Historical Incident Similarity

### Performance

| Metric | Value         |
| ------ | ------------- |
| MAE    | 34.19 Minutes |

---

## 4. Similar Incident Retrieval

### Embedding Model

all-MiniLM-L6-v2

### Vector Dimension

384

### Retrieval Engine

FAISS + Semantic Similarity

---

# 🛠️ Technology Stack

## Frontend

* Next.js 15
* React 19
* TypeScript
* Tailwind CSS
* Zustand
* TanStack Query
* Recharts
* React Leaflet

## Backend

* FastAPI
* Pydantic v2
* MongoDB Atlas
* Redis
* Groq LLM

## Machine Learning

* XGBoost
* Scikit-Learn
* Pandas
* NumPy
* Sentence Transformers
* FAISS

## Mapping & Routing

* OpenStreetMap
* Leaflet
* OpenRouteService

---

# 📂 Repository Structure

```text
GRIDLOCK/
│
├── backend/
│   ├── app/
│   ├── assets/
│   ├── tests/
│   ├── tools/
│   ├── requirements.txt
│   └── Dockerfile
│
├── docs/
│   ├── architecture/
│   ├── api_docs/
│   └── diagrams/
│
├── frontend/
│
└── README.md
```

---

# 🚀 Backend Workflow

The primary endpoint:

```http
POST /api/v1/analyze
```

Executes:

1. Closure Prediction
2. Priority Analysis
3. Similar Incident Retrieval
4. Clearance Estimation
5. Resource Recommendation
6. Risk Scoring
7. AI Copilot Summary
8. MongoDB Persistence

---

# 📊 Dashboard Capabilities

* Real-Time Incident Monitoring
* Risk Heatmaps
* Corridor Intelligence
* Zone Risk Analysis
* Resource Tracking
* Similar Incident Visualization
* AI Decision Support

---

# 🔮 Future Enhancements

* Live Traffic API Integration
* CCTV Computer Vision
* Congestion Forecasting
* Emergency Vehicle Routing
* Mobile Operations App
* Multi-City Deployment

---

# 👨‍💻 Team GRIDLOCK

AI-Powered Traffic Intelligence & Smart Mobility Platform

Built for Smart City Traffic Operations, Incident Management, and Command Center Decision Support.

---

# 📄 License

This project is developed for educational, research, and hackathon demonstration purposes.
