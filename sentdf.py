import streamlit as st
import pandas as pd


uploaded_file = st.sidebar.file_uploader("Upload your input CSV file", type=["csv"])
if uploaded_file is not None:
    input_df = pd.read_csv(uploaded_file)
else:
    def user_input_features():
        area = st.sidebar.selectbox("Area", ("NYE", "WST", "TXS"))
        sex = st.sidebar.selectbox("Sex", ("male", "female"))
        bill_length_mm = st.sidebar.slider("Bill length (mm)", 32.1, 59.6, 43.9)
        bill_depth_mm = st.sidebar.slider("Bill depth (mm)", 13.1, 21.5, 17.2)
        flipper_length_mm = st.sidebar.slider("Flipper length (mm)", 172.0, 231.0, 201.0)
        body_mass_g = st.sidebar.slider("Body mass (g)", 2700.0, 6300.0, 4207.0)
        data = {
            "area": area,
            "bill_length_mm": bill_length_mm,
            "bill_depth_mm": bill_depth_mm,
            "flipper_length_mm": flipper_length_mm,
            "body_mass_g": body_mass_g,
            "sex": sex,
        }
        features = pd.DataFrame(data, index=[0])
        return features

    input_df = user_input_features()

st.write("Hello")

input_df
"Show row 0 of area column", input_df["area"][0]
"Bill Ratio: ", input_df["bill_length_mm"][0] / input_df["bill_depth_mm"][0]

x_axis = st.selectbox("x-axis", input_df.columns, index=0)
y_axis = st.selectbox("y-axis", input_df.columns, index=1)
st.line_chart(input_df, x=x_axis, y=y_axis)
