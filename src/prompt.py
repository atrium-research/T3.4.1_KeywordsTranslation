POTENTIAL_ENTITIES_GENERATION_PROMPT = """
You are a helpful assistant. 
You will be provided information about an academic article in the area of social sciences and humanities. 
You will be provided the following elements about the article: Original language of the article, Title of the article, Abstract of the article.
When one of these elements is not available, you will be provided an empty string.

Your goal is the following: given a keyword (which has been provided by the author of the article and can be in any language), find the corresponding entity in Wikidata. 
You have to provide the name of the entity, then another agent will take care of finding the corresponding URI.
In some cases, the keyword is a Wikidata entity itself (for example, a word like "horse" has a Wikidata entity with the same name).
In other cases (complex concept or expression), you have to provide entities that you think are related to the keyword, given your understanding of the article content. 

You can give up to {number_of_names} potential entity names for a keyword. 
You don't necessarily have to provide {number_of_names} names: 1 name is enough if the keyword is a simple concept. However, you need to provide at least 1 name.
Give the list of names separated by commas. The names should always be in English. Please, include only the list of names in the output, without any other text.

Original language of the article: {original_language}
Title of the article: {title}
Abstract of the article: {abstract}
Keyword: {keyword}
"""


ENTITY_SELECTION_PROMPT = """
You are a helpful assistant. 
You will be provided with a list of Wikidata entities and their descriptions. 
These entities are potential matches for a keyword of an academic article.
You will be provided the following elements about the article: Original language of the article, Title of the article, Abstract of the article, and the original keyword (note that the keyword can be in any language).

Your goal is the following: given the list of entities and their descriptions, select the best matching entity that matches the keyword.

Provide the URI of the best matching entity. Please, include only the URI, without any other text.

Original language of the article: {original_language}
Title of the article: {title}
Abstract of the article: {abstract}
Keyword: {keyword}

Entities: 
{entities}
"""

DIRECT_WIKIDATA_LINKING_PROMPT = """
You are a helpful assistant. 
You are provided with metadata about an academic article: its original language, title, abstract, and author-provided keywords (which may be in any language).
Your task is to find, for each keyword, the **most relevant Wikidata entity**, and return the following fields:

- The original keyword (as written)
- The English label of the matched Wikidata entity
- A brief description of that entity
- The Wikidata URI (e.g., https://www.wikidata.org/wiki/Q42)

 Output format instructions (MANDATORY):

- Respond **only** with a **pure JSON list**.
- Do **not** wrap the response in code blocks (e.g., do **not** use triple backticks ```).
- Do **not** prepend any text such as "Here is the JSON:".
- Do **not** use Markdown syntax at all.
- The output must be strictly parsable with `json.loads()` without any preprocessing.

Return the list where each item is an object with the fields:  
`"keyword"`, `"label"`, `"description"`, and `"uri"`.

Original language of the article: {original_language}  
Title of the article: {title}  
Abstract of the article: {abstract}  
Keywords: {keywords}
"""

DIRECT_WIKIDATA_LINKING_PROMPT_OLD= """
We process a scientific article of which we have the TITLE, the ABSTRACT and the KEYWORDS separated by commas.

The language of the article is English but the KEYWORDS can be in different languages.

The goal is to: map each keyword to corresponding URLs of controlled vocabularies of Wikidata or close enough match with Wikidata entries.
TO DO:

Use the TITLE and ABSTRACT as context. Use this context to suggest a mapping of each keyword to a URL.
VERIFY for each URL if it actually corresponds to the expected Wikidata entry. To do so, load the Wikidata page: the concept MUST BE in the title of the retrieved Wikidata entry.

Otherwise report the mismatch.

TITLE: Demonstrative pronouns and articles in Egyptian and Coptic ; emergence and development

ABSTRACT: This dissertation investigates the demonstratives in Old Egyptian. It shows that the proper description of the Old Kingdom deictic system delivers key insights into the emergence of the new proclitic forms "pȝ", "tȜ", "nȜ", which later grammaticalize to definite articles. In order to define the features of the Old Kingdom demonstratives, I provide an in-depth introduction into the current methods of analysis of deixis and specificity. I further summarise the Egyptological research, dedicated to the demonstratives in Old Egyptian. Although the temporal frames of this study are confined to the Old Kingdom, I deal extensively with the category of determination in Middle Egyptian, Demotic and Coptic. I extend the reviews with the commentaries, and introduce the original topics, such as determiner compatibilities and syntactic specificity effects. In preparation for the analysis of demonstratives in the Old Kingdom I provide the diachronic, diaphasic, and diastratic features of the core textual records. The analysis section embraces the typological and diatopic traits of Old Kingdom demonstratives, supplemented by the overview of the grammaticalization patterns of Afro-Asiatic deictic roots. I demonstrate the presence of two competing deictic systems in the Old Kingdom Egypt: one based on the joint attentional focus of the interlocutors, operating with "pn" as attention shifter and "pw" as attention tracker; and an alternative one, relying on the distance contrast, utilising "pf" for a distal referent and "pn" for a proximal referent. The attentional system is visibly in decline in the literary discourse, the process possibly triggered by the arrival of the emphatic "pf". It persists, however, in the colloquial stratum, as manifested by the emergence of the recognitional "pȝ", "tȝ", "nȝ". The morphological features suggest that these are the allomorphs of the attention trackers "pw", "tw", "nw", as proven by the change "w" → "ȝ" in deictic and non-deictic lexemes containing the final "w". I put forward the hypothesis ... 
KEYWORDS: demonstrative pronouns, definite articles, grammaticalization, Old Egyptian, Coptic, Old Kingdom, joint attention, dialects, ddc:417
"""



class PotentialEntitiesGenerationPrompt:
    def __init__(self, number_of_names, original_language, title, abstract, keyword):
        self.number_of_names = number_of_names
        self.original_language = original_language
        self.title = title
        self.abstract = abstract
        self.keyword = keyword

    def generate_prompt(self):
        return POTENTIAL_ENTITIES_GENERATION_PROMPT.format(number_of_names=self.number_of_names, original_language=self.original_language, title=self.title, abstract=self.abstract, keyword=self.keyword)

    def checking_schema_function(self, answer: str) -> str:
        try:
            answer = answer.strip()
            answer = answer.split(",")
            return answer
        except:
            return None
        

class EntitySelectionPrompt:
    def __init__(self, number_of_entities, original_language, title, abstract, keyword, entities):
        self.number_of_entities = number_of_entities
        self.original_language = original_language
        self.title = title
        self.abstract = abstract
        self.keyword = keyword
        self.entities = entities

    def generate_prompt(self):
        return ENTITY_SELECTION_PROMPT.format(number_of_entities=self.number_of_entities, original_language=self.original_language, title=self.title, abstract=self.abstract, keyword=self.keyword, entities=self.entities)

    def checking_schema_function(self, answer: str) -> str:
        try:
            answer = answer.strip()
            answer_comma_splitted = answer.split(",")
            if len(answer_comma_splitted) == 1:
                answer_dot_splitted = answer.split(".")
                if len(answer_dot_splitted) == 1:
                    answer_newline_splitted = answer.split("\n")
                    if len(answer_newline_splitted) == 1:
                        answer_space_splitted = answer.split(" ")
                        if len(answer_space_splitted) == 1:
                            return []
                        else:
                            return [uri.strip() for uri in answer_space_splitted]
                    else:
                        return [uri.strip() for uri in answer_newline_splitted]
                else:
                    return [uri.strip() for uri in answer_dot_splitted]
            else:
                return [uri.strip() for uri in answer_comma_splitted]
        except:
            return None
        

class DirectWikidataLinkingPrompt:
    def __init__(self, language, title, abstract, keywords):
        self.language = language
        self.title = title
        self.abstract = abstract
        self.keywords = keywords

    def generate_prompt(self):
        return DIRECT_WIKIDATA_LINKING_PROMPT.format(
            original_language=self.language,
            title=self.title,
            abstract=self.abstract,
            keywords=self.keywords,
        )

    def checking_schema_function(self, answer: str):
        import json

        try:
            #print("RAW LLM RESPONSE:")
            print(answer)
            parsed = json.loads(answer)
            if not isinstance(parsed, list):
                print("Ha ritornato none, il json non va bene")
                return None
            validated = []
            for item in parsed:
                if not all(k in item for k in ("keyword", "label", "description", "uri")):
                    print("Ha ritornato none, il non ci sono le keyword")
                    continue
                transformed_uri =  item["uri"].replace("https://", "")
                transformed_uri = transformed_uri.replace("wiki/", "entity/")
                first_split = transformed_uri.split('.', 1)
                www_part = first_split[0]
                remaining_part = first_split[1]
                second_split = remaining_part.split('.', 1)
                wikidata_part = second_split[0]
                org_entity_part = second_split[1]
                validated.append("http://" + www_part)  # Aggiunge "http://www"
                validated.append(wikidata_part)  # Aggiunge "wikidata"
                validated.append(org_entity_part)  # Aggiunge "org/entity/roba"
            return validated
        except Exception as e:
            print(f"⚠️ JSON parsing error in LLM response: {e}")
            return None
