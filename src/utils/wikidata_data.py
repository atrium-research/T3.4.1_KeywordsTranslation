"""
Wikidata utility functions extracted from legacy codebase.
Provides functionality for querying Wikidata API and SPARQL endpoints.
"""

import requests
from SPARQLWrapper import SPARQLWrapper, JSON
from difflib import SequenceMatcher
from typing import List, Dict, Optional, Any


def query_wikidata(query_term: str, language: str = "en") -> Optional[Dict[str, Any]]:
    """
    Query Wikidata API for a single term and return the best match.
    
    Args:
        query_term: The term to search for
        language: Language code for the search (default: "en")
        
    Returns:
        Dictionary with best matching entity or None if no match found
    """
    WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
    params = {
        'action': 'wbsearchentities',
        'search': query_term,
        'language': language,
        'format': 'json'
    }
    
    try:
        response = requests.get(WIKIDATA_API_URL, params=params)
        response.raise_for_status()
        search_results = response.json().get('search', [])
        
        if not search_results:
            return None
            
        # Find best match using sequence matching
        best_match = None
        highest_score = 0
        
        for result in search_results:
            score = SequenceMatcher(None, query_term.lower(), result['label'].lower()).ratio()
            if score > highest_score:
                highest_score = score
                best_match = result
                
        return best_match
        
    except requests.RequestException as e:
        print(f"Error querying Wikidata: {e}")
        return None


def query_best_matches_wikidata(
    query_term: str, 
    language: str = "en", 
    number_of_results: int = 3
) -> List[Dict[str, Any]]:
    """
    Query Wikidata API and return multiple best matches sorted by similarity score.
    
    Args:
        query_term: The term to search for
        language: Language code for the search (default: "en")
        number_of_results: Maximum number of results to return (default: 3)
        
    Returns:
        List of dictionaries with entity information and similarity scores
    """
    WIKIDATA_API_URL = "https://www.wikidata.org/w/api.php"
    params = {
        'action': 'wbsearchentities',
        'search': query_term,
        'language': language,
        'format': 'json'
    }
    
    try:
        response = requests.get(WIKIDATA_API_URL, params=params)
        response.raise_for_status()
        search_results = response.json().get('search', [])
        
        if not search_results:
            return []
            
        # Calculate similarity scores and format results
        results_with_scores = []
        for entity in search_results:
            result = {
                'label': entity['label'],
                'uri': entity['concepturi'],
                'description': entity.get('description', ''),
                'score': SequenceMatcher(None, query_term.lower(), entity['label'].lower()).ratio()
            }
            results_with_scores.append(result)
        
        # Sort by score (highest first) and return top results
        return sorted(results_with_scores, key=lambda x: x['score'], reverse=True)[:number_of_results]
        
    except requests.RequestException as e:
        print(f"Error querying Wikidata: {e}")
        return []


def get_wikidata_uri_from_dbpedia(dbpedia_uri: str) -> List[str]:
    """
    Map DBpedia URI to corresponding Wikidata URIs using SPARQL query.
    
    Args:
        dbpedia_uri: DBpedia URI to convert
        
    Returns:
        List of corresponding Wikidata URIs
    """
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    query = f"""
    PREFIX owl: <http://www.w3.org/2002/07/owl#>

    SELECT ?wikidataURI
    WHERE {{
      <{dbpedia_uri}> owl:sameAs ?wikidataURI .
      FILTER (STRSTARTS(STR(?wikidataURI), "http://www.wikidata.org/entity/"))
    }}
    """
    
    try:
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        
        wikidata_uris = [
            result["wikidataURI"]["value"] 
            for result in results["results"]["bindings"]
        ]
        return wikidata_uris
        
    except Exception as e:
        print(f"Error querying SPARQL endpoint: {e}")
        return []


def query_dbpedia_spotlight(text: str, language: str, confidence: float = 0.5) -> Optional[Dict[str, Any]]:
    """
    Query DBpedia Spotlight API for entity annotation.
    
    Args:
        text: Text to annotate
        language: Language code for the annotation
        confidence: Confidence threshold (default: 0.5)
        
    Returns:
        JSON response from DBpedia Spotlight or None if error
    """
    url = f'https://api.dbpedia-spotlight.org/{language}/annotate'
    headers = {'Accept': 'application/json'}
    params = {
        'text': text,
        'confidence': confidence
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
        
    except requests.RequestException as e:
        print(f'DBpedia Spotlight API error: {e}')
        return None


def extract_wikidata_entities_from_text(
    text: str, 
    language: str, 
    keywords: List[str] = None,
    use_context: bool = True
) -> List[Dict[str, Any]]:
    """
    Extract and map entities from text using DBpedia Spotlight and convert to Wikidata.
    
    Args:
        text: Input text for entity extraction
        language: Language code
        keywords: Optional list of keywords to filter results
        use_context: Whether to use full text context or just keywords
        
    Returns:
        List of extracted entities with DBpedia and Wikidata URIs
    """
    if not use_context and keywords:
        text = ", ".join(keywords)
    
    # Query DBpedia Spotlight
    spotlight_result = query_dbpedia_spotlight(text, language)
    if not spotlight_result or 'Resources' not in spotlight_result:
        return []
    
    results = []
    keywords_tokens = []
    if keywords:
        keywords_tokens = [token for kw in keywords for token in kw.split(' ')]
    
    # Process DBpedia Spotlight results
    for entity in spotlight_result['Resources']:
        surface_form = entity['@surfaceForm']
        
        # Filter by keywords if provided and using context
        if use_context and keywords and surface_form not in keywords_tokens:
            continue
            
        result = {
            'surface_form': surface_form,
            'dbpedia_uri': entity['@URI'],
            'wikidata_uris': []
        }
        
        # Convert to Wikidata URIs if language is English
        if language == 'en':
            result['wikidata_uris'] = get_wikidata_uri_from_dbpedia(entity['@URI'])
        
        results.append(result)
    
    # Remove duplicates based on surface form
    seen_forms = set()
    unique_results = []
    for result in results:
        if result['surface_form'] not in seen_forms:
            seen_forms.add(result['surface_form'])
            unique_results.append(result)
    
    return unique_results