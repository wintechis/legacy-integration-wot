from urllib.parse import quote_plus

import requests
import streamlit as st
from configs import settings


# Define functions for device and service discovery
def discover_devices():
    url = f"http://{settings.http_server.host}:{settings.http_server.port}/bluetooth_gatt/device_discovery"
    with st.spinner("Discovering devices..."):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                st.session_state["device_ids"] = response.json()["discovered_devices"]
                st.session_state["service_discovered"] = {}
            else:
                st.error("Failed to discover devices")
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {e}")


def discover_services(device_id):
    encoded_device_id = quote_plus(device_id)
    service_url = f"http://{settings.http_server.host}:{settings.http_server.port}/bluetooth_gatt/service_discovery/{encoded_device_id}"
    redirect_url = f"http://{settings.http_server.host}:{settings.http_server.port}/{encoded_device_id}"
    try:
        service_response = requests.get(service_url)
        if service_response.status_code == 200:
            redirect_response = requests.get(redirect_url)
            if redirect_response.status_code == 200:
                st.session_state["service_discovered"][
                    device_id
                ] = redirect_response.json()
        else:
            st.error("Failed to discover services for device")
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")


# Sidebar for navigation
st.sidebar.title("Navigation")
nav = st.sidebar.radio(
    "", ("Device Identification", "Service Discovery", "Thing Descriptions")
)

# Main page UI
st.title("Bluetooth Device Interaction")

if nav == "Device Identification":
    if "device_ids" not in st.session_state:
        st.session_state["device_ids"] = []
    if st.button("Device Identification with Bluetooth"):
        discover_devices()
    for device_id in st.session_state.get("device_ids", []):
        st.write(device_id)

elif nav == "Service Discovery":
    if "device_ids" in st.session_state:
        for device_id in st.session_state["device_ids"]:
            if st.button(f"Discover services for {device_id}"):
                discover_services(device_id)

elif nav == "Thing Descriptions":
    if "service_discovered" in st.session_state:
        for device_id, data in st.session_state["service_discovered"].items():
            if st.button(f"Show Thing Description for {device_id}"):
                st.json(data)

# If devices have been discovered, initialize 'service_discovered' dictionary
if "device_ids" in st.session_state and "service_discovered" not in st.session_state:
    st.session_state["service_discovered"] = {}
