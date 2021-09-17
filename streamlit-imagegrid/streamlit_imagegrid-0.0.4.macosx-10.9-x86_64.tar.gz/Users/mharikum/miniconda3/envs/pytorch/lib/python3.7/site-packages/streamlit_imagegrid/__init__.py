import streamlit.components.v1 as components
import streamlit as st
import uuid
import os
import requests
from PIL import Image
from io import BytesIO
import json
_RELEASE = True
_DEBUG = False
root_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(root_dir, "frontend/build")

if _DEBUG:
    urls = ["https://as1.ftcdn.net/jpg/01/41/02/26/500_F_141022623_Wi0PLc8Xi1K4FcPKF4UJAjNu6vuYjha5.jpg",
            "https://t4.ftcdn.net/jpg/02/65/19/21/240_F_265192146_GkxdiHss4XhAPPHkW2C6nBkrfrc4DxrJ.jpg",
            "https://t4.ftcdn.net/jpg/01/18/41/79/240_F_118417934_BYUeBM4c2TTFcbl9xkKT7KnJjvbKAIaB.jpg",
            "https://t3.ftcdn.net/jpg/00/71/63/34/240_F_71633411_20afo12ENX4SvYssbZZAQGjE6LlUWMOO.jpg",
            "https://t4.ftcdn.net/jpg/01/18/41/79/240_F_118417934_BYUeBM4c2TTFcbl9xkKT7KnJjvbKAIaB.jpg",
            "https://t4.ftcdn.net/jpg/01/18/41/79/240_F_118417934_BYUeBM4c2TTFcbl9xkKT7KnJjvbKAIaB.jpg"]
    urls = json.load(open("streamlit_imagegrid/test_files.json"))

if _RELEASE:
    _streamlit_imagegrid = components.declare_component(
        "streamlit_imagegrid",
        path=build_dir
    )
else:
    _streamlit_imagegrid = components.declare_component(
    "streamlit_imagegrid",
    url="http://localhost:3001"
)



def streamlit_imagegrid(urls=None,zoom=None,key=None,height=300):
    if urls== None:
        return None
    if zoom==None:
        zoom = 120
    if key==None:
        key=str(uuid.uuid4())[:3]
    return _streamlit_imagegrid(urls=urls,zoom=zoom,height=height,default=None,key=key)

#return_value = streamlit_imagegrid(key=3)

if _DEBUG:

    return_value = streamlit_imagegrid(urls=urls,key=2)
    if return_value:
        response = requests.get(return_value['src'])
        img = Image.open(BytesIO(response.content)).resize((100,100))

        st.sidebar.image(img)