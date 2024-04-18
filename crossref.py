import requests
import json

def dump(data, fname):
    with open(fname, "w") as json_file:
        json.dump(data, json_file)

num = 10000

# category_name = "Artificial Intelligence"
# https://service.elsevier.com/app/answers/detail/a_id/15181/supporthub/scopus/related/1/
category_name = "Experimental and Cognitive Psychology"

# URL for the Crossref API to get random DOIs
# url = f'https://api.crossref.org/works?sample={100}&filter=type:journal-article,from-pub-date:2000,until-pub-date:2020,has-affiliation:true,has-license:true,category-name:{category_name}'

def get_random_articles(num_articles):
    items = []
    cursor = '*'
    while len(items) < num_articles:
        # URL for the Crossref API to get random DOIs
        url = f'https://api.crossref.org/works?rows=100&cursor={cursor}&filter=type:journal-article,from-pub-date:2000,until-pub-date:2020,has-affiliation:true,has-license:true,category-name:{category_name}'

        # Make a GET request to the API
        response = requests.get(url)

        # Parse the response JSON
        data = response.json()['message']
        new_items = data['items']
        # new_dois = [item['DOI'] for item in items]

        # Add new DOIs to the dois list
        # dois.extend(new_dois)
        items.extend(new_items)

        # Update the cursor for the next request
        cursor = data['next-cursor']

        # Break the loop if there are no more results
        if not cursor:
            break

    # return dois[:num_articles]
    return items[:num_articles]


articles = []

items = get_random_articles(num)
for i, data in enumerate(items):
    # URL for the Crossref API to get metadata for a specific DOI
    # url = f'https://api.crossref.org/works/{doi}'

    # Make a GET request to the API
    # response = requests.get(url)

    # Parse the response JSON
    # data = response.json()['message']

    # Extract metadata, including author information
    title = data['title'][0] if 'title' in data else 'N/A'
    author_data = data['author'] if 'author' in data else []
    published_date = data['published']['date-parts'][0] if 'published' in data else 'N/A'
    if len(published_date) < 2:
        published_date = ["N/A", "N/A"]
    # if published_date != "N/A":
    #     published_date = f"{published_date[1]}-{published_date[0]}"

    affiliations = []
    author_count = 0
    for author in author_data:
        affiliations.append([a["name"] for a in author["affiliation"]])
        author_count += 1
        
    articles.append({
        "title": title,
        "affiliations": affiliations,
        "author_count": author_count,
        # "date": published_date,
        "year": published_date[0],
        "month": published_date[1],
        "subject": data["subject"] if 'subject' in data else [],
        "num_citations": data["is-referenced-by-count"]
    })
    print(f"finished doi #{str(i)}")


dump(articles, "./data/articles10k.json")