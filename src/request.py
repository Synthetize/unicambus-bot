import datetime
import requests as req
from bs4 import BeautifulSoup
from datetime import datetime
import time
import json

url = 'https://marcheroma.contram.it/home/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
    'Referer': 'https://marcheroma.contram.it/home/MostraAcquisto',
    'Origin': 'https://marcheroma.contram.it',
}

def require_valid_id(stop_id):
    with open('data/stops.json', 'r') as f:
        stops = json.load(f)
        for stop in stops:
            if stop['id'] == id:
                return
    raise Exception(f'Invalid stop id {stop_id}')


def book_ticket(start_id, destination_id, date, email, name, surname, phone):
    #require_valid_id(start_id)
    #require_valid_id(destination_id)

    s = req.session()
    s.headers = headers

    #formatted_date = datetime.strptime(date, '%Y-%m-%d')

    research = (url + f'Ricerca?PartenzaID={start_id}&DestinazioneID={destination_id}&DataPartenza=2025-03-19'
                      f'&NumeroAdulti=0&NumeroStudenti=1')
    print(research)

    res = s.get(research)

    if res.status_code != 200:
        raise Exception('Failed research')

    soup = BeautifulSoup(res.text, 'html.parser')
    div = soup.find('div', {'id': 'viaggi'})
    form = div.find('form', {'action': 'Prenota'})

    if not form:
        raise Exception('No tickets available')

    data = {}
    for tag in form.find_all('input', {'type': 'hidden'}):
        data[tag['name']] = tag.get('value')

    res = s.post(url + 'Prenota', data=data)

    if not res.history:
        raise Exception('Failed to book a ticket')

    res = s.get(url + 'RitornaCarrello')

    soup = BeautifulSoup(res.text, 'html.parser')

    form = soup.find('form', {'action': '/home/RitornaCarrello'})

    data = {}
    for tag in form.find_all('input', {'type': 'hidden'}):
        data[tag['name']] = tag.get('value')

    data['EmailAcquirente'] = email
    data['Nominativi[0].' + 'nome'] = name
    data['Nominativi[0].' + 'cognome'] = surname
    data['Nominativi[0].' + 'email'] = email
    data['Nominativi[0].' + 'telefono'] = phone

    res = s.post(url + 'RitornaCarrello', data=data)

    if not res.history:
        raise Exception('Failed to book')

    soup = BeautifulSoup(res.text, 'html.parser')

    form = soup.find('form', {'id': 'form-pagamento'})

    data = {}
    for tag in form.find_all('input', {'type': 'hidden'}):
        data[tag['name']] = tag.get('value')

    time.sleep(2)

    res = s.post(url + 'ConfermaPagamentoBraintree', data=data)

    print(res.status_code)


refund_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
    'Referer': 'https://marcheroma.contram.it/home/RimborsoClienti',
    'Origin': 'https://marcheroma.contram.it',
}

expected_errors = [
    "Non è stato trovato alcun biglietto da rimborsare.",
    "L'e-mail inserita non è corretta."
]

async def refund_ticket(ticket_id: int, email: str) -> bool:
    s = req.session()
    s.headers = refund_headers

    res = s.post(url + f'RimborsoClienti?CodTitolo={ticket_id}&EmailAcquisto={email}&CodTitolo=&EmailAcquisto=')

    soup = BeautifulSoup(res.text, 'html.parser')
    error_divs = soup.find_all('div', {'class': 'text-danger'})

    if error_divs.__len__() != 0:
        return False
    return True

