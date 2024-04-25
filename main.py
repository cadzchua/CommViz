import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import pandas as pd
import re
import networkx as nx
import matplotlib.pyplot as plt
from googletrans import Translator # pip install googletrans==3.1.0a0

def translate_to_english(text):
    """
    A function that translates arabic to english.
    """
    try:
        translator = Translator()
        translated = translator.translate(text, src='ar', dest='en')
        return translated.text
    except Exception as e:
        # Handle other exceptions, print the error for debugging
        print(f"An error occurred: {e}")
        return text

def extract_phone(parties):
    """ 
    A function that extracts phone numbers. 
    """
    match_to = re.search(r'To: ?\+?(\d+)', parties)
    match_from = re.search(r'From: ?\+?(\d+)', parties)
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

def extract_emails(text):
    match = re.search(r'(.+@[A-Za-z]+.com)', str(text))
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
    call_log["Parties"] = call_log["Parties"].apply(translate_to_english)
    call_log['Phone (From:)'], call_log['Phone (To:)'] = zip(*call_log['Parties'].apply(extract_phone))
    call_log.dropna(axis=1, inplace=True, how='all')
    call_log['Phone (From:)'].fillna(android_id.iloc[0], inplace=True)
    call_log['Phone (To:)'].fillna(android_id.iloc[0], inplace=True)
    call_log = call_log[['Phone (From:)', 'Phone (To:)']]
    all_phone_numbers = set(call_log['Phone (To:)'].dropna()) | set(call_log['Phone (From:)'].dropna())
    call_log['to_from_tuple'] = list(zip(call_log['Phone (From:)'], call_log['Phone (To:)']))
    tuple_counts = call_log['to_from_tuple'].value_counts()
    for tup, count in tuple_counts.items():
        print(tup, count)

    # Instant Messages
    instant_msgs = xls.parse("Instant Messages", header=1)
    instant_msgs['Phone (From:)'] = instant_msgs['From'].apply(extract_phone_number)
    instant_msgs['Phone (To:)'] = instant_msgs['To'].apply(extract_phone_number)
    instant_msgs.dropna(subset=['Phone (From:)', 'Phone (To:)'], how='all', inplace=True)
    instant_msgs['Phone (To:)'].fillna(android_id.iloc[0], inplace=True)
    all_instant_messages_numbers = set(instant_msgs['Phone (To:)'].dropna()) | set(instant_msgs['Phone (From:)'].dropna())
    instant_msgs['to_from_tuple'] = list(zip(instant_msgs['Phone (From:)'], instant_msgs['Phone (To:)']))
    tuple_counts2 = instant_msgs['to_from_tuple'].value_counts()
    for tup, count in tuple_counts.items():
        print(tup, count)

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
    for (x,y), count in tuple_counts3.items():
        print(x, y, count)