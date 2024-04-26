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
    
def extract_phone_number(text):
    match = re.search(r'\b(\d{4,})\b', str(text))
    if match:
        return match.group(1)
    else:
        return None
    
uploaded_file = st.sidebar.file_uploader("Upload your input xls file", type=["xls", "xlsx"])
if uploaded_file is not None:
    xls = pd.ExcelFile(uploaded_file)

    # Device Information
    device_info = xls.parse("Device Information", header=1)
    device_info['Name'] = device_info['Name'].str.strip()
    android_id = device_info[device_info["Name"] == "Android ID"]['Value'] # Extracted User Device ID

    # Call Log
    call_log = xls.parse("Call Log", header=1)
    call_log['Phone (From:)'], call_log['Phone (To:)'] = zip(*call_log['Parties'].apply(extract_phone))
    call_log.dropna(subset=['Phone (From:)', 'Phone (To:)'], how='all', inplace=True)
    call_log['Phone (From:)'].fillna(android_id.iloc[0], inplace=True)
    call_log['Phone (To:)'].fillna(android_id.iloc[0], inplace=True)
    call_log['to_from_tuple'] = list(zip(call_log['Phone (From:)'], call_log['Phone (To:)']))
    tuple_counts = call_log['to_from_tuple'].value_counts()
    df_call = pd.DataFrame(columns=['from', 'to', 'weight'])  # Initialize an empty DataFrame
    for (from_num, to_num), count in tuple_counts.items():
        df_call.loc[len(df_call)] = [from_num, to_num, count**0.66]

    # Instant Messages
    instant_msgs = call_log = xls.parse("Instant Messages", header=1)
    instant_msgs['Phone (From:)'] = instant_msgs['From'].apply(extract_phone_number)
    instant_msgs['Phone (To:)'] = instant_msgs['To'].apply(extract_phone_number)
    instant_msgs.dropna(subset=['Phone (From:)', 'Phone (To:)'], how='all', inplace=True)
    instant_msgs['Phone (To:)'].fillna(android_id.iloc[0], inplace=True)
    instant_msgs['Phone (From:)'].fillna(android_id.iloc[0], inplace=True)
    instant_msgs['to_from_tuple'] = list(zip(instant_msgs['Phone (From:)'], instant_msgs['Phone (To:)']))
    tuple_counts2 = instant_msgs['to_from_tuple'].value_counts()
    df_imsg = pd.DataFrame(columns=['from', 'to', 'weight'])  # Initialize an empty DataFrame
    for (from_num, to_num), count in tuple_counts2.items():
        df_imsg.loc[len(df_imsg)] = [from_num, to_num, count**0.66]

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
        df_email.loc[len(df_email)] = [from_num, to_num, count**0.66]

    # Set header title
    st.title('Network Graph Visualization')
    
    # Define list of selection options and sort alphabetically
    list = ['Call', 'Instant Messages', 'Email']
    list.sort()

    # Implement multiselect dropdown menu for option selection (returns a list)
    selected_options = st.multiselect('Select option(s) to visualize', list)

    heading_text = ", ".join(selected_options) + " Network"
    st.header(heading_text)
    # Create networkx graph objects
    G_email = nx.from_pandas_edgelist(df_email, 'from', 'to', 'weight')
    G_instant_messages = nx.from_pandas_edgelist(df_imsg, 'from', 'to', 'weight')
    G_call = nx.from_pandas_edgelist(df_call, 'from', 'to', 'weight')

    G_combined = nx.Graph()
    if len(selected_options) == 0:
        st.text('Choose at least 1 option to start')

    elif len(selected_options) == 3:  # All three options selected
        G_combined = nx.compose_all([G_email, G_instant_messages, G_call])
        for node, data in G_combined.nodes(data=True):
            if node in G_email and node in G_instant_messages and node in G_call:
                data['color'] = '#5c5c5c'
            elif node in G_email and node in G_instant_messages:
                data['color'] = 'green'
            elif node in G_email and node in G_call:
                data['color'] = '#8f9aff'
            elif node in G_instant_messages and node in G_call:
                data['color'] = 'orange'
            elif node in G_email:
                data['color'] = '#427bff'
            elif node in G_instant_messages:
                data['color'] = 'yellow'
            elif node in G_call:
                data['color'] = 'red'

        for source, target, data in G_combined.edges(data=True):
            if (source, target) in G_email.edges() and (source, target) in G_instant_messages.edges() and (source, target) in G_call.edges():
                data['color'] = '#5c5c5c'
            elif (source, target) in G_email.edges() and (source, target) in G_instant_messages.edges():
                data['color'] = 'green'
            elif (source, target) in G_email.edges() and (source, target) in G_call.edges():
                data['color'] = '#8f9aff'
            elif (source, target) in G_instant_messages.edges() and (source, target) in G_call.edges():
                data['color'] = 'orange'
            elif (source, target) in G_email.edges():
                data['color'] = '#427bff'
            elif (source, target) in G_instant_messages.edges():
                data['color'] = 'yellow'
            elif (source, target) in G_call.edges():
                data['color'] = 'red'

    elif len(selected_options) == 2:  # Any two options selected
        if "Email" in selected_options and "Instant Messages" in selected_options:
            G_combined = nx.compose(G_email, G_instant_messages)
            for node, data in G_combined.nodes(data=True):
                if node in G_email and node in G_instant_messages:
                    data['color'] = 'green'
                elif node in G_email:
                    data['color'] = '#427bff'
                elif node in G_instant_messages:
                    data['color'] = 'yellow'

            for source, target, data in G_combined.edges(data=True):
                if (source, target) in G_email.edges() and (source, target) in G_instant_messages.edges():
                    data['color'] = 'green'
                elif (source, target) in G_email.edges():
                    data['color'] = '#427bff'
                elif (source, target) in G_instant_messages.edges():
                    data['color'] = 'yellow'
                
        elif "Email" in selected_options and "Call" in selected_options:
            G_combined = nx.compose(G_email, G_call)
            for node, data in G_combined.nodes(data=True):
                if node in G_email and node in G_call:
                    data['color'] = '#8f9aff'
                elif node in G_email:
                    data['color'] = '#427bff'
                elif node in G_call:
                    data['color'] = 'red'

            for source, target, data in G_combined.edges(data=True):
                if (source, target) in G_email.edges() and (source, target) in G_call.edges():
                    data['color'] = '#8f9aff'
                elif (source, target) in G_email.edges():
                    data['color'] = '#427bff'
                elif (source, target) in G_call.edges():
                    data['color'] = 'red'

        elif "Instant Messages" in selected_options and "Call" in selected_options:
            G_combined = nx.compose(G_instant_messages, G_call)
            for node, data in G_combined.nodes(data=True):
                if node in G_instant_messages and node in G_call:
                    data['color'] = 'orange'
                elif node in G_instant_messages:
                    data['color'] = 'yellow'
                elif node in G_call:
                    data['color'] = 'red'

            for source, target, data in G_combined.edges(data=True):
                if (source, target) in G_instant_messages.edges() and (source, target) in G_call.edges():
                    data['color'] = 'orange'
                elif (source, target) in G_instant_messages.edges():
                    data['color'] = 'yellow'
                elif (source, target) in G_call.edges():
                    data['color'] = 'red'

    elif len(selected_options) == 1:  # Any one option selected
        if "Email" in selected_options:
            G_combined = G_email
            for node, data in G_combined.nodes(data=True):
                if node in G_email:
                        data['color'] = '#427bff'
            for source, target, data in G_combined.edges(data=True):
                if (source, target) in G_email.edges():
                    data['color'] = '#427bff'

        elif "Instant Messages" in selected_options:
            G_combined = G_instant_messages
            for node, data in G_combined.nodes(data=True):
                if node in G_instant_messages:
                        data['color'] = 'yellow'
            for source, target, data in G_combined.edges(data=True):
                if (source, target) in G_call.edges():
                    data['color'] = 'yellow'

        elif "Call" in selected_options:
            G_combined = G_call
            for node, data in G_combined.nodes(data=True):
                if node in G_call:
                        data['color'] = 'red'
            for source, target, data in G_combined.edges(data=True):
                if (source, target) in G_call.edges():
                    data['color'] = 'red'

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

    legend_html = """
    <div style="background-color: black; padding: 10px; border-radius: 5px;">
        <h3>Legend</h3>
        <ul>
            <li><span style="color: #427bff;">Email</span></li>
            <li><span style="color: yellow;">Instant Messages</span></li>
            <li><span style="color: red;">Call</span></li>
            <li><span style="color: green;">Email and Instant Messages</span></li>
            <li><span style="color: #8f9aff;">Email and Call</span></li>
            <li><span style="color: orange;">Instant Messages and Call</span></li>
            <li><span style="color: #5c5c5c;">All</span></li>
        </ul>
    </div>
    """
    st.markdown(legend_html, unsafe_allow_html=True)
