import json
import requests

"""
Function for executing a query using the GoTriple API.
Takes as parameters the language of the articles we want as output and the query term.
Returns the data in Json format if the request was successful (by default, it searches for 250 documents), 
None (and print an error message otherwise)
It could be improved using other parameters, for example Year (which is not useful for our purposes).
"""

def query_api(language, query_term, size=10):
    
    url = 'https://api.gotriple.eu/documents'
    params = {
        'q': query_term,
        'include_duplicates': 'false',
        'fq': 'in_language={}'.format(language),  # Filtra per documenti in francese
        'size': 250
    }

    headers = {
        'accept': 'application/json'
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f'Error: {response.status_code}')
        return None
    
"""
Below is a function get_sample that can be used to obtain a sample of data (triples title-abstract-keywords) using the GoTriple API. Parameters of the function are:

- languages. Accepts as values a list of languages (supported languages are 'es', 'en', 'pt', 'fr', 'de', 'ru', 'ca', 'it', 'nl', 'el', 'hr'). Specifies languages of keywords in multi-language sample. The sample returned by the function returns an equal number of keywords for each language in the list. 
- sample_size. Specifies size of the sample (where the size is the number of keywords). Using a limited number of keywords (approximately) is recommended , 
otherwise the execution could be slow (or get stuck if there are not enough data, this is especially the case with underresourced languages)

The function produces a list of Python dictionaries with the following data:
'Language' (the language of the keywords), 'Title_eng' (the English title of the article), 'Title_or' (the title of the article in the original language, the value of 'in_language') 
'Id' (the ID of the article), 'Abstract_eng' (the English version of the abstract), 'Abstract_or' (the abstract of the article in the original language) 'keywords' (a list of keywords)
If one of the values is not present among data returned by the API (for example, there is no English title for an article), None value is
returned
"""

def get_sample(languages, sample_size):
    total_items = []
    #  load the Json file with a list of query terms in different languages, useful to make queries
    with open("C:/Users/paolo/Desktop/query_terms.json", "r") as file:  #  change path
        query_terms = json.load(file)
    keywords_per_language = sample_size / len(languages)  #  determines the number of keywords per language in the final sample
    
    #  for each language, looks for keywords by making consecutive queries until it reaches the number of necessary keywords
    for language in languages:
        items = []
        query_terms_it = iter(query_terms)
        keywords_count = 0
        while (keywords_count < keywords_per_language):
            next_query_term = next(query_terms_it)
            data = query_api(language, next_query_term[language])
            try:
                try_item = data[0]
            except:
                print("Error in API query")
            else:
                for document in data:
                    keywords_original_language = [kw['text'] for kw in document["keywords"] if kw["lang"] == language]
                    if len(keywords_original_language) > 0:
                        item = {}
                        item['Language'] = language
                        item['Id'] = document["id"]
                        item['Keywords'] = []
                        item['Title_eng'] = None
                        item['Title_or'] = None
                        item['Abstract_eng'] = None
                        item['Abstract_or'] = None
                        for headline in document["headline"]:
                            if headline["lang"] == "en":
                                item['Title_eng'] = headline["text"]
                            if headline["lang"] == language:
                                item['Title_or'] = headline["text"]
                        for abstract in document["abstract"]:
                            if abstract["lang"] == "en":
                                item['Abstract_eng'] = abstract["text"]
                            if abstract["lang"] == language:
                                item['Abstract_or'] = abstract["text"]
                        item['Keywords'] = keywords_original_language
                        keywords_count += len(keywords_original_language)
                        items.append(item)


        #  further iteration to ensure the number of keywords in the final sample is equal to sample size
        items_iter = iter(items)
        items = []
        keywords_count = 0
        while (keywords_count < keywords_per_language):
            next_item = next(items_iter)
            items.append(next_item)
            keywords_count += len(next_item['Keywords'])
        total_items.extend(items)

    return total_items