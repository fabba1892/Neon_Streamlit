import json
import pandas as pd
import streamlit as st
from datetime import datetime
import os

# ==========================================
# 🚀 CORE DATA INGESTION
# ==========================================

@st.cache_data(ttl=300) # Cache the data for 5 minutes to prevent redundant I/O operations
def load_and_process_data(file_path: str = "Phase1result.txt"):
    """
    Ingests the Phase 1 JSON output, extracts metadata, and flattens the 
    regional incident data into a highly optimized Pandas DataFrame.
    
    Returns:
        tuple: (incidents_df, metadata_dict, regional_kpi_dict)
    """
    
    # 1. FAULT TOLERANCE: Check if file exists before attempting to open
    if not os.path.exists(file_path):
        st.error(f"🚨 CRITICAL FAILURE: Data source '{file_path}' not found.")
        st.stop() # Halts the app completely - Blast Radius Containment

    # 2. INGESTION & PARSING
    try:
        with open(file_path, 'r') as file:
            raw_data = json.load(file)
            
        metadata = raw_data.get("metadata", {})
        regional_data = raw_data.get("regional_data", {})
        
    except json.JSONDecodeError:
        st.error("🚨 CRITICAL FAILURE: JSON schema is corrupted. Cannot parse data.")
        st.stop()

    # 3. DATA FLATTENING (The Transformation Engine)
    # We will store flattened incident records here
    flat_incidents = []
    
    # We will store the top-level KPIs (Total OOS per region) here for the Neon UI Cards
    regional_kpis = {}

    # Iterate through the dynamically scaling regions (NGA, EAS, WES, etc.)
    for region_name, region_info in regional_data.items():
        
        # Store the high-level KPI (e.g., NGA has 56 Total OOS)
        regional_kpis[region_name] = {
            "Total_OOS_Count": region_info.get("Total_OOS_Count", 0)
        }
        
        # Process individual incidents if they exist
        incidents = region_info.get("Incidents", [])
        for inc in incidents:
            # Blast Radius Calculation: If Hub_Site_List has items, this is a major outage
            is_hub_impact = len(inc.get("Hub_Site_List", [])) > 0
            
            # Extract and flatten the record
            record = {
                "Region_Key": region_name, # e.g., NGA
                "Priority_Region": inc.get("Region", "Unknown"), # e.g., "P2 NGA"
                "Window_Start": inc.get("Window_Start", ""),
                "Start_TS": inc.get("start_ts", 0),
                "OOS_Count": inc.get("OOS_Count", 0),
                "Total_Rank": inc.get("Total_Rank", 999999), # Lower rank = higher priority
                
                # Hardware / Alarms
                "Power_Count": inc.get("Power_Count", 0),
                "TX_Count": inc.get("TX_Count", 0),
                "RF_Count": inc.get("RF_Count", 0),
                "HW_Count": inc.get("HW_Count", 0),
                
                # Lists (Kept as lists for UI rendering, but joined as strings for searching)
                "OOS_Location_List": inc.get("OOS_Location_List", []),
                "Hub_Site_List": inc.get("Hub_Site_List", []),
                "County_Names": inc.get("County_Names", []),
                
                # Calculated / Extracted Meta
                "Is_Hub_Impact": is_hub_impact,
                "RCA": inc.get("RCA", "Pending Analysis"),
                
                # We join counties into a single string to make text-filtering easier later
                "County_String": ", ".join(inc.get("County_Names", []))
            }
            flat_incidents.append(record)

    # 4. DATAFRAME CONVERSION
    # Convert the list of dictionaries into a Pandas DataFrame for vectorized operations
    df = pd.DataFrame(flat_incidents)
    
    # If the dataframe is empty (network is 100% healthy), handle gracefully to prevent UI crashes
    if df.empty:
        # Create an empty dataframe with the expected columns
        expected_cols = ["Region_Key", "Priority_Region", "Window_Start", "OOS_Count", "Total_Rank", "Is_Hub_Impact"]
        df = pd.DataFrame(columns=expected_cols)

    return df, metadata, regional_kpis


# ==========================================
# 🎯 TACTICAL FILTERING LOGIC
# ==========================================

def filter_incident_data(df: pd.DataFrame, selected_regions: list, search_query: str = "") -> pd.DataFrame:
    """
    Applies user-selected filters to the DataFrame. 
    Kept separate from ingestion to ensure rapid UI responsiveness.
    """
    if df.empty:
        return df

    filtered_df = df.copy()

    # 1. Filter by Region (if the user selected any in the UI sidebar)
    if selected_regions:
        filtered_df = filtered_df[filtered_df["Region_Key"].isin(selected_regions)]

    # 2. Text-based Search (Fuzzy matching across Locations and Counties)
    if search_query:
        search_query = search_query.lower()
        
        # We check if the search query exists in the Region string, County string, or RCA
        mask = (
            filtered_df["Priority_Region"].str.lower().str.contains(search_query, na=False) |
            filtered_df["County_String"].str.lower().str.contains(search_query, na=False) |
            filtered_df["RCA"].str.lower().str.contains(search_query, na=False)
        )
        filtered_df = filtered_df[mask]

    # 3. Always sort by Total_Rank ascending (Lowest rank number = Highest Business Value)
    # This aligns with our Operational Rule: Prioritize Quality over Quantity
    if "Total_Rank" in filtered_df.columns:
        filtered_df = filtered_df.sort_values(by="Total_Rank", ascending=True)

    return filtered_df