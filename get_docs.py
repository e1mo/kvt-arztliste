from bs4 import BeautifulSoup
from pathlib import Path,PurePath
import json
import csv
import requests

def getDoctors(params = {}):
    pages = -1
    page = 0
    doctors = []

    while page < pages or pages == -1:
        page += 1
        print('Querying page {}/{}... '.format(page,pages), end='')
        html = callSearchService({**{'page': page},**params}) 
        soup = BeautifulSoup(html, features='html.parser')
        if pages < 0:
            pages = getPageCount(soup)

        newdocs = extractDoctors(soup)
        doctors.extend(newdocs)
        print('{} doctors added. {} total'.format(len(newdocs), len(doctors)))

    return doctors

def getPageCount(soup: BeautifulSoup):
    maxPage = 0
    pages = soup.find(
        'form',
        class_="pagination"
    )

    if pages is None:
        return 1

    pages = pages.find_all(
        'input',
        class_="pagination-button",
        attrs={'type':'submit'}
    )

    return len(pages)
        
def extractDoctors(soup: BeautifulSoup):
    doctors = []

    rawDoctors = soup.find(
        'ul', class_='results'
    ).find_all('li')

    for doctor in rawDoctors:
        doc = {}
        a = doctor.find('a')
        p = a.find('p')
        p_strs = [pstr for pstr in p.stripped_strings]

        doc['name'] = a.find('h3').string.strip()
        doc['establishment'] = p_strs[0]
        doc['field'] = p_strs[1]
        doc['address'] = p_strs[2]
        doc['url'] = 'https://www.kv-thueringen.de{}'.format(a.get('href'))

        doc = extendDoctor(doc)
        doctors.append(doc)

    return doctors

def extendDoctor(doc: dict):
    listCounter = 0
    headpos = 0

    infoFieldMap = {
        'Schwerpunkt:':         'focus',
        'Zusatzbezeichung:':    'additionalDesignation',
        'Leistungsangebote:':   'serviceRange',
        'Sonderverträge:':      'specialContracts'
    }
    headMap = {
        'Telefon': 'telephone',
        'Einrichtung': None,
        'Weitere Ärzte': 'otherDocs',
        'Wegbeschreibung': None
    }

    r = requests.get(doc['url'])
    soup = BeautifulSoup(r.text, features='html.parser')
    res = soup.find('div', class_='resultdetail')
    lists = res.find_all('ul')
    headings = res.find_all('h3')
    infoFields = res.find_all(string=['Schwerpunkt:', 'Zusatzbezeichung:', 'Leistungsangebote:', 'Sonderverträge:'])

    for field in infoFields:
        if field not in infoFieldMap:
            continue

        key = infoFieldMap[field]
        doc[key] = []
        for li in lists[listCounter].find_all('li'):
            doc[key].append(li.string)

        listCounter += 1

    ps = res.find_all('p')
    del ps[0:1+len(infoFields)] # Strip the headings we've already dealt with
    if "Sprechzeiten" in headings[0]:
        del headings[:1]

    for head in [head.string for head in headings]:
        if head not in  headMap:
            continue

        key = headMap[head]

        if key is None:
            headpos += 1
            continue

        val = ps[headpos].text.strip()
        doc[key] = val

        headpos += 1

    return doc

    
def callSearchService(params, url='https://www.kv-thueringen.de/arztsuche'):
    data = {}
    defaultParams = {
        'search': '',
        'place': '',
        'radius': '',
        'typeFachgebiet': '',
        'typeSchwerpunkt': '',
        'typeZusatzbezeichnung': '',
        'typeGenehmigung': '',
        'typeSelektivvertraege': '',
        'filter': 1,
        '__referrer][@action': 'list'
    }
    params = {**defaultParams, **params}
    for key,val in params.items():
        data['tx_t3kvclient_showclient[{}]'.format(key)] = val

    return requests.post(url,data).text

if __name__ == '__main__':
    #doctors = getDoctors({'search': 'Tondt'})
    doctors = getDoctors({'search': 'Öhring'})
    with open('out/doctors.json', 'w') as fp:
        json.dump(doctors, fp)
