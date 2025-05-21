import os
import numpy as np
import pandas as pd
from typing import List, Tuple, Optional
from openai import OpenAI
from dotenv import load_dotenv
from api.backend_for_vercel.database_manager import DatabaseManager
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables from .env file
load_dotenv()

class FAQEmbeddingManager:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set. Please check your .env file.")
            
        self.client = OpenAI(api_key=openai_api_key)
        self.db_manager = DatabaseManager()
        self.embedding_dim = 1536  # OpenAI's embedding dimension
        self.faqs = self.load_faqs()
        
        # Flag to track if we have valid OpenAI API access
        self.use_embeddings = True
        
        # Initialize embedding storage
        self.embeddings = None
        
        # For caching question embeddings with their index
        self.question_map = {}
        
        # Try to build index if we have FAQs
        if len(self.faqs) > 0:
            try:
                self.build_index()
            except Exception as e:
                print(f"Could not build embeddings index, falling back to keyword matching: {str(e)}")
                self.use_embeddings = False

    def load_faqs(self) -> pd.DataFrame:
        """Load FAQs from database"""
        # First try to get FAQs from database
        db_faqs = self.db_manager.get_faqs()
        
        if db_faqs:
            print(f"Loaded {len(db_faqs)} FAQs from database")
            return pd.DataFrame(db_faqs)
        
        # Fallback to a sample FAQ dataset if no database data
        sample_faqs = [
            {
                "Question": "What is Anthill IQ?",
                "Answer": "Anthill IQ is a premium coworking space with multiple locations across Bangalore, offering private offices, dedicated desks, meeting rooms, and flexible workspace solutions for professionals and businesses."
            },
            {
                "Question": "What services do you offer?",
                "Answer": "Anthill IQ offers private office spaces, dedicated desks, coworking spaces, meeting rooms, event spaces, and virtual office services at our locations in Bangalore."
            },
            {
                "Question": "How can I book a workspace?",
                "Answer": "You can book a workspace at Anthill IQ by contacting us at 9119739119 or emailing connect@anthilliq.com. Alternatively, you can use our booking form on the website or this chatbot."
            },
            {
                "Question": "Where are your locations?",
                "Answer": "Anthill IQ has four locations in Bangalore: Cunningham Road (Central Bangalore), Hulimavu (South Bangalore), Arekere (South Bangalore), and our upcoming location in Hebbal (North Bangalore)."
            }
        ]
        print("Using fallback sample FAQs")
        return pd.DataFrame(sample_faqs)

    def create_embedding(self, text: str) -> np.ndarray:
        """Create embedding for a piece of text using OpenAI API"""
        try:
            # Only try to get embeddings if we think it will work
            if not self.use_embeddings:
                raise Exception("Embeddings disabled due to previous errors")
                
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return np.array(response.data[0].embedding, dtype=np.float32)
        except Exception as e:
            print(f"Error creating embedding: {str(e)}")
            # If we get quota error, stop trying to use embeddings
            if "quota" in str(e).lower() or "insufficient_quota" in str(e).lower():
                self.use_embeddings = False
            # Return a zero vector as fallback
            return np.zeros(self.embedding_dim, dtype=np.float32)

    def build_index(self) -> bool:
        """Build embeddings for all FAQs"""
        try:
            # Create embeddings for all questions
            embeddings = []
            self.question_map = {}  # Reset the map
            
            for idx, question in enumerate(self.faqs["Question"].tolist()):
                embedding = self.create_embedding(question)
                # If we've disabled embeddings during this process, break out
                if not self.use_embeddings:
                    raise Exception("Embeddings disabled due to quota issues")
                embeddings.append(embedding)
                # Store question with its index for faster lookup
                self.question_map[idx] = question
                
            # Convert to numpy array
            self.embeddings = np.array(embeddings, dtype=np.float32)
            
            print(f"Built embeddings index with {len(self.faqs)} FAQs")
            return True
        except Exception as e:
            print(f"Error building embeddings index: {str(e)}")
            self.use_embeddings = False
            return False

    def keyword_match(self, query: str) -> Tuple[str, str, float]:
        """Find matching FAQ using simple keyword matching (fallback method)"""
        query_words = set(query.lower().split())
        
        best_score = 0
        best_q = None
        best_a = None
        
        for _, row in self.faqs.iterrows():
            question = row["Question"]
            answer = row["Answer"]
            
            # Calculate how many words match
            question_words = set(question.lower().split())
            matches = len(query_words.intersection(question_words))
            
            # Calculate a rough similarity score
            total_words = len(query_words.union(question_words))
            score = matches / total_words if total_words > 0 else 0
            
            if score > best_score:
                best_score = score
                best_q = question
                best_a = answer
        
        # Require at least some minimal matching
        if best_score < 0.1:
            return None, None, 0.0
            
        return best_q, best_a, best_score

    def semantic_search(self, query: str, top_k: int = 3) -> List[Tuple[str, str, float]]:
        """Search for the top k most similar FAQs to the query"""
        try:
            if not self.use_embeddings or self.embeddings is None:
                raise Exception("Embeddings not available")
                
            # Create embedding for query
            query_embedding = self.create_embedding(query)
            query_embedding = np.array([query_embedding])
            
            # Calculate cosine similarity between query and all FAQ embeddings
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            
            # Get indices of top k most similar questions
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                similarity = similarities[idx]
                
                # Get the FAQ details
                question = self.faqs.iloc[idx]["Question"]
                answer = self.faqs.iloc[idx]["Answer"]
                
                results.append((question, answer, similarity))
            
            return results
            
        except Exception as e:
            print(f"Error in semantic search: {str(e)}")
            return []  # Return empty list if there's an error

    def find_most_similar(self, query: str) -> Tuple[str, str, float]:
        """Find the most similar FAQ to the query"""
        # If embeddings are disabled or no index, use keyword matching
        if not self.use_embeddings or self.embeddings is None or len(self.faqs) == 0:
            print("Using keyword matching instead of embeddings")
            return self.keyword_match(query)
            
        try:
            # Get top 3 matches using semantic search
            results = self.semantic_search(query, top_k=3)
            
            if not results:
                # Fall back to keyword matching if no results
                return self.keyword_match(query)
                
            # Get the best match
            best_match = results[0]
            question, answer, similarity = best_match
            
            # If the similarity is too low, use keyword matching as a backup
            if similarity < 0.6:
                print(f"Semantic similarity too low ({similarity}), trying keyword matching")
                kw_question, kw_answer, kw_score = self.keyword_match(query)
                
                # If keyword matching score is decent, use that instead
                if kw_score > 0.2:
                    return kw_question, kw_answer, kw_score
            
            # Debug info
            print(f"Query: '{query}' matched to FAQ: '{question}' with similarity {similarity}")
            
            return question, answer, similarity
            
        except Exception as e:
            print(f"Error finding similar FAQ: {str(e)}")
            # Fall back to keyword matching
            print("Falling back to keyword matching")
            return self.keyword_match(query)

    def refresh_faqs(self) -> bool:
        """Refresh FAQs from database and rebuild index"""
        try:
            self.faqs = self.load_faqs()
            if self.use_embeddings:
                return self.build_index()
            return True
        except Exception as e:
            print(f"Error refreshing FAQs: {str(e)}")
            return False 