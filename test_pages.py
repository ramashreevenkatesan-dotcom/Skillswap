"""Test script to check teach page for errors"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

with app.test_client() as c:
    # Get login page to get CSRF token
    resp = c.get('/login')
    html = resp.data.decode()
    
    import re
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    token = match.group(1) if match else ''
    print(f"CSRF Token found: {bool(token)}")
    
    # Login as alex_morgan
    resp2 = c.post('/login', data={
        'email': 'alex.morgan@campus.edu', 
        'password': 'Password123!', 
        'csrf_token': token
    }, follow_redirects=True)
    print(f"Login page status: {resp2.status_code}")
    
    # Test each protected page
    pages = ['/dashboard', '/teach', '/skill-exchange', '/requests', '/profile', '/settings']
    
    for page in pages:
        try:
            resp = c.get(page, follow_redirects=True)
            data = resp.data.decode('utf-8', errors='ignore')
            has_error = 'Traceback' in data or 'Internal Server Error' in data or resp.status_code >= 500
            if has_error:
                print(f"\n{'='*60}")
                print(f"ERROR on {page} (status {resp.status_code}):")
                # Find traceback
                idx = data.find('Traceback')
                if idx >= 0:
                    print(data[idx:idx+2000])
                else:
                    idx = data.find('Internal Server Error')
                    print(data[max(0,idx-500):idx+500])
                print(f"{'='*60}")
            else:
                print(f"{page} -> OK ({resp.status_code})")
        except Exception as e:
            print(f"{page} -> EXCEPTION: {e}")
    
    print("\nDone testing all protected pages!")
