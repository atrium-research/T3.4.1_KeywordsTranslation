from ..utils import query_best_matches_wikidata 
from ..clients import LLMClient
from ..prompt import PotentialEntitiesGenerationPrompt, EntitySelectionPrompt

class EntityExtractionPipeline:
    """Pipeline for extracting entities from research papers using any LLM client."""
    
    def __init__(self, llm_client: LLMClient):
        """
        Initialize the pipeline with an LLM client.
        
        Args:
            llm_client: Instance of LLMClient (or its subclasses)
        """
        self.llm_client = llm_client
    
    def generate_potential_entities(self, language: str, title: str, abstract: str, keywords: str, num_names: int = 10):
        """
        Generate potential entities using LLM based on paper metadata.
        
        Returns:
            List of generated entities or None if parsing fails
        """
        # print("🔍 Generating potential entities...")
        
        # Create prompt
        prompt_object = PotentialEntitiesGenerationPrompt(
            num_names, language, title, abstract, keywords
        )
        
        prompt = prompt_object.generate_prompt()
        
        # Call LLM
        try:
            response = self.llm_client.generate_response(
                "You are a helpful assistant.", 
                prompt
            )
            # print(f"✅ LLM Response: {response}")
            
            # Parse response
            entities = prompt_object.checking_schema_function(response)
            # print(f"📋 Generated {len(entities)} entities")
            return entities
            
        except Exception as e:
            print(f"❌ Failed to generate entities: {e}")
            return None
    
    def query_wikidata_matches(self, generated_entities):
        """
        Query Wikidata for best matches of generated entities.
        
        Returns:
            List of Wikidata entities with metadata
        """
        # print("🌐 Querying Wikidata for matches...")
        
        wikidata_entities = []
        for entity in generated_entities:
            matches = query_best_matches_wikidata(entity)
            wikidata_entities.extend(matches)
        
        # print(f"📊 Found {len(wikidata_entities)} Wikidata matches")
        return wikidata_entities
    
    def format_wikidata_entities(self, wikidata_entities):
        """Format Wikidata entities into a readable string."""
        formatted_string = ""
        for entity in wikidata_entities:
            formatted_string += (
                f"Entity: {entity['label']}; "
                f"Description: {entity['description']}; "
                f"URI: {entity['uri']}\n"
            )
        return formatted_string
    
    def filter_entities_with_llm(self, language: str, title: str, abstract: str, 
                               keywords: str, wikidata_entities_string: str, 
                               num_entities: int = 1):
        """
        Use LLM to filter and select best entities from Wikidata matches.
        
        Returns:
            List of selected entities or None if parsing fails
        """
        # print(f"🎯 Filtering to select top {num_entities} entities...")
        
        # Create selection prompt
        prompt_object = EntitySelectionPrompt(
            num_entities, language, title, abstract, keywords, wikidata_entities_string
        )
        prompt = prompt_object.generate_prompt()
        
        # Call LLM
        try:
            response = self.llm_client.generate_response(
                "You are a helpful assistant.",
                prompt
            )
            # print(f"✅ Selection Response: {response}")
            
            # Parse response
            selected_entities = prompt_object.checking_schema_function(response)
            # print(f"🎉 Selected {len(selected_entities)} final entities")
            return selected_entities
            
        except Exception as e:
            print(f"❌ Failed to filter entities: {e}")
            return []
    
    def extract_entities(self, language: str, title: str, abstract: str, keywords: str, num_entities: int = 1, num_generated_names: int = 10):
        """
        Complete pipeline to extract relevant entities from a research paper.
        
        This function:
        1. Generates potential entities using LLM
        2. Queries Wikidata for matches
        3. Uses LLM to filter and select the best entities
        
        Args:
            language: Original language of the paper
            title: Paper title
            abstract: Paper abstract
            keywords: Paper keywords
            num_entities: Number of final entities to return
            num_generated_names: Number of potential entities to generate initially
            
        Returns:
            List of selected entities or [] if process fails
        """
        # print("🚀 Starting entity extraction pipeline...")
        # print(f"📄 Paper: {title}")
        # print("-" * 50)
        
        # Step 1: Generate potential entities
        generated_entities = self.generate_potential_entities(
            language, title, abstract, keywords, num_generated_names
        )
        if not generated_entities:
            return []
        
        # Step 2: Query Wikidata
        wikidata_entities = self.query_wikidata_matches(generated_entities)
        if not wikidata_entities:
            print("❌ No Wikidata matches found")
            return []
        
        # Step 3: Format entities for LLM
        wikidata_entities_string = self.format_wikidata_entities(wikidata_entities)
        
        # Step 4: Filter with LLM
        selected_entities = self.filter_entities_with_llm(
            language, title, abstract, keywords, wikidata_entities_string, num_entities
        )
        
        if selected_entities:
            pass
            # print("✨ Entity extraction completed successfully!")
        else:
            print("❌ Entity extraction failed")
        
        return selected_entities
