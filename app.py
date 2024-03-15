import streamlit as st
import pandas as pd
st.write("""
            # My First StreamLit!
            Hello world!
        """)

tab1, tab2 = st.tabs(["Tab 1", "Tab2"])
tab1.write("this is tab 1")
tab2.write("this is tab 2")

data_frame = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40],
})

# # You can also use "with" notation:
# with tab1:
#     st.radio('Select one:', [1, 2])
#     st.write('Below is a DataFrame:', data_frame, 'Above is a dataframe.')

# with tab2:
#     st.write(1234)
#     "WHATS UPPPPP"
#     data_frame
#     {'foo': 'bar', 'fu': 'ba'}

# st.metric(label="Temp", value="273 K", delta="1.2 K")

# col1, col2 = st.columns(2)
# col1.write('Column 1')
# col2.write('Column 2')
# with col1:
#     st.write('This is column 1')

# # Group multiple widgets:
# with st.form(key='my_form'):
#     username = st.text_input('Username')
#     password = st.text_input('Password')
#     st.form_submit_button('Login')

# st.button('Hit me')
# data = b'Your binary data here'  # Replace with your binary data
# file_name = 'example.txt'  # Replace with your desired file name

# st.download_button('Download Data', data, file_name)

sampleNumber = st.number_input('Num:')
for i in range(int(sampleNumber)):
    st.write("Datad")

SampleBox = st.sidebar.selectbox('I:', ['f', 'd'])
if SampleBox == 'f':
    st.write("Data")
if SampleBox == 'd':
    st.write(data_frame)

my_slider_val = st.slider('Quinn Mallory', 1, 88)
st.write(my_slider_val)
