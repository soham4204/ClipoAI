import asyncio
import json
import urllib.request
import urllib.error
import urllib.parse
from uuid import UUID

import httpx

base_url = 'http://localhost:8080/api'
login_data = urllib.parse.urlencode({
    'username': 'admin@clipo.ai',
    'password': 'admin123'
}).encode('ascii')

async def main():
    print('--- ClipoAI Backend Transcription Test ---')
    
    # 1. Login
    access_token = None
    try:
        req = urllib.request.Request(f'{base_url}/auth/login/access-token', data=login_data, method='POST')
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            access_token = data.get('access_token')
            print(f'[1] Auth Login: 200 OK -> Token generated')
    except Exception as e:
        print(f'[1] Auth Login Failed: {e}')
        return

    if not access_token:
        return

    # 2. Upload Video
    video_id = None
    print('[2] Uploading dummy video...')
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            with open('/tmp/dummy.mp4', 'rb') as f:
                files = {'file': ('dummy.mp4', f, 'video/mp4')}
                resp = await client.post(f"{base_url}/videos/upload", headers=headers, files=files)
                
            if resp.status_code == 200:
                video_data = resp.json()
                video_id = video_data.get('id')
                print(f"[2] Video Upload: 200 OK -> Video ID: {video_id}")
            else:
                print(f"[2] Video Upload Failed: {resp.status_code} {resp.text}")
                return
    except Exception as e:
        print(f'[2] Video Upload Exception: {e}')
        return

    # 3. Trigger Transcription
    print('[3] Triggering transcription...')
    try:
        req = urllib.request.Request(f'{base_url}/transcription/{video_id}', method='POST')
        req.add_header('Authorization', f'Bearer {access_token}')
        with urllib.request.urlopen(req) as response:
            job_data = json.loads(response.read())
            print(f'[3] Transcription Triggered: {response.getcode()} OK -> Job ID: {job_data.get("job_id")}')
    except Exception as e:
        print(f'[3] Transcription Trigger Failed: {e}')
        return
        
    print('[4] Waiting 10 seconds for background job to complete...')
    await asyncio.sleep(10)
    
    # Check job status via DB directly just to show it worked
    print('[5] Checking job status...')
    
if __name__ == '__main__':
    asyncio.run(main())
