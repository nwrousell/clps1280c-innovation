import requests
from urllib.parse import quote
import json

# Scopus: https://dev.elsevier.com/sc_apis.html
# SciVal: https://dev.elsevier.com/scival_apis.html

# getting started guide: https://dev.elsevier.com/guides/Scopus%20API%20Guide_V1_20230907.pdf

API_KEY = "8347b6813c165486b46955f733adc441"

# endpoint = f"http://api.elsevier.com/content/abstract/doi/10.1016/S0014-5793(01)03313-0?apiKey={API_KEY}"

def dump(data, fname):
    with open(fname, "w") as json_file:
        json.dump(data, json_file)

def retrieve_abstract():
    endpoint = f"http://api.elsevier.com/content/abstract/doi/10.1016/S0014-5793(01)03313-0?apiKey={API_KEY}"
    response = requests.get(endpoint)
    return response

def extract_relevant_fields(document):
    doc = {
        "title": document["dc:title"],
        "identifier": document["dc:identifier"],
        "url": document["prism:url"],
        "num_citations": document["citedby-count"],
        "date": document["prism:coverDate"],
        "doi": document["prism:doi"],
        "links": {
            "author-affiliation": document["link"][1]["@href"]
        }
    }
    affiliations = []
    for affiliation in document["affiliation"]:
        affiliations.append({
            "country": affiliation["affiliation-country"],
            "city": affiliation["affiliation-city"],
            "name": affiliation["affilname"]
        })

    doc["affiliations"] = affiliations
    return doc

def api(link):
    headers = {'X-ELS-APIKey': API_KEY}
    response = requests.get(link, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f'Error: {response.status_code}, {response.text}')

def sample(count: int, field: str):
    # field = quote(f'TITLE-ABS-KEY("{field}")')
    query = quote(f'SUBJAREA({field}) AND DOCTYPE(ar) AND PUBYEAR > 2000 AND PUBYEAR < 2020')
    endpoint = f"https://api.elsevier.com/content/search/scopus?query={query}&count=${count}&sample=random"
    
    data = api(endpoint)
    documents = []
    for result in data['search-results']['entry']:
        # print(result['dc:title'])
        documents.append(extract_relevant_fields(result))
    dump(documents, "./data/documents.json")

if __name__ == "__main__":
    field = 'COMP'
    count = 1000
    sample(count, field)