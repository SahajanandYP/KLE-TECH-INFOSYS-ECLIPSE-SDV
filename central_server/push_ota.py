import sys
import json
import time
import urllib.request

try:
    import zenoh
    ZENOH_AVAILABLE = True
except ImportError:
    ZENOH_AVAILABLE = False

def push_ota(vehicle_id="virya-apm-01"):
    print(f"🌐 Initializing True Eclipse Zenoh Pub/Sub router...")
    
    if ZENOH_AVAILABLE:
        try:
            conf = zenoh.Config()
            session = zenoh.open(conf)
            topic = f"sdv/ota/trigger/{vehicle_id}"
            print(f"🚀 Broadcasting OTA command to topic: {topic}")
            payload = json.dumps({"target_version": "v2.0-Zenoh"}).encode('utf-8')
            session.put(topic, payload)
            time.sleep(0.5)
            session.close()
            print("✅ Broadcast sent to Zenoh cloud!")
        except Exception as e:
            print(f"Zenoh broadcast failed: {e}")
    else:
        print("Zenoh not available locally.")

    print("\\n📡 Attempting HTTP REST Fallback (in case corporate Wi-Fi blocks UDP Multicast)...")
    try:
        req = urllib.request.Request("http://localhost:8080/api/v1/vehicles")
        with urllib.request.urlopen(req, timeout=1.0) as res:
            data = json.loads(res.read().decode())
            target = next((v for v in data.get("vehicles", []) if v.get("vehicle_id") == vehicle_id), None)
            
            if target and target.get("network_endpoint"):
                endpoint = target["network_endpoint"]
                if "localhost" in endpoint or "0.0.0.0" in endpoint:
                    print(f"❌ Aborting HTTP fallback. Vehicle hasn't reported its true IP yet.")
                    return
                print(f"🚀 Discovered True IP: {endpoint}. Pushing OTA...")
                req_ota = urllib.request.Request(f"{endpoint}/api/ota/trigger", method="POST")
                req_ota.add_header('Content-Type', 'application/json')
                payload = json.dumps({"target_version": "v2.0-HTTP"}).encode('utf-8')
                urllib.request.urlopen(req_ota, data=payload, timeout=2.0)
                print("✅ HTTP Fallback Successful!")
    except Exception as e:
        print(f"❌ HTTP Fallback failed: {e}")

if __name__ == "__main__":
    vid = sys.argv[1] if len(sys.argv) > 1 else "virya-apm-01"
    push_ota(vid)
