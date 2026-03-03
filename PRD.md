1. Project Overview & Vision
The Ops Command Center (Neon) is a decoupled, fault-tolerant Streamlit application designed for Telecommunications Network Operations.
The primary vision is to transition the operations team from Reactive Observation (just counting fault alarms) to Financial Protection & Gamification (prioritizing sites based on business value, dependency blast radius, and ZAR saved).

2. Target Audience & Personas
NOC Shift Teams (Tactical): Require rapid root cause analysis, MTTR tracking, and Hubsite dependency grouping to execute fast repairs.

Senior Management (Strategic): Require high-level network availability insights, financial risk exposure (ZAR), and regional/shift performance leaderboards.

3. System Architecture (Decoupled "Micro-Monolith")
To ensure fault tolerance and scalability, the application must avoid a single monolithic script. It requires a modular architecture:

Separation of Concerns: Data ingestion/ETL logic must be separate from UI rendering logic.

Blast Radius Containment: Individual pages (Operations, Strategy, Intelligence) must be wrapped in error-handling blocks so a failure in one module does not crash the core application.

Scalability: Must dynamically support 9 regions (KZN, WES, CEN, EAS, SGS, SGC, MPU, NGA, LIM) using a dropdown selector, automatically pulling the corresponding Sonar_{Region} metadata.

4. The 3-Stage Data Pipeline
Intelligent Ingestion (The "Header Hunter"): The application must dynamically scan the first 15 rows of raw incident uploads to locate the data horizon (headers), preventing crashes from messy Excel formatting.

Dynamic Unification (The "Fuzzy Join"): A vectorized string normalization engine must clean joining keys (lowercasing, stripping special characters and prefixes like KZN_) to achieve a 100% match rate between Incident Data and Engineering Metadata.

Strategic Visualization: The final output must render calculated decision metrics (Risk, Variance) rather than raw alarm counts.

5. Core Features & Business Logic
A. Operational Metrics
MTTR Variance (Delta): Identifies "Problem Children" by calculating MTTR (Hours) - MTTR Target.

SLA Compliance: Tracking IN vs. OUT SLA failure rates.

B. Strategic Prioritization (Risk Engine)
Risk Score Calculation: Frequency * (1000 / Site Rank). Ensures high-value (low rank number) sites are pushed to the top of the engineering hit-list, regardless of standard chronological queuing.

C. Geospatial & Technical Intelligence
Heatmaps: Interactive maps plotting coordinates, sized by outage frequency and colored by Risk Score.

Administrative Drill-downs: MTTR performance comparisons across District Councils and Municipalities.

Tech Impact: Visualizing MTTR differences across GreenZones (security access impact) and Modernisation statuses (Legacy vs. Upgraded).

6. Future Roadmap (In-Planning)
Phase 2: Hubsite Logic & Dependencies
Goal: Group individual site failures under their parent Hubsite to understand the true network impact.

New Metric (Blast Radius): Calculate the cumulative value of an outage: Hub_Value = Hub_Rank + Sum(Child_Ranks). Visually represent the blast radius on the geospatial map.

Phase 3: Financial Gamification
Goal: Drive shift performance through competition and financial awareness.

New Metric (ZAR Value): Assign a financial loss proxy to Site Ranks (e.g., Rank 1 = High ZAR/hr).

Leaderboards: Implement "Region Wars" and "Shift Saver" dashboards to reward teams that restore high-value networks faster than target SLAs.

Phase 4: Full Automation
Goal: Replace manual Excel uploads by integrating Streamlit directly with a SharePoint Data Lake via Office365-REST-Python-Client.

7. UI/UX Requirements
Theme: "Neon Cyberpunk" Command Center. Dark background (#0e1117) with cyan (#00c8ff) and magenta accents.

Interactivity: Fast, cached (@st.cache_data) filtering without API/server overloads during user refreshes.

Exportability: All priority tables must feature a one-click BytesIO Excel download button for engineering dispatch.

## Version 1.1: The Streamlit Baseline Prototype
* **Objective:** Translate the legacy UiPath static `dashboard.html` into a live, decoupled Streamlit application.
* **Core Requirement:** Maintain absolute parity with the Phase 1 UiPath logic. The app must ingest `Phase1result.txt` and accurately display Total OOS, Region Pulse Cards (Yellow <50, Orange 50-100, Red >100), and the Diagnostic Table (Power, TX, RF, HW, Hub).
* **Architecture:** Enforce the "Micro-Monolith" structure using `Neon_Streamlit_App.py` (Controller), `data_engine.py` (ETL), and `ui_components.py` (View).