import urllib.request
import json
import sys

def push_ota(vehicle_id="virya-apm-01"):
    print(f"📡 Requesting vehicle registry for {vehicle_id}...")
    try:
        # Get vehicle IP from local central server
        req = urllib.request.Request("http://localhost:8080/api/v1/vehicles")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        vehicles = data.get("vehicles", [])
        target = next((v for v in vehicles if v.get("vehicle_id") == vehicle_id), None)
        
        if not target:
            print(f"❌ Error: Vehicle '{vehicle_id}' not found in registry. Is it online?")
            return
            
        endpoint = target.get("network_endpoint")
        if not endpoint or "0.0.0.0" in endpoint or "localhost" in endpoint:
            # Fallback if vehicle didn't report its true Wi-Fi IP
            print(f"⚠️ Warning: Vehicle reported local endpoint '{endpoint}'.")
            print("Please enter the Skateboard's Wi-Fi IP address manually (e.g. 192.168.1.50):")
            ip = input("> ").strip()
            endpoint = f"http://{ip}:5000"
            
        print(f"🚀 Pushing OTA Command to {endpoint}...")
        
        ota_req = urllib.request.Request(f"{endpoint}/api/ota/trigger", method="POST")
        ota_req.add_header('Content-Type', 'application/json')
        payload = json.dumps({"target_version": "v2.0-OTA"}).encode('utf-8')
        
        with urllib.request.urlopen(ota_req, data=payload, timeout=5.0) as ota_res:
            res_data = json.loads(ota_res.read().decode())
            if res_data.get("success"):
                print("✅ OTA Push Successful! The vehicle dashboard is now prompting the driver.")
            else:
                print(f"❌ Vehicle rejected OTA: {res_data}")
                
    except Exception as e:
        print(f"❌ Failed to push OTA: {e}")

if __name__ == "__main__":
    vid = sys.argv[1] if len(sys.argv) > 1 else "virya-apm-01"
    push_ota(vid)
