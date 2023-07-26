import json
import requests
import time

API_KEY =  ''
BASE_URL = ''
ORG_KEY = ''
FILE_PATH = 'c:\\temp\\trend_activation.ps1'

HEADERS = {
    'X-AUTH-TOKEN': API_KEY
}

def search_devices(os_type: list = ['WINDOWS']):
    url = f'{BASE_URL}/appservices/v6/orgs/{ORG_KEY}/devices/_search'
    payload = {'criteria': {'os': os_type}}
    resp = requests.post(url, data=payload, headers=HEADERS)

    return resp

class DeviceSession:
    def __init__(self, device_id: int) -> None:
        self.device_id = device_id
        self.session_id = self.start_device_session()

    def start_device_session(self):
        url = f'{BASE_URL}/appservices/v6/orgs/{ORG_KEY}/liveresponse/sessions'
        payload = {'device_id': self.device_id}
        resp = requests.post(url, json=payload, headers=HEADERS)

        if resp:
            return resp.json().get('id')

    def get_device_info(self):
        resp = requests.get(
            f'{BASE_URL}/appservices/v6/orgs/{ORG_KEY}/devices/{self.device_id}',
            headers=HEADERS
        )

        return resp.json()

    def file_upload(self):
        headers = HEADERS
        file = {'file': open(FILE_PATH, 'rb')}
        url = f'{BASE_URL}/appservices/v6/orgs/{ORG_KEY}/liveresponse/sessions/{self.session_id}/files'
        resp = requests.post(
            url,
            files=file,
            headers=headers
        )

        return resp.json().get('id')

    def put_file(self, file_id: str):
        path = 'c:\\temp\\trend_install.ps1'
        payload = {
            'name': 'put file',
            'path': path,
            'file_id': file_id
        }
        url = f'{BASE_URL}/appservices/v6/orgs/{ORG_KEY}/liveresponse/sessions/{self.session_id}/commands'
        resp = requests.post(url, json=payload, headers=HEADERS)

        return resp.json()

    def create_process(self, output_file: str = 'c:\\temp\trend_install.log'):
        path = 'c:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe -ExecutionPolicy Bypass -File c:\\temp\\trend_install.ps1'
        url = f'{BASE_URL}/appservices/v6/orgs/{ORG_KEY}/liveresponse/sessions/{self.session_id}/commands'
        payload = {
            'name': 'create process',
            'path': path,
            'output_file': output_file
        }

        resp = requests.post(url, json=payload, headers=HEADERS)

        return resp.json()

    def check_cmd_status(self, cmd_id: str):
        url = f'{BASE_URL}/appservices/v6/orgs/{ORG_KEY}/liveresponse/sessions/{self.session_id}/commands/{cmd_id}'
        resp = requests.get(url, headers=HEADERS).json()

        return resp.get('status')

#Write local a CSV of machine ad cmd_id, for checking later for issues, also write local log file of output.
def main(device_ids: list):
    for device in device_ids:
        try:
            device_session = DeviceSession(device)
            if not device_session:
                print(f'failed to get session for device: {device}')
                continue
            file_id = device_session.file_upload()
            put_file = json.loads(device_session.put_file(file_id))
            status = put_file.get('status')
            time.sleep(2)
            if status == 'COMPLETE':
                device_session.create_process()
                print(f'Installation has started on device: {device}')
        except Exception as error:
            print(error)
