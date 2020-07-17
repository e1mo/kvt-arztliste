from bs4 import BeautifulSoup as Bs
from pathlib import Path,PurePath
import json
import csv
import requests

def getOptionsFromSelect(id):
    r = requests.get('https://www.kv-thueringen.de/arztsuche')
    content = r.text
    soup = Bs(content,features='html.parser')
    rawAddDesignations = soup.find('select', id=id).find_all('option')
    rawAddDesignations = (x for x in rawAddDesignations if x.get('value') != '')

    addDesignations = {}
    for option in rawAddDesignations:
        # With some entries (detected at selFachgebiet > FA Radiologie)
        # there are two numbers within the value field
        # They are sperated by a ',', this looks like this: option value="44,86"
        # We split the value and itterate over it to remove that annoying ,
        addDesignations[int(option.get('value').split(',')[0])] = option.contents

    return dict(sorted(addDesignations.items(), key = lambda kv:kv[0]))
   
def getAdditionalDesignations():
    return getOptionsFromSelect('selzusatzbezeichnung')

def getServiceOffers():
    return getOptionsFromSelect('selGenehmigung')

def getSpecialContracts():
    return getOptionsFromSelect('selSelektivvertraege')

def writeToCSV(path,data,fieldnames=['num', 'title']):
    Path(PurePath(path).parent).mkdir(parents=True,exist_ok=True)

    with open (path, 'w', newline='') as f:
        fw = csv.writer(f)

        fw.writerow(['num', 'name'])
        for key,des in data.items():
            fw.writerow([key,des[0]])
       

if __name__ == '__main__':
    ids = ['selFachgebiet', 'selSchwerpunkt', 'selzusatzbezeichnung', 'selGenehmigung', 'selSelektivvertraege']

    for id in ids:
        print(id)
        writeToCSV('out/{}.csv'.format(id),getOptionsFromSelect(id))
