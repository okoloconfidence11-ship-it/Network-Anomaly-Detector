from scapy.all import sniff, IP, TCP
import requests
import time

API_URL = "http://localhost:8000/predict"

def process_packet(packet):
    if packet.haslayer(IP) and packet.haslayer(TCP):
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        payload_size = len(packet[TCP].payload)

        features = [0.0] * 78
        features[4] = float(payload_size)

        try:
            response = requests.post(API_URL, json={"features": features}, timeout=1)
            result = response.json()

            status = result.get("status", "SAFE")
            prediction = result.get("prediction", "NORMAL")

            if status != "SAFE":
                print(f"🚨 [ALERT] {prediction} detected from {src_ip} -> {dst_ip} | Size: {payload_size}")
                print(f"💡 Remedy: {result.get('fix')}")
            else:
                print(f"🟢 [SECURE] Traffic Normal from {src_ip}")

        except Exception as e:
            print(f"❌ Connection error to AI Backend: {e}")

print("🛰️ Starting Live Data Ingestion... Press Ctrl+C to stop.")
sniff(filter="tcp", prn=process_packet, store=0)