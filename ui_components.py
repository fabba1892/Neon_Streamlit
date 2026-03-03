import streamlit as st
import pandas as pd

# ==========================================
# 🎨 1. THEME & CSS INJECTION
# ==========================================
def inject_neon_theme():
    """
    Injects the core Neon Cyberpunk CSS. 
    Handles the glowing pulse animations for critical SLAs.
    """
    custom_css = """
    <style>
        /* Base background handled by Streamlit config, these are overrides */
        .neon-card {
            background: #1e1e2d;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            color: #ffffff;
            border-bottom: 4px solid #334155; /* Default inactive border */
            margin-bottom: 15px;
        }
        .neon-title { color: #94a3b8; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }
        .neon-value { font-size: 2em; font-weight: bold; color: #ffffff; }
        
        /* Pulse Animations for Critical Faults */
        .pulse-red { border-bottom-color: #ef4444; animation: flash-red 1.5s infinite; }
        .pulse-orange { border-bottom-color: #f97316; animation: flash-orange 2s infinite; }
        .pulse-cyan { border-bottom-color: #00c8ff; }

        @keyframes flash-red { 0% { box-shadow: 0 0 0 0 rgba(239,68,68,0.7); } 70% { box-shadow: 0 0 0 10px rgba(239,68,68,0); } 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); } }
        @keyframes flash-orange { 0% { box-shadow: 0 0 0 0 rgba(249,115,22,0.7); } 70% { box-shadow: 0 0 0 10px rgba(249,115,22,0); } 100% { box-shadow: 0 0 0 0 rgba(249,115,22,0); } }
        
        /* Badges */
        .hub-badge { background-color: #ef4444; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8em; margin-left: 10px;}
        .rank-badge { background-color: #00c8ff; color: #0e1117; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8em;}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# 📊 2. TOP-LEVEL KPI CARDS
# ==========================================
def render_regional_kpis(regional_kpis: dict):
    """
    Dynamically renders the top row of regional status cards.
    Expects the regional_kpis dictionary from data_engine.py.
    """
    st.markdown("### 🌐 Regional Network Status")
    
    if not regional_kpis:
        st.info("No regional data available.")
        return

    # Dynamically create columns based on the number of regions
    cols = st.columns(len(regional_kpis))
    
    for idx, (region, data) in enumerate(regional_kpis.items()):
        total_oos = data.get("Total_OOS_Count", 0)
        
        # Determine pulse severity
        pulse_class = "pulse-cyan" # Healthy/Normal
        if total_oos > 100:
            pulse_class = "pulse-red"
        elif total_oos > 50:
            pulse_class = "pulse-orange"

        # Inject HTML for the card
        html_card = f"""
        <div class="neon-card {pulse_class}">
            <div class="neon-title">{region}</div>
            <div class="neon-value">{total_oos}</div>
            <div class="neon-title" style="font-size: 0.7em; margin-top:5px;">SITES DOWN</div>
        </div>
        """
        cols[idx].markdown(html_card, unsafe_allow_html=True)

# ==========================================
# 🚨 3. TACTICAL INCIDENT ACCORDIONS
# ==========================================
def render_incident_list(df: pd.DataFrame):
    """
    Renders the filtered DataFrame into an interactive, drill-down list.
    Designed for rapid NOC RCA and Hubsite identification.
    """
    st.markdown("### ⚡ Tactical Incident Queue")
    
    if df.empty:
        st.success("✅ Zero active incidents matching current filters. Network is stable.")
        return

    # Loop through the dataframe (already sorted by Total_Rank in data_engine)
    for _, row in df.iterrows():
        try:
            # 1. Build the Expander Header (High Signal Info)
            hub_warning = '<span class="hub-badge">⚠️ HUB IMPACT</span>' if row["Is_Hub_Impact"] else ""
            rank_display = f'<span class="rank-badge">Rank: {row["Total_Rank"]}</span>'
            
            # We use st.expander for native Streamlit interactability
            header_label = f"🔴 {row['Priority_Region']} | {row['OOS_Count']} Sites Down"
            
            with st.expander(header_label, expanded=False):
                # We inject a small HTML row for the badges right below the expander header
                st.markdown(f"{rank_display} {hub_warning}", unsafe_allow_html=True)
                st.write(f"**Root Cause Analysis:** {row['RCA']}")
                st.write(f"**Impacted Counties:** {row['County_String']}")
                
                # 2. Tech Impact Row (Native Streamlit Columns)
                st.markdown("##### 🛠️ Hardware Alarms")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("⚡ Power", row["Power_Count"])
                c2.metric("📡 TX", row["TX_Count"])
                c3.metric("📡 RF", row["RF_Count"])
                c4.metric("⚙️ HW", row["HW_Count"])
                
                # 3. Location & Blast Radius Lists
                col_loc, col_hub = st.columns(2)
                with col_loc:
                    st.markdown("**🌍 OOS Locations:**")
                    if row["OOS_Location_List"]:
                        # Convert list to a markdown bulleted list
                        st.markdown("\n".join([f"* {loc}" for loc in row["OOS_Location_List"]]))
                    else:
                        st.caption("No specific locations listed.")
                        
                with col_hub:
                    if row["Is_Hub_Impact"]:
                        st.markdown("**⚠️ Critical Hubs Down:**")
                        st.markdown("\n".join([f"* **{hub}**" for hub in row["Hub_Site_List"]]))
                        
        except Exception as e:
            # Fault isolation: If one row has corrupted data, it fails gracefully without killing the app
            st.error(f"Failed to render incident block. Error: {str(e)}")