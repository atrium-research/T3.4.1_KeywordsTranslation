import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from difflib import SequenceMatcher
from openai import OpenAI
from groq import Groq



"""The following function sends an HTTP request to the DBPediaSpotlight API. 
It takes as parameters the text of the query (the text to annotate), the language of the input text
and the confidence score (default=0.5)
It returns None (and prints error) if the query has no success, otherwise it returns the response in JSON format (the response
contains links to the DBPedia version correspondent to the language) """


def queryAPIDBpediaSpotlight(text, lang, confidence=0.5):
    url = 'https://api.dbpedia-spotlight.org/{}/annotate'.format(lang)
    headers = {'Accept': 'application/json'}
    params = {
        'text': text,
        'confidence': 0.5  
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Errore: {response.status_code}')
        return None

    

"""The following function is used to map DBPedia URIs to Wikidata ones.
It takes as input the DBPedia URI and returns the Wikidata one (more precisely, it returns a list
with all the correspondent candidates). 
It uses a Python SPARQL wrapper to execute a SPARQL query in Python, using the property owl:sameAs  """

def get_wikidata_uri(dbpedia_uri):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query = f"""
    PREFIX owl: <http://www.w3.org/2002/07/owl#>

    SELECT ?wikidataURI
    WHERE {{
      <{dbpedia_uri}> owl:sameAs ?wikidataURI .
      FILTER (STRSTARTS(STR(?wikidataURI), "http://www.wikidata.org/entity/"))
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    wikidata_uris = [result["wikidataURI"]["value"] for result in results["results"]["bindings"]]
    return wikidata_uris

"""
The following function load a LLM from the HuggingFace Hub using the Python wrapper for Llama.cpp.
The function takes as input repo_id (the name of the HuggingFace repository of the model) 
and the name of the model file (typically for each repository there are different versions of the model, 
where each version corresponds to a quantization using a different number of bits to encode weights). 
Different models can be tried by looking for quantized models in gguf format in Huggingface. 
By default, the function uses a 4-bit version of a Mistral-7B-Instruct quantization.
The function returns the model object
"""

def loadLLM(repo_id="TheBloke/Mistral-7B-Instruct-v0.2-GGUF", filename='mistral-7b-instruct-v0.2.Q4_K_M.gguf'):
    llm = Llama.from_pretrained(
    repo_id,
    filename,
    verbose=False
    )
    return llm

"""The following function makes a query on Wikidata using the Wikidata API.
It takes as input the term to be queried
and returns (EXPLAIN HERE THE RETURNED VALUE IN DETAIL)"""
def query_wikidata(query_term):
    WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
    params = {
        'action': 'wbsearchentities',
        'search': query_term,
        'language': 'en',
        'format': 'json'
    }
    response = requests.get(WIKIDATA_API_URL, params=params)
    
    response = response.json().get('search', [])

    best_match = None
    highest_score = 0
    for result in response:
        score = SequenceMatcher(None, query_term, result['label']).ratio()
        if score > highest_score:
            highest_score = score
            best_match = result
    return best_match


"""The following function makes a query on Wikidata using the API, 
sort the results by a sequence matching score and returns the best matches
Results are in the form of a list of dictionaries, where each dictionary contains the following keys:
- label: the label of the entity
- uri: the URI of the entity
- description: the description of the entity
- score: the sequence matching score

"""
def query_best_matches_wikidata(query_term, language = "en", number_of_results=3):
    WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
    params = {
        'action': 'wbsearchentities',
        'search': query_term,
        'language': language,
        'format': 'json'
    }
    response = requests.get(WIKIDATA_API_URL, params=params)
    
    response = response.json().get('search', [])


    best_match = None
    highest_score = 0
    results_with_scores = []
    for entity in response:
        result = {}
        result['label'] = entity['label']
        result['uri'] = entity['concepturi']
        if 'description' in entity:
            result['description'] = entity['description']
        else:
            result['description'] = ""
        result['score'] = SequenceMatcher(None, query_term, entity['label']).ratio()
        results_with_scores.append(result)
    return sorted(results_with_scores, key=lambda x: x['score'], reverse=True)[:number_of_results]


"""The following function is a wrapper for authentication in the OpenAI API
It takes in input the name of the organization and the name of the project and gives as output
the client object"""

def openAI_authentication(key):
    client = OpenAI(
        api_key = key
    )
    return client


"""The following function is a wrapper for authentication in the Groq API. 
It takes as input the API key and returns the client object"""

def groq_authentication(key):
    client = Groq(
        api_key = key
    )
    return client
