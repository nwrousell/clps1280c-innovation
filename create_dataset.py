import requests
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import threading

endpoint = "https://api.openalex.org/works"

earliest_date = "1980-01-01"
latest_date = "2020-01-01"


def get_random_works(num_works=20, field_id=17):
    filter_string = f"filter=from_publication_date:{earliest_date},to_publication_date:{latest_date},has_oa_accepted_or_published_version:true,type:article,language:en,primary_topic.field.id:{field_id}"
    select_string = f"select=id,display_name,publication_year,authorships,countries_distinct_count,institutions_distinct_count,cited_by_count"
    page = 1
    items = []
    while len(items) < num_works:
        endpoint = f"https://api.openalex.org/works?sample={num_works}&per-page=200&page={page}&seed=123&{filter_string}&{select_string}"
        response = requests.get(endpoint)
        data = response.json()
        items.extend(data['results'])
        print(f"Fetched {len(items)} papers")
        page += 1
    return items


# for author, get list of past works before specific date
# create unique list of total Domains, fields, and subfields
def get_author_experience(author_id, date):
    select_string = "select=topics"
    endpoint = f"https://api.openalex.org/authors/{author_id}?{select_string}"

    res = requests.get(endpoint)
    data = res.json()
    author_topics = data["topics"]
    
    topics, domains, fields, subfields = [], [], [], []
    for t in author_topics:
        topics.append(t["display_name"])
        domains.append(t["domain"]["display_name"])
        subfields.append(t["subfield"]["display_name"])
        fields.append(t["field"]["display_name"])
    topics = list(set(topics))
    domains = list(set(domains))
    fields = list(set(fields))
    subfields = list(set(subfields))
    
    return topics, domains, fields, subfields

def process_papers(batches_ref, paper_data):
    papers = {
        "title": [],
        "countries_distinct_count": [],
        "institutions_distinct_count": [],
        "cited_by_count": [],
        "publication_year": [],
        "id": [],
        "num_authors": [],
        "total_author_domain_count": [],
        "mean_author_domain_count": [],
        "max_author_domain_count": [],
        "total_author_field_count": [],
        "mean_author_field_count": [],
        "max_author_field_count": [],
        "total_author_subfield_count": [],
        "mean_author_subfield_count": [],
        "max_author_subfield_count": [],
    }
    for i, p_data in enumerate(paper_data):
    
        # print(p_data["authorships"])
        author_ids = [author["author"]["id"].split("/")[-1] for author in p_data["authorships"]]
    
        total_topics = []
        total_domains = []
        total_fields = []
        total_subfields = []
    
        topic_counts = []
        domain_counts = []
        field_counts = []
        subfield_counts = []
        for author_id in author_ids:
            topics, domains, fields, subfields = get_author_experience(author_id, str(p_data["publication_year"])+"-01-01")
            total_topics.extend(topics)
            total_domains.extend(domains)
            total_fields.extend(fields)
            total_subfields.extend(subfields)
            topic_counts.append(len(topics))
            domain_counts.append(len(domains))
            field_counts.append(len(fields))
            subfield_counts.append(len(subfields))
    
        total_topics = list(set(total_topics))
        total_domains = list(set(total_domains))
        total_fields = list(set(total_fields))
        total_subfields = list(set(total_subfields))
        
        num_authors = len(author_ids)
        
        total_author_domain_count = len(total_domains)
        mean_author_domain_count = 0 if total_author_domain_count == 0 else np.mean(domain_counts)
        max_author_domain_count = 0 if total_author_domain_count == 0 else np.max(domain_counts)
        
        total_author_field_count = len(total_fields)
        mean_author_field_count = 0 if total_author_field_count == 0 else np.mean(field_counts)
        max_author_field_count = 0 if total_author_field_count == 0 else np.max(field_counts)
        
        total_author_subfield_count = len(total_subfields)
        mean_author_subfield_count = 0 if total_author_subfield_count == 0 else np.mean(subfield_counts)
        max_author_subfield_count = 0 if total_author_subfield_count == 0 else np.max(subfield_counts)
        
    
        papers["title"].append(p_data["display_name"])
        papers["countries_distinct_count"].append(p_data["countries_distinct_count"])
        papers["institutions_distinct_count"].append(p_data["institutions_distinct_count"])
        papers["cited_by_count"].append(p_data["cited_by_count"])
        papers["publication_year"].append(p_data["publication_year"])
        papers["id"].append(p_data["id"])
        papers["num_authors"].append(num_authors)
        papers["total_author_domain_count"].append(total_author_domain_count)
        papers["mean_author_domain_count"].append(mean_author_domain_count)
        papers["max_author_domain_count"].append(max_author_domain_count)
        papers["total_author_field_count"].append(total_author_field_count)
        papers["mean_author_field_count"].append(mean_author_field_count)
        papers["max_author_field_count"].append(max_author_field_count)
        papers["total_author_subfield_count"].append(total_author_subfield_count)
        papers["mean_author_subfield_count"].append(mean_author_subfield_count)
        papers["max_author_subfield_count"].append(max_author_subfield_count)

        if i % 10 == 0:
            print(f"[{threading.current_thread().name}] processed {i}/{len(paper_data)} papers")
    
    df = pd.DataFrame(papers)
    batches_ref.append(df)

def create_dataset(num=20):
    paper_data = get_random_works(num)

    n_threads = 10
    threads = []
    batches = []
    batch_size = len(paper_data) // n_threads
    start = 0
    for i in range(n_threads):
        threads.append(threading.Thread(target=process_papers, args=(batches, paper_data[start:start+batch_size]), name=f"Thread {i}"))
        start += batch_size

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
        
    master_df = pd.concat(batches, axis=0)
    return master_df


df = create_dataset(10000)
df.to_csv("data/papers10k.csv")