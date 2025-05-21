import os
import numpy as np
import pandas as pd
from typing import List, Tuple, Optional
from openai import OpenAI
from dotenv import load_dotenv
from api.backend_for_vercel.sheets_manager import GoogleSheetsManager

# Try to import faiss, but provide a fallback if it's not available
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    print("FAISS not available, using fallback similarity search")
    FAISS_AVAILABLE = False

# Load environment variables from .env file
load_dotenv()

class FAQEmbeddingManager:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set. Please check your .env file.")
            
        self.client = OpenAI(api_key=openai_api_key)
        self.sheets_manager = GoogleSheetsManager()
        self.embedding_dim = 1536  # OpenAI's embedding dimension
        self.faqs = self.load_faqs()
        
        # Flag to track if we have valid OpenAI API access
        self.use_embeddings = True and FAISS_AVAILABLE  # Only use if FAISS is available
        
        # Initialize FAISS index
        self.index = None
        self.embeddings = None
        
        # For caching question embeddings with their index
        self.question_map = {}
        
        # Try to build index if we have FAQs
        if len(self.faqs) > 0:
            try:
                self.build_index()
            except Exception as e:
                print(f"Could not build FAISS index, falling back to keyword matching: {str(e)}")
                self.use_embeddings = False

    def load_faqs(self) -> pd.DataFrame:
        """Load FAQs from Google Sheets"""
        # First try to get FAQs from Google Sheets
        sheet_faqs = self.sheets_manager.get_faqs()
        
        if sheet_faqs:
            print(f"Loaded {len(sheet_faqs)} FAQs from Google Sheets")
            return pd.DataFrame(sheet_faqs)
        
        # Fallback to a sample FAQ dataset if no sheets data
        sample_faqs = [
            {
                "Question": "What is Anthill IQ?",
                "Answer": "Anthill IQ is a leading business consulting firm specializing in digital transformation and strategic business optimization."
            },
            {
                "Question": "What services do you offer?",
                "Answer": "We offer comprehensive services including business strategy consulting, digital transformation, process optimization, data analytics, and technology implementation."
            },
            {
                "Question": "How can I schedule a consultation?",
                "Answer": "You can schedule a consultation using our booking form on the website. Just provide your contact details and preferred time."
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
        """Build FAISS index from FAQs"""
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
            
            # Create FAISS index
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.index.add(self.embeddings)
            
            print(f"Built FAISS index with {len(self.faqs)} FAQs")
            return True
        except Exception as e:
            print(f"Error building FAISS index: {str(e)}")
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
            if not self.use_embeddings or self.index is None:
                raise Exception("Embeddings not available")
                
            # Create embedding for query
            query_embedding = self.create_embedding(query)
            query_embedding = np.array([query_embedding], dtype=np.float32)
            
            # Search the index
            distances, indices = self.index.search(query_embedding, top_k)
            
            results = []
            for i in range(len(indices[0])):
                idx = indices[0][i]
                distance = distances[0][i]
                
                # Convert distance to similarity score (0-1)
                # FAISS uses L2 distance, so smaller is better
                # We convert to a similarity score where 1 is perfect match
                max_reasonable_distance = 10.0  # Hyperparameter to tune
                similarity = max(0, 1 - (distance / max_reasonable_distance))
                
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
        if not self.use_embeddings or self.index is None or len(self.faqs) == 0:
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
        """Refresh FAQs from Google Sheets and rebuild index"""
        try:
            self.faqs = self.load_faqs()
            if self.use_embeddings:
                return self.build_index()
            return True
        except Exception as e:
            print(f"Error refreshing FAQs: {str(e)}")
            return False 