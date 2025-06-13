import pandas as pd
import requests
from difflib import SequenceMatcher

def parse_excel_file(filepath: str) -> list:
    # Read the Excel file
    df = pd.read_excel(filepath)
    
    # Identify all columns that match the keyword pattern:
    #   kw_1, wikidata_url_kw_1, match_kw_1,
    #   kw_2, wikidata_url_kw_2, match_kw_2, etc.
    # We'll do this by splitting column names and checking the prefix/suffix.
    # Another approach is a regex, but splitting can also work.

    # A small helper to extract the index i from "kw_i", "wikidata_url_kw_i", "match_kw_i"
    def get_kw_index(col_name, prefix):
        """
        Given a column name (e.g., 'kw_2') and a prefix (e.g., 'kw_'),
        return the integer index if it matches, otherwise None.
        """
        if col_name.startswith(prefix):
            # e.g. col_name = 'kw_2', prefix = 'kw_'
            # we want to extract '2'
            try:
                return int(col_name[len(prefix):])
            except ValueError:
                return None
        return None

    # We build a dictionary such that for each index i, we know the columns:
    # kw_i_col = 'kw_i'
    # wikidata_i_col = 'wikidata_url_kw_i'
    # match_i_col = 'match_kw_i'
    # We only do so if they exist in the DataFrame.
    max_index = 0
    for col in df.columns:
        idx = get_kw_index(col, 'kw_')
        if idx is not None and idx > max_index:
            max_index = idx

    # Now we have an idea of how many sets of kw / wikidata / match columns might exist (up to max_index)
    
    result = []
    
    for _, row in df.iterrows():
        # Build the base dictionary for each row
        row_dict = {
            'language': row.get('language', None),
            'id': row.get('id', None),
            'title_or': row.get('title_or', None),
            'title_eng': row.get('title_eng', None),
            'abstract_or': row.get('abstract_or', None),
            # In your description, you said 'abstract_eng': value of 'title_eng',
            # but that might be a typo. Assuming it should be 'abstract_eng'.
            'abstract_eng': row.get('abstract_eng', None),
            'kws': []
        }
        
        # Now collect relevant keywords
        kws = []
        
        for i in range(0, max_index):
            kw_label = row.get(f'kw_{i}', None)
            kw_wikidata = row.get(f'Wikidata_url_kw_{i}', None)
            kw_match = row.get(f'match_kw_{i}', None)

            # If the keyword cell is non-empty (not None or NaN) 
            # AND it’s relevant (i.e., wikidata_url or match is not empty),
            # then we collect it.
            if pd.notna(kw_label) and kw_label != "":
                # Check if the wikidata_url and match are actually meaningful
                # (not both empty).
                not_empty_wikidata = pd.notna(kw_wikidata) and kw_wikidata != ""
                not_empty_match = pd.notna(kw_match) and kw_match != ""
                
                if not_empty_wikidata and not_empty_match:
                    kws.append({
                        'label': kw_label,
                        'wikidata_url': kw_wikidata.split(";") if pd.notna(kw_wikidata) else [],
                        'match': kw_match if pd.notna(kw_match) else ""
                    })
        
        # Attach the collected keywords to our row dictionary
        row_dict['kws'] = kws
        
        # Append this row's dictionary to the result list
        result.append(row_dict)
    
    return result

#quante delle entità corrette sono state effettivamente recuperate.
def compute_recall(correct_uris, retrieved_uris):
    if len(correct_uris) == 0:
        return 0
    else:
        return len(set(correct_uris) & set(retrieved_uris)) / len(correct_uris)

#quante delle entità recuperate sono corrette.
def compute_precision(correct_uris, retrieved_uris):
    if len(retrieved_uris) == 0:
        return 0
    else:
        return len(set(correct_uris) & set(retrieved_uris)) / len(retrieved_uris)


def query_best_matches_wikidata(query_term, language = "en", number_of_results=10):
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
