import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network
import re, os

def extract_emails(text):
    match = re.search(r'(.+@[A-Za-z]+.com)', str(text))
    if match:
        return match.group(1)
    else:
        return None
    
def extract_phone(parties):
    match_to = re.search(r'To:\s*\+*(\d+)', parties)
    match_from = re.search(r'From:\s*\+*(\d+)', parties)
    if match_to and match_from:
        return match_from.group(1), match_to.group(1)
    elif match_to:
        return None, match_to.group(1)
    elif match_from:
        return match_from.group(1), None
    else:
        return None, None
    
uploaded_file = st.sidebar.file_uploader("Upload your input xls file", type=["xls", "xlsx"])
if uploaded_file is not None:
    xls = pd.ExcelFile(uploaded_file)

    # Device Information
    device_info = xls.parse("Device Information", header=1)
    device_info['Name'] = device_info['Name'].str.strip()
    android_id = device_info[device_info["Name"] == "Android ID"]['Value'] # Extracted User Device ID

    # Emails
    emails = xls.parse("Emails", header=1)
    emails['Email (From:)'] = emails['From'].apply(extract_emails)
    emails['Email (To:)'] = emails['To'].apply(extract_emails)
    emails.dropna(subset=['Email (From:)', 'Email (To:)'], how='all', inplace=True)
    emails['Email (From:)'].fillna(android_id.iloc[0], inplace=True)
    emails['Email (To:)'].fillna(android_id.iloc[0], inplace=True)
    all_emails = set(emails['Email (To:)'].dropna()) | set(emails['Email (From:)'].dropna())
    emails['to_from_tuple'] = list(zip(emails['Email (From:)'], emails['Email (To:)']))
    tuple_counts3 = emails['to_from_tuple'].value_counts()
    df_email = pd.DataFrame(columns=['from', 'to', 'weight'])  # Initialize an empty DataFrame
    for (from_num, to_num), count in tuple_counts3.items():
        df_email.loc[len(df_email)] = [from_num, to_num, count**0.5]

    # Set header title
    st.title('Network Graph Visualization')
    
    # Define list of selection options and sort alphabetically
    list = ['Call', 'Instant Messages', 'Email']
    list.sort()

    # Implement multiselect dropdown menu for option selection (returns a list)
    selected_options = st.multiselect('Select option(s) to visualize', list)

    heading_text = ", ".join(selected_options) + " Network"
    st.header(heading_text)
    # Set info message on initial site load
    if len(selected_options) == 0:
        st.text('Choose at least 1 option to start')

    # Create network graph when user selects >= 1 item
    else:
            # Check if both 'Email' and 'Instant Messages' are selected
        if "Email" in selected_options and "Instant Messages" in selected_options:
            # Create networkx graph object from pandas dataframe for email
            G_email = nx.from_pandas_edgelist(df_email, 'from', 'to', 'weight')
            
            # Create networkx graph object from pandas dataframe for instant messages
            G_instant_messages = nx.from_pandas_edgelist(df_instant_messages, 'from', 'to', 'weight')
            
            # Combine the two graphs
            G_combined = nx.compose(G_email, G_instant_messages)
            
            # Initiate PyVis network object
            combined_net = Network(
                            height='450px',
                            width='100%',
                            bgcolor='#121925',
                            font_color='white',
                            directed=True
                            )

            # Take Networkx graph and translate it to a PyVis graph format
            combined_net.from_nx(G_combined)

            # Generate network with specific layout settings
            combined_net.repulsion(
                                node_distance=420,
                                central_gravity=0.33,
                                spring_length=110,
                                spring_strength=0.10,
                                damping=0.95
                            )

            # Save and read graph as HTML file (on Streamlit Sharing)
            
            path = 'tmp'
            if not os.path.exists(path):
                os.makedirs(path)
            combined_net.save_graph(f'{path}/pyvis_combined_graph.html')
            HtmlFile = open(f'{path}/pyvis_combined_graph.html', 'r', encoding='utf-8')
            # Load HTML file in HTML component for display on Streamlit page
            components.html(HtmlFile.read(), height=470)

        if "Email" in selected_options:
        # Create networkx graph object from pandas dataframe
            G_email = nx.from_pandas_edgelist(m, 'from', 'to', 'weight')
            
            # Initiate PyVis network object
            email_net = Network(
                            height='450px',
                            width='100%',
                            bgcolor='#121925',
                            font_color='white',
                            directed=True
                            )

            # Take Networkx graph and translate it to a PyVis graph format
            email_net.from_nx(G_email)

            # Generate network with specific layout settings
            email_net.repulsion(
                                node_distance=420,
                                central_gravity=0.33,
                                spring_length=110,
                                spring_strength=0.10,
                                damping=0.95
                            )

            # Save and read graph as HTML file (on Streamlit Sharing)
            
            path = 'tmp'
            if not os.path.exists(path):
                os.makedirs(path)
            email_net.save_graph(f'{path}/pyvis_graph.html')
            HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')
            # Load HTML file in HTML component for display on Streamlit page
            components.html(HtmlFile.read(), height=470)

