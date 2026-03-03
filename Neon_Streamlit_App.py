import streamlit as st
import pandas as pd
import os

# Import our decoupled modules
import data_engine
import ui_components

# ==========================================
# ⚙️ 1. PAGE CONFIGURATION
# Must be the very first Streamlit command
# ==========================================
st.set_page_config(
    page_title="Neon Ops Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # ==========================================
    # 🎨 2. INJECT UI STYLES
    # ==========================================
    ui_components.inject_neon_theme()

    # ==========================================
    # 📡 3. DATA INGESTION
    # ==========================================
      # Ensure this is imported at the top of your file

    with st.spinner("📡 Syncing with Network Data..."):
        # 1. Get the directory where Neon_Streamli_App.py lives
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Dynamically route into the 'data' folder
        target_file = os.path.join(current_dir, "data", "Phase1result.txt")
        
        # 3. Pass the absolute path to the Data Engine
        df, metadata, regional_kpis = data_engine.load_and_process_data(target_file)

    # ==========================================
    # 🎛️ 4. SIDEBAR: COMMAND & CONTROL
    # ==========================================
    with st.sidebar:
        st.markdown("## 🖥️ NEON OPS C2")
        st.caption(f"Last Refreshed: {metadata.get('last_refreshed', 'Unknown')}")
        st.markdown("---")
        
        st.markdown("### 🎯 Tactical Filters")
        
        # Dynamically populate region options based on available data
        available_regions = list(regional_kpis.keys())
        selected_regions = st.multiselect(
            "Filter by Region:",
            options=available_regions,
            default=[]
        )
        
        # Text search for RCAs, Counties, or specific sites
        search_query = st.text_input(
            "🔍 Search Incident (Location, RCA):",
            placeholder="e.g., KZN, Link Issue, PELLA..."
        )
        
        st.markdown("---")
        
        # Manual cache clearing for NOC engineers who need immediate updates
        if st.button("🔄 Force Data Sync", use_container_width=True):
            data_engine.load_and_process_data.clear()
            st.rerun()

    # ==========================================
    # 📊 5. MAIN DASHBOARD RENDERING
    # ==========================================
    # Render the top row of pulsing regional cards
    ui_components.render_regional_kpis(regional_kpis)
    
    st.markdown("---")
    
    # Pass the sidebar inputs to the data engine for rapid filtering
    filtered_df = data_engine.filter_incident_data(
        df=df, 
        selected_regions=selected_regions, 
        search_query=search_query
    )
    
    # Render the filtered incidents in the interactive accordion queue
    ui_components.render_incident_list(filtered_df)

    # ==========================================
    # 📥 6. DATA EXPORT (PRD Requirement)
    # ==========================================
    if not filtered_df.empty:
        st.markdown("---")
        # Convert filtered dataframe to CSV for easy download
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.download_button(
                label="📥 Download Shift Report (CSV)",
                data=csv_data,
                file_name="Neon_Shift_Report.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True
            )

if __name__ == "__main__":
    main()