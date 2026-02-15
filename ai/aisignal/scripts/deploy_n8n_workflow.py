import requests
import os
import json
import sys

# Load environment variables (simulate loading from .env if needed, but we'll assume they are set in container)
N8N_HOST = os.getenv('N8N_API_HOST', 'http://n8n:5678') # Default to internal docker host
N8N_USER = os.getenv('N8N_USER', 'admin')
N8N_PASSWORD = os.getenv('N8N_PASSWORD', 'changeme_secure_password')

WORKFLOW_FILE = 'n8n/workflows/data_collection.json'

def get_workflow_json():
    with open(WORKFLOW_FILE, 'r') as f:
        return json.load(f)

def deploy_workflow():
    workflow_data = get_workflow_json()
    workflow_name = workflow_data.get('name')
    
    auth = (N8N_USER, N8N_PASSWORD)
    headers = {'Content-Type': 'application/json'}
    
    print(f"📡 Connecting to n8n at {N8N_HOST}...")
    
    # Check if workflow exists
    try:
        response = requests.get(f"{N8N_HOST}/api/v1/workflows", auth=auth)
        if response.status_code != 200:
            print(f"❌ Failed to list workflows: {response.text}")
            return False
            
        workflows = response.json().get('data', [])
        existing_workflow = next((w for w in workflows if w['name'] == workflow_name), None)
        
        if existing_workflow:
            workflow_id = existing_workflow['id']
            print(f"🔄 Updating existing workflow: {workflow_name} ({workflow_id})")
            
            # Update workflow
            update_url = f"{N8N_HOST}/api/v1/workflows/{workflow_id}"
            resp = requests.put(update_url, json=workflow_data, auth=auth, headers=headers)
            if resp.status_code == 200:
                print("✅ Update successful")
            else:
                print(f"❌ Update failed: {resp.text}")
                return False
                
            # Activate workflow
            activate_url = f"{N8N_HOST}/api/v1/workflows/{workflow_id}/activate"
            resp = requests.post(activate_url, auth=auth, headers=headers)
            if resp.status_code == 200:
                print("✅ Activation successful")
            else:
                print(f"⚠️ Activation warning: {resp.text}")

        else:
            print(f"➕ Creating new workflow: {workflow_name}")
            create_url = f"{N8N_HOST}/api/v1/workflows"
            resp = requests.post(create_url, json=workflow_data, auth=auth, headers=headers)
            if resp.status_code == 200:
                new_id = resp.json()['data']['id']
                print(f"✅ Creation successful (ID: {new_id})")
                
                # Activate
                activate_url = f"{N8N_HOST}/api/v1/workflows/{new_id}/activate"
                requests.post(activate_url, auth=auth, headers=headers)
                print("✅ Activation successful")
            else:
                print(f"❌ Creation failed: {resp.text}")
                return False
                
        return True

    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    if deploy_workflow():
        sys.exit(0)
    else:
        sys.exit(1)
