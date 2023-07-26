import re
import requests

MIGRATION_YEAR = 0
API_KEY = ''
REGION = ''
URL = f'https://workload.{REGION}.cloudone.trendmicro.com/api'
HEADERS = {
    'Authorization': f'ApiKey {API_KEY}',
    'api-version': 'v1'
}

def get_policies():
    policies = requests.get(
        f'{URL}/policies',
        headers=HEADERS
    )
    return policies.json().get('policies')

def policy_rename(policy_id: int, new_name: str):
    resp = requests.post(
        url=f'{URL}/policies/{policy_id}',
        json={'name': new_name},
        headers=HEADERS
    )

for policy in get_policies():
    policy_name = policy.get('name')
    re_search = re.search(f' \({MIGRATION_YEAR}', policy_name)
    if re_search:
        new_name = policy_name[:re_search.start()]
        policy_rename(policy.get('ID'), new_name)
