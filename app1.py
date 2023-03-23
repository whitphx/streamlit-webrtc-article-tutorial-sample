#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 12:38:03 2023

@author: sirishalanka
"""
import streamlit as st
import av
import cv2
from streamlit_webrtc import webrtc_streamer

st.title("my first streamlit app")
st.write("hellow,world")

threshold1 = st.slider("threshold", min_value =0, max_value=1000,step=1,value=100)
threshold2 = st.slider("Threshold2", min_value=0, max_value=1000, step=1, value=200)

def callback(frame):
    img = frame.to_ndarray(format="bgr24")

    img = cv2.cvtColor(cv2.Canny(img, threshold1, threshold2), cv2.COLOR_GRAY2BGR)

    return av.VideoFrame.from_ndarray(img, format="bgr24")



webrtc_streamer(key="example",video_frame_callback=callback, rtc_configuration={  # Add this line
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    }
    )
