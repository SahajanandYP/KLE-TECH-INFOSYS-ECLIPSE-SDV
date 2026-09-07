import sys
import json
import time

try:
    import zenoh
except ImportError:
    print("❌ Error: eclipse-zenoh not installed on Hub. Run: pip3 install eclipse-zenoh")
    sys.exit(1)

def push_ota(vehicle_id="virya-apm-01"):
    print(f"🌐 Initializing True Eclipse Zenoh Pub/Sub router...")
    
    # Open a Zenoh session which will automatically discover peers on the Wi-Fi LAN
    conf = zenoh.Config()
    session = zenoh.open(conf)
    
    topic = f"sdv/ota/trigger/{vehicle_id}"
    print(f"🚀 Broadcasting OTA command to topic: {topic}")
    print(f"📡 Waiting 2 seconds for Zenoh multicast auto-discovery...")
    time.sleep(2)
    
    payload = json.dumps({"target_version": "v2.0-Zenoh"}).encode('utf-8')
    session.put(topic, payload)
    
    print("✅ Broadcast sent to the Cloud queue!")
    print("If the vehicle is online anywhere on the LAN, it will instantly receive it.")
    print("(No IP address was needed!)")
    
    time.sleep(1) # Give it a second to send before closing
    session.close()

if __name__ == "__main__":
    vid = sys.argv[1] if len(sys.argv) > 1 else "virya-apm-01"
    push_ota(vid)
