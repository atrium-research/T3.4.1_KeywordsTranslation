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
        

