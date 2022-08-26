#!/usr/bin/env python
# coding: utf-8

# In[6]:



import datetime as dt
import datetime as datetime
import time
import numpy as np
import pandas as pd
import pandas_ta as ta
import requests
import streamlit as st
from glob import glob

st.set_page_config(page_title='Strategies Detailed Info', page_icon=':tada:',layout='wide')
st.markdown("# Strategies Detailed Info")
st.sidebar.markdown("# Strategies Detailed Info")



master=pd.read_csv('Trading Patterns Anomalies 2022_Updated.csv')
image1=pd.read_csv('images.csv')
user_input = st.empty()

user_input1 = user_input.text_input("Enter Password", '')

if(user_input1=='XCteam@276'):
  st.dataframe(master)
  y= pd.DataFrame((image1['name'].unique()))
  st.markdown("# Trade-Log")
  option = st.selectbox('Select Strategy', y)
  op=image1[image1['name']==option]
  st.image(op['location'].iloc[0])
  if user_input1 != "":
      user_input.empty()

