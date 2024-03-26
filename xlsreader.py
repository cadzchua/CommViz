import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

uploaded_file = st.sidebar.file_uploader("Upload your input xls file", type=["xls"])
if uploaded_file is not None:
    xls = pd.ExcelFile(uploaded_file)
    # sheetX = xls.parse(2, header=1)
    # sheetX
    # var1 = sheetX['Is a contact']
    # var1

    # for sheet_name in xls.sheet_names:
    #     sheetX = xls.parse(sheet_name, header=1)
    #     # Do something with sheetX, such as processing or analysis
    #     sheet_name
    #     sheetX
    
    whatsapp_contacts = xls.parse("Analytics WhatsApp", header=1)
    whatsapp_contacts
    
# Create an empty graph
G = nx.Graph()

# Add nodes
G.add_node(1)
G.add_node(2)
G.add_node(3)

# Add edges
G.add_edge(1, 2)
G.add_edge(2, 3)
G.add_edge(3, 1)

# Draw the graph
nx.draw(G, with_labels=True, node_color='skyblue', node_size=2000, font_size=15, font_weight='bold')
# Save the plot to a file
plt.savefig("graph.png")
st.image('./graph.png')
# Close the plot to release memory (optional)
plt.close()