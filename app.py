import streamlit as st
import pandas as pd
import requests
from io import BytesIO

def app():
    st.title("Excel/CSV Uploader & Internal POST Simulation")

    # ------------------------------------------------------------------------------
    # 1. CONFIGURATION OPTIONS
    # ------------------------------------------------------------------------------
    st.sidebar.header("Configuration")
    endpoint_url = st.sidebar.text_input(
        label="Endpoint URL (placeholder)",
        value="http://localhost:8501/post-endpoint",
        help="Type a dummy or real endpoint URL here."
    )
    simulate_local_post = st.sidebar.checkbox(
        label="Simulate local API receiver?",
        value=True,
        help="If checked, we'll pretend to POST to ourselves and display the data."
    )

    # ------------------------------------------------------------------------------
    # 2. FILE UPLOAD
    # ------------------------------------------------------------------------------
    uploaded_file = st.file_uploader(
        label="Upload a data file (Excel or CSV)",
        type=["xlsx", "xls", "csv"],
        help="Upload your Excel or CSV file. Each row represents one item. The first column is the main item; the rest are children."
    )

    if uploaded_file is not None:
        # Determine file type and read into a Pandas DataFrame
        if uploaded_file.name.lower().endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("Uploaded File Preview")
        st.dataframe(df)

        # ------------------------------------------------------------------------------
        # 3. PREPARE THE DATA PAYLOAD
        # ------------------------------------------------------------------------------
        data_list = []
        for _, row in df.iterrows():
            # Use "result_code" as the main key 
            main_item = row["result_code"]
            # Ignore the first 2 columns and the "result_code" column itself
            children = row.drop([df.columns[0], df.columns[1], "result_code"], errors="ignore").to_dict()
            data_list.append({
                "main_item": main_item,
                "children": children
            })

        st.subheader("Prepared JSON payload")
        st.json(data_list)

        # ------------------------------------------------------------------------------
        # 4. SEND TO API (SIMULATION)
        # ------------------------------------------------------------------------------
        if st.button("Send Data"):
            if simulate_local_post:
                st.session_state["api_payload"] = data_list
                st.success("Data 'posted' to internal placeholder endpoint!")
            else:
                try:
                    response = requests.post(endpoint_url, json=data_list)
                    response.raise_for_status()
                    st.session_state["api_payload"] = response.json()
                    st.success("Data successfully posted to real endpoint!")
                except Exception as e:
                    st.error(f"Failed to POST data: {e}")

    # ------------------------------------------------------------------------------
    # 5. (OPTIONAL) DISPLAY WHAT THE "RECEIVER" GOT
    # ------------------------------------------------------------------------------
    st.subheader("Internal API Receiver")
    st.write("Below simulates what an internal endpoint would have received in a POST.")
    if "api_payload" in st.session_state:
        st.json(st.session_state["api_payload"])
    else:
        st.info("No data has been 'received' yet.")

# ------------------------------------------------------------------------------
# Streamlit entry point
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app()