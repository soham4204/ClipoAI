import urllib.request
import urllib.parse
import json

base_url = 'http://localhost:8080/api'
print('--- ClipoAI Backend E2E Test ---')

# 1. Health Check
try:
    with urllib.request.urlopen(f'{base_url}/health') as response:
        print(f'[1] Health Check: {response.getcode()} OK -> {json.loads(response.read())}')
except Exception as e:
    print(f'[1] Health Check Failed: {e}')

# 2. Login (JWT)
access_token = None
try:
    data = urllib.parse.urlencode({'username': 'admin@clipo.ai', 'password': 'admin123'}).encode('utf-8')
    req = urllib.request.Request(f'{base_url}/auth/login/access-token', data=data)
    with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read())
        access_token = res_data.get('access_token')
        print(f'[2] Auth Login: {response.getcode()} OK -> Token generated (Length: {len(access_token)})')
except Exception as e:
    print(f'[2] Auth Login Failed: {e}')

# 3. Test Video Listing
if access_token:
    try:
        print('[3] Testing Video Listing...')
        req = urllib.request.Request(f'{base_url}/videos')
        req.add_header('Authorization', f'Bearer {access_token}')
        with urllib.request.urlopen(req) as response:
            videos = json.loads(response.read())
            print(f'[3] Video Listing: {response.getcode()} OK -> Found {len(videos)} videos')
            if videos:
                print(f'    First video: {videos[0].get("title")}')
    except Exception as e:
        print(f'[3] Video Listing Failed: {e}')
else:
    print('[3] Skipping Video test due to Login Failure.')
