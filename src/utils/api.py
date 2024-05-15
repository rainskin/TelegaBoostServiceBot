import config
import requests

API_TOKEN = config.API_TOKEN
BASE_URL = config.BASE_URL


def get_services():
    method = 'services'
    url = f'{BASE_URL}{method}&key={API_TOKEN}'
    response = requests.get(url)
    services = response.json()

    categories = []
    for i in services:
        category = i['category']
        if category not in categories:
            categories.append(category)

    return categories

def get_tariffs(category_name):
    method = 'services'
    url = f'{BASE_URL}{method}&key={API_TOKEN}'
    response = requests.get(url)
    services = response.json()

    tariffs = []
    for service in services:
        if service['category'] == category_name:
            tariffs.append(service)

    return tariffs


def get_plan(_id: int):
    method = 'services'
    url = f'{BASE_URL}{method}&key={API_TOKEN}'
    response = requests.get(url)
    services = response.json()

    for service in services:
        service_id = service['service']
        if service_id == _id:
            return service


