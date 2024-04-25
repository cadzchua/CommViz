from streamlit_agraph import agraph, Node, Edge, Config
import pandas as pd
import re
import networkx as nx
import matplotlib.pyplot as plt
from googletrans import Translator # pip install googletrans==3.1.0a0

file = "C:\\Users\\cadid\\Downloads\\file_17.xlsx"

def index_change(file, sheet_name):
  excel = pd.read_excel(file, sheet_name)
  excel.columns = excel.iloc[0]
  excel = excel[1:]
  excel.reset_index(drop=True, inplace=True)
  return excel

def translate_to_english(text):
    try:
        translator = Translator()
        translated = translator.translate(text, src='ar', dest='en')
        return translated.text
    except Exception as e:
        # Handle other exceptions, print the error for debugging
        print(f"An error occurred: {e}")
        return text

def extract_phone(parties):
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