# Implementation Guide: Ops Command Center (Neon)

## Folder & File Structure
* `Neon_Streamlit_App.py`: The Main Controller. Handles sidebar routing, global state, search/sort filters, and triggers UI rendering.
* `data_engine.py`: The ETL layer. Responsible for opening `data/Phase1result.txt`, parsing the nested JSON, and flattening it into queryable Pandas DataFrames and dictionaries.
* `ui_components.py`: The View layer. Stores the CSS injections for the "Pulse" animations and the logic for generating the `st.expander` diagnostic tables.
* `config/RAN_Region_County_Mapping_With_IDs.json`: Static metadata used for enriching region/county lookups if necessary.

## Data Flow
1. User opens app -> `Neon_Streamlit_App.py` calls `data_engine.load_phase1_data()`.
2. App reads `data/Phase1result.txt`.
3. UI Filters (Sidebar) interact with the DataFrames.
4. Filtered data is passed to `ui_components.render_pulse_cards()` and `ui_components.render_incident_list()`.