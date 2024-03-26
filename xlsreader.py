import streamlit as st
import pandas as pd

uploaded_file = st.sidebar.file_uploader("Upload your input xls file", type=["xls"])
if uploaded_file is not None:
    xls = pd.ExcelFile(uploaded_file)
    # sheetX = xls.parse(2, header=1)
    # sheetX
    # var1 = sheetX['Is a contact']
    # var1

    for sheet_name in xls.sheet_names:
        sheetX = xls.parse(sheet_name, header=1)
        # Do something with sheetX, such as processing or analysis
        sheet_name
        sheetX