import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network
import re, os, math
from googletrans import Translator

def extract_emails(text):
    """
    This function extracts emails from text.
    """
    match = re.search(r'(.+@[A-Za-z]+.com)', str(text))
    if match:
        return match.group(1)
    else:
        return None
    
def extract_phone(parties):
    """
    This function extracts phone numbers after "From: " and "To: " keywords.
    """
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
    
def extract_info(text):
    """  
    This function extracts phone numbers or android/phone ID if there is no phone number to be extracted.
    """
    match = re.search(r'\b(\d{4,})\b', str(text))
    if match:
        return match.group(1)
    else:
        match2 = re.search(r'\b([A-Za-z0-9]{12})\b', str(text))
        if match2:
          return match2.group(1)
        else:
          return None
    
def filter_subgraph(G_combined, nodes):
    """  
    This function creates and returns a subgraph containing only the relevant nodes and edges.
    """
    subgraph_nodes = []
    subgraph_edges = []

    # Loop through each node in the list of nodes
    for node in nodes:
        # Filter nodes based on the provided node value (case insensitive)
        subgraph_nodes.extend([n for n in G_combined.nodes() if node.lower() in str(n).lower()])
        # Filter edges connected to the filtered nodes
        subgraph_edges.extend([(u, v) for u, v in G_combined.edges() if u in subgraph_nodes or v in subgraph_nodes])

    # Remove duplicate nodes and edges
    subgraph_nodes = list(set(subgraph_nodes))
    subgraph_edges = list(set(subgraph_edges))

    # Create and return the subgraph
    return G_combined.subgraph(subgraph_nodes).copy(), subgraph_edges
    
def parse_xls_file(uploaded_file):
    """  
    This functions reads the xlsx/xls file and return the relevant sheets interested.
    """
    try:
        xls = pd.ExcelFile(uploaded_file)
        device_info = xls.parse("Device Information", header=1)
    except:
        device_info = None
    try:
        call_log = xls.parse("Call Log", header=1)
    except:
        call_log = None
    try:
        instant_msgs = xls.parse("Instant Messages", header=1)
    except:
        instant_msgs = None
    try:
        emails = xls.parse("Emails", header=1)
    except:
        emails = None
    return device_info, call_log, instant_msgs, emails
    
def main():
    """  
    This function holds the main code for the streamlit website.
    """
    uploaded_files = st.sidebar.file_uploader("Upload your input xls file", type=["xls", "xlsx"], accept_multiple_files=True)

    if uploaded_files:
        st.title('Network Graph Visualization', anchor="")
        list_options = ['Call', 'Instant Messages', 'Email']
        list_options.sort()

        # Implement multiselect dropdown menu for option selection (returns a list)
        selected_options = st.multiselect('Select option(s) to visualize', list_options)
        output_list = []
        node_list = []

        df_email = pd.DataFrame(columns=['from', 'to', 'weight']) # Initialize an empty DataFrame
        df_imsg = pd.DataFrame(columns=['from', 'to', 'weight'])  # Initialize an empty DataFrame
        df_call = pd.DataFrame(columns=['from', 'to', 'weight'])  # Initialize an empty DataFrame

        G_combined = nx.DiGraph()
        G_email_list, G_call_list, G_instant_messages_list = [], [], []
        if len(selected_options) == 0:
                st.text('Choose at least 1 option to start')
        if len(selected_options):
            for uploaded_file in uploaded_files:
                missing_sheets = []
                device_info, call_log, instant_msgs, emails = parse_xls_file(uploaded_file)

                # Device Information
                if device_info is not None:
                    device_info['Name'] = device_info['Name'].str.strip()
                    android_id = device_info[device_info["Name"] == "Android ID"]['Value'] # Extracted User Device ID
                    if android_id.empty:
                        missing_sheets.append("Device Information (does not have Android ID)")
                else:
                    missing_sheets.append("Device Information")

                if not android_id.empty:
                    # Call Log
                    if call_log is not None:
                        call_log['Phone (From:)'], call_log['Phone (To:)'] = zip(*call_log['Parties'].apply(extract_phone))
                        call_log.dropna(subset=['Phone (From:)', 'Phone (To:)'], how='all', inplace=True)
                        call_log['Phone (From:)'].fillna(android_id.iloc[0], inplace=True)
                        call_log['Phone (To:)'].fillna(android_id.iloc[0], inplace=True)    
                        call_log['to_from_tuple'] = list(zip(call_log['Phone (From:)'], call_log['Phone (To:)']))
                        tuple_counts = call_log['to_from_tuple'].value_counts()
                        df_call = pd.DataFrame(columns=['from', 'to', 'weight'])  # Initialize an empty DataFrame
                        for (from_num, to_num), count in tuple_counts.items():
                            df_call.loc[len(df_call)] = [from_num, to_num, math.log((count + 5)**0.5)]
                    else:
                        missing_sheets.append("Call Log")

                    # Instant Messages
                    if instant_msgs is not None:
                        instant_msgs['Phone (From:)'] = instant_msgs['From'].apply(extract_info)
                        instant_msgs['Phone (To:)'] = instant_msgs['To'].apply(extract_info)
                        instant_msgs.dropna(subset=['Phone (From:)', 'Phone (To:)'], how='all', inplace=True)
                        instant_msgs['Phone (To:)'].fillna(android_id.iloc[0], inplace=True)
                        instant_msgs['Phone (From:)'].fillna(android_id.iloc[0], inplace=True)
                        instant_msgs['to_from_tuple'] = list(zip(instant_msgs['Phone (From:)'], instant_msgs['Phone (To:)']))
                        tuple_counts2 = instant_msgs['to_from_tuple'].value_counts()
                        df_imsg = pd.DataFrame(columns=['from', 'to', 'weight'])  # Initialize an empty DataFrame
                        for (from_num, to_num), count in tuple_counts2.items():
                            df_imsg.loc[len(df_imsg)] = [from_num, to_num, math.log((count + 5)**0.5)]
                    else:
                        missing_sheets.append("Instant Messages")

                    # Emails
                    if emails is not None:
                        emails['Email (From:)'] = emails['From'].apply(extract_emails)
                        emails['Email (To:)'] = emails['To'].apply(extract_emails)
                        emails.dropna(subset=['Email (From:)', 'Email (To:)'], how='all', inplace=True)
                        emails['Email (From:)'].fillna(android_id.iloc[0], inplace=True)
                        emails['Email (To:)'].fillna(android_id.iloc[0], inplace=True)
                        emails['to_from_tuple'] = list(zip(emails['Email (From:)'], emails['Email (To:)']))
                        tuple_counts3 = emails['to_from_tuple'].value_counts()
                        df_email = pd.DataFrame(columns=['from', 'to', 'weight'])  # Initialize an empty DataFrame
                        for (from_num, to_num), count in tuple_counts3.items():
                            df_email.loc[len(df_email)] = [from_num, to_num, math.log((count + 5)**0.5)]
                    else:
                        missing_sheets.append("Emails")

                    # Create networkx graph objects
                    G_email = nx.from_pandas_edgelist(df_email, source='from', target='to', edge_attr='weight', create_using=nx.DiGraph)
                    G_instant_messages = nx.from_pandas_edgelist(df_imsg, source='from', target='to', edge_attr='weight', create_using=nx.DiGraph)
                    G_call = nx.from_pandas_edgelist(df_call, source='from', target='to', edge_attr='weight', create_using=nx.DiGraph)

                    if "Email" in selected_options:
                        G_combined = nx.compose(G_combined, G_email)
                        G_email_list.append(G_email)

                    if "Instant Messages" in selected_options:
                        G_combined = nx.compose(G_combined, G_instant_messages)
                        G_instant_messages_list.append(G_instant_messages)

                    if "Call" in selected_options:
                        G_combined = nx.compose(G_combined, G_call)
                        G_call_list.append(G_call)

                if missing_sheets:
                    output_list.append(f"{uploaded_file.name} does not have the following sheet(s): {', '.join(missing_sheets)}")
                
        for node, data in G_combined.nodes(data=True):
            if any(node in G.nodes() for G in G_email_list) and any(node in G.nodes() for G in G_instant_messages_list) and any(node in G.nodes() for G in G_call_list):
                data['color'] = '#5c5c5c'
            elif any(node in G.nodes() for G in G_email_list) and any(node in G.nodes() for G in G_instant_messages_list):
                data['color'] = 'green'
            elif any(node in G.nodes() for G in G_email_list) and any(node in G.nodes() for G in G_call_list):
                data['color'] = '#8f9aff'
            elif any(node in G.nodes() for G in G_instant_messages_list) and any(node in G.nodes() for G in G_call_list):
                data['color'] = 'orange'
            elif any(node in G.nodes() for G in G_email_list):
                data['color'] = '#427bff'
            elif any(node in G.nodes() for G in G_instant_messages_list):
                data['color'] = '#999403'
            elif any(node in G.nodes() for G in G_call_list):
                data['color'] = 'red'

        for source, target, data in G_combined.edges(data=True):
            if any((source, target) in G.edges() for G in G_email_list) and any((source, target) in G.edges() for G in G_instant_messages_list) and any((source, target) in G.edges() for G in G_call_list):
                data['color'] = '#5c5c5c'
            elif any((source, target) in G.edges() for G in G_email_list) and any((source, target) in G.edges() for G in G_instant_messages_list):
                data['color'] = 'green'
            elif any((source, target) in G.edges() for G in G_email_list) and any((source, target) in G.edges() for G in G_call_list):
                data['color'] = '#8f9aff'
            elif any((source, target) in G.edges() for G in G_instant_messages_list) and any((source, target) in G.edges() for G in G_call_list):
                data['color'] = 'orange'
            elif any((source, target) in G.edges() for G in G_email_list):
                data['color'] = '#427bff'
            elif any((source, target) in G.edges() for G in G_instant_messages_list):
                data['color'] = '#999403'
            elif any((source, target) in G.edges() for G in G_call_list):
                data['color'] = 'red'
            
        all_nodes = set()
        all_nodes.update(G_combined.nodes())
        node_list.extend(all_nodes)
        node_list = sorted(set(node_list))
        search_node = st.multiselect("Select nodes", node_list)
        heading_text = ", ".join(selected_options) + " Network"
        st.header(heading_text)

        if search_node:
            nodes_in_subgraph = set()
            for node in search_node:
                try:
                    try:
                        successors = list(G_combined.successors(node))
                        nodes_in_subgraph.update(successors)
                    except:
                        st.write(f"Node {node} has no successors.")
                    try:
                        predecessors = list(G_combined.predecessors(node))
                        nodes_in_subgraph.update(predecessors)
                    except:
                        st.write(f"Node {node} has no predecessors.")
                    nodes_in_subgraph.add(node)
                except nx.exception.NetworkXError:
                    st.write(f"Node {node} is not in the graph.")

            G_combined = G_combined.subgraph(nodes_in_subgraph)
    
        combined_net = Network(
                        height='450px',
                        width='100%',
                        bgcolor='black',
                        font_color='white',
                        directed=True
                        )

        combined_net.from_nx(G_combined)
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

        components.html(HtmlFile.read(), height=470)

        legend_html = """
        <div style="background-color: black; padding: 10px; border-radius: 5px;">
            <h3>Legend</h3>
            <ul>
                <li><span style="color: #427bff;">Email</span></li>
                <li><span style="color: #999403;">Instant Messages</span></li>
                <li><span style="color: red;">Call</span></li>
                <li><span style="color: green;">Email and Instant Messages</span></li>
                <li><span style="color: #8f9aff;">Email and Call</span></li>
                <li><span style="color: orange;">Instant Messages and Call</span></li>
                <li><span style="color: #5c5c5c;">All</span></li>
            </ul>
        </div>
        """
        st.markdown(legend_html, unsafe_allow_html=True)
        st.sidebar.markdown('\n\n'.join(output_list))
    else:
        st.write("""
                    # Network Graph Visualization
                    ## Description
                    Visualizing network(s) between contacts in various files by using 
                    `Call Log`, `Device Information`, `Emails`, `Instant Messages`.

                    Upload one or more xls/xlsx file(s) at the sidebar to see the network graph visualization.
                """)
        
if __name__ == "__main__":
    main()