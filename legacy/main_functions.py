"""This file contains functions to use tools to map GoTriple keywords to WikiData pages. 
Each function takes as input an item from the list produced by the function get_sample in data_utils.py 
(each item contains information about the title, the abstract and the keywords of the article, see data_utils.py for further details)
"""

import requests
import importlib
import legacy.data_utils as data_utils
import tools_utils
import legacy.prompt_utils as prompt_utils
#  from llama_cpp import Llama
import re
from openai import OpenAI

from tenacity import (
  retry,
  stop_after_attempt,
  wait_random_exponential,
)  # for exponential backoff

"""- The first function uses DBPedia Spotlight. It maps keywords to DBPedia resources 
(each keyword is mapped to the DBPedia correspondent to the keywords language) 
if the language of the keyword is different than 'en' (English). 
- The parameter 'context' specifies the text that is given as input to DBPedia Spotlight. 
If True, the title and abstract are given as additional context (this slows execution since DBPedia Spotlight 
annotates the whole input). If False, only keywords are given as input
- If keywords are in English, a further mapping from DBPedia to Wikidata resources is performed 
(using SPARQL). This feature is not available for other languages for what it seems 
like a lack of semantic annotation (the SPARQL engine is not available for DBPedia corresponding to some languages and there is shortage of annotated links between pages in different languages). Moreover, it should be noted that the performance of DBPedia Spotlight seems to be poorer when it is used in languages other than English (THIS NEEDS VERIFICATION).

- The function returns a list where each element corresponds to an annotation. 
Each element of the returned list has three keys: 'Form' (specifies the surface form that DBPedia Spotlight has linked to the URI), 
'DBPediaURI' and 'WikiDataURI' (contains None if the language of the keywords is not English) """

def useDBPediaSpotlight(item, context):

    results = []

    #  useful to retrieve entities relevant to the keywords (and not to the context) in case of search with context
    keywords_token = [token for kw in item['Keywords'] for token in kw.split(' ')]

    abstract = item['Abstract_or'] if item['Abstract_or'] else ""
    title = item['Title_or'] if item['Title_or'] else ""

    #  prepare the text for the query
    if context:
        text = 'Title: ' + title + '. ' + 'Abstract: ' + abstract + '. Keywords: ' + ", ".join(item['Keywords'])
    else:
        text = ", ".join(item['Keywords'])

    #  send a request to DBPedia Spotlight API
    data = tools_utils.queryAPIDBpediaSpotlight(text, item['Language'])['Resources']

    #  processes the output to retain only entities corresponding to keywords
    for entity in data:
        if context:
            if entity['@surfaceForm'] in keywords_token:
                results.append({'Form': entity['@surfaceForm'], 'DBPediaURI': entity['@URI']})
        else: 
            results.append({'Form': entity['@surfaceForm'], 'DBPediaURI': entity['@URI']})

    #  conversion of DBPedia URIs in Wikidata URIs
    for result in results:
        if item['Language'] == 'en':
            result['WikidataURI'] = tools_utils.get_wikidata_uri(result['DBPediaURI'])
        else: 
            result['WikidataURI'] = None

    
    #  remove duplicates
    words_in_results = []
    final_results = []
    for result in results:
        if result['Form'] not in words_in_results:
            words_in_results.append(result['Form'])
            final_results.append(result)
    
    return results


"""
The second function uses Open Source LLMs. In this notebook, we use Llama.cpp, a library where various LLMs are implemented in C++ 
in order to allow faster inference times even on CPU. The library allows inference on variety of quantized LLMs available 
on HuggingFace in GGUF format. We use the library in order to allow replicability of the code without requiring 
specialized software. Specifically, we use llama-cpp-python, a Python wrapper of the library.
- The function takes as input item (an item from the list produced by the function get_sample in data_utils.py), 
model (a model loaded via the Python wrapper of the Llama.cpp library), and context (controls the context that we provide to the model:
"Title" if we want to provide the title with no abstract, "All" if we want to provide the title and the abstract, 
otherwise we will provide only the keywords). 
- The function prompts the model for the Wikidata entities corresponding to the keywords and then 
performs a query on Wikidata using the WikiData API (the requests and the method for searching the best fit 
are in a function in tools_utils.py). It returns a list of dictionaries where each dictionary has a field 'Keyword' 
and a field 'URI' (the second has no value if the query gives no result)

NB: This feature is only for experimentation since it has very slow response time.  

"""

def useLLM(item, model, context):
    prompt = data_utils.prompt_generator(item, context)

    output = model(
      prompt,
      max_tokens=200, 
    ) 

    #  formatting of the answer (this procedure is dependent on the output form we impose via the prompt.)
    entities = re.findall(r'\[([^\]]+)\]', output['choices'][0]['text'])

    #  Wikidata query
    results = []
    for entity in entities:
        item = {}
        item['Keyword'] = entity
        uri = tools_utils.query_wikidata(entity.lower().split("()")[0])
        if uri:
            item['URI'] = uri['concepturi']
        else:
            item['URI'] = ''
        results.append(item)

    return results



"""
The third function allows to use OpenAI LLMs by encapsulating calls via the openAI API. The function requires 
previous authentication, otherwise it will not work. Like the function useLLM, the function takes as input item 
(an item from the list produced by the function get_sample in data_utils.py), context (controls the context that 
we provide to the model) and model (this time, model is the ID of the model to use - see https://platform.openai.com/docs/models/tts). 
It also takes as input client (the object created by the OpenAI API after authentication - it should be created outside 
the function and given as input to the function).
The function creates a prompt analogous to the function useLLM. In particular, the prompt is structured so that the entities 
recognized by the model are included in square brackets in the response, so that they can easily be retrieved using a regular expression.

As can be seen, the function uses default values for arguments when the OpenAI API is called. 
Default values are listed in https://platform.openai.com/docs/api-reference/chat/create. In order to change the values,
feel free to change the call to the API (client.chat.completions.create)

As the function useLLM, this function performs a query on Wikidata using the WikiData API 
(the requests and the method for searching the best fit are in a function in tools_utils.py). 
It returns a list of dictionaries where each dictionary has a field 'Keyword' and a field 'URI' 
(the second has no value if the query gives no result)
"""

def useOpenAILLM(item, model, context, client):
  prompt = data_utils.prompt_generator(item, context)

  completion = client.chat.completions.create(
      model=model,
      messages=[
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": prompt}
      ]
    )
  
  
  #  formatting of the answer 
  entities = re.findall(r'\[([^\]]+)\]', completion.choices[0].message.content)

  #  Wikidata query (same code of the useLLM function)
  results = []
  for entity in entities:
      item = {}
      item['Keyword'] = entity
      uri = tools_utils.query_wikidata(entity.lower().split("()")[0])
      if uri:
          item['URI'] = uri['concepturi']
      else:
          item['URI'] = ''
      results.append(item)

  return results


"""
The next function allows to use open-source LLMs via the Groq API. The function requires 
previous authentication, otherwise it will not work. Like the function useLLM, the function takes as input item 
(an item from the list produced by the function get_sample in data_utils.py), context (controls the context that 
we provide to the model) and model (this time, model is the ID of the model to use - see https://console.groq.com/docs/models). 
It also takes as input client (the object created by the Groq API after authentication - it should be created outside 
the function and given as input to the function).
The function creates a prompt analogous to the function useLLM. In particular, the prompt is structured so that the entities 
recognized by the model are included in square brackets in the response, so that they can easily be retrieved using a regular expression.


As the function useLLM, this function performs a query on Wikidata using the WikiData API 
(the requests and the method for searching the best fit are in a function in tools_utils.py). 
It returns a list of dictionaries where each dictionary has a field 'Keyword' and a field 'URI' 
(the second has no value if the query gives no result)
"""

def useGroqLLM(item, model_name, context, client):
    prompt = data_utils.prompt_generator(item, context)

    completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
    ],
    model=model_name
    )

    entities = re.findall(r'\[([^\]]+)\]', completion.choices[0].message.content)

    results = []
    for entity in entities:
        item = {}
        item['Keyword'] = entity
        uri = tools_utils.query_wikidata(entity.lower().split("()")[0])
        if uri:
            item['URI'] = uri['concepturi']
        else:
            item['URI'] = ''
        results.append(item)

    return results


def useLLM_back_and_forth(original_language, title, abstract, keyword, client, model_name, num_entities=1, NUM_NAMES = 10):

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def completion_with_backoff(**kwargs):
        return client.chat.completions.create(**kwargs)    
    
    # generate all entities and parse it
    potential_entities_generation_prompt_object = prompt_utils.PotentialEntitiesGenerationPrompt(NUM_NAMES, original_language, title, abstract, keyword)
    potential_entities_generation_prompt = potential_entities_generation_prompt_object.generate_prompt()

    completion = completion_with_backoff(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": potential_entities_generation_prompt},
        ],
        model=model_name
    )


    response = completion.choices[0].message.content
    print(f"generate all entities and parse it {response}")
    try:
        llm_generated_entities = potential_entities_generation_prompt_object.checking_schema_function(response)
    except:
        print("Generated potential entities cannot be parsed")
        return None
    
    print(f"take best matches with wikidata {llm_generated_entities}")
    # take best matches with wikidata
    wikidata_entities = []
    for generated_entity in llm_generated_entities:
        wikidata_entities.extend(tools_utils.query_best_matches_wikidata(generated_entity))

    wikidata_entities_string = ""
    for entity in wikidata_entities:
        wikidata_entities_string += "Entity: " + entity['label'] + "; " + "Description: " + entity['description'] + "; " + "URI: " + entity['uri'] + "\n"

    # filter best matches from wikidata with LLM
    entity_selection_prompt_object = prompt_utils.EntitySelectionPrompt(num_entities, original_language, title, abstract, keyword, wikidata_entities_string)
    entity_selection_prompt = entity_selection_prompt_object.generate_prompt()

    completion = completion_with_backoff(
            messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": entity_selection_prompt},
        ],
        model=model_name
    )

    response = completion.choices[0].message.content
    print(f"filter best matches from wikidata with LLM {response}")
    try:
        selected_entities = entity_selection_prompt_object.checking_schema_function(response)
    except:
        print("Selected entities cannot be parsed")
        return None

    return selected_entities

