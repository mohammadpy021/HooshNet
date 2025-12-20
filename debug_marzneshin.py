import sys
import os
import json
import logging

# Add current directory to path
sys.path.append(os.getcwd())

from professional_database import ProfessionalDatabase
from marzneshin_manager import MarzneshinPanelManager

# Setup logging
logging.basicConfig(level=logging.INFO)

def debug_marzneshin():
    try:
        db = ProfessionalDatabase()
        
        # Find Marzneshin panel
        query = "SELECT id, name, type, url FROM panels WHERE type = 'marzneshin' OR url LIKE '%vizitur.ir%'"
        panels = db.fetch_all(query)
        
        if not panels:
            print("❌ No Marzneshin panel found in database")
            return
            
        print(f"✅ Found {len(panels)} panels")
        for p in panels:
            print(f"   ID: {p['id']}, Name: {p['name']}, Type: {p['type']}, URL: {p['url']}")
            
        # Use the first one
        panel_id = panels[0]['id']
        print(f"🔍 Using Panel ID: {panel_id}")
        
        manager = MarzneshinPanelManager(panel_id=panel_id, db=db)
        
        if not manager.ensure_logged_in():
            print("❌ Failed to login")
            return
            
        print("✅ Login successful")
        
        # Target user
        username = "NBKX1026"
        
        print(f"🔍 Fetching user: {username}")
        response = manager.session.get(
            f"{manager.base_url}/api/users/{username}",
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"📄 User Data:\n{json.dumps(user_data, indent=2)}")
            
            # Check key
            key = user_data.get('key')
            print(f"🔑 Key found: {key}")
            
            # Check subscription_url
            sub_url = user_data.get('subscription_url')
            print(f"🔗 Subscription URL found: {sub_url}")
            
        else:
            print(f"❌ Failed to get user: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_marzneshin()
