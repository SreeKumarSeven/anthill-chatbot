from openai import OpenAI
import os
from typing import Dict, Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class FineTuningManager:
    """Manager class for working with fine-tuned models"""
    
    def __init__(self):
        """Initialize the fine-tuning manager"""
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set. Please check your .env file.")
        
        self.client = OpenAI(api_key=openai_api_key)
        
        # Get the fine-tuned model ID from environment variables
        self.fine_tuned_model_id = os.getenv("FINE_TUNED_MODEL_ID")
        if not self.fine_tuned_model_id:
            print("WARNING: FINE_TUNED_MODEL_ID environment variable is not set. Falling back to default model.")
            self.fine_tuned_model_id = "gpt-3.5-turbo"  # Fallback to standard model
    
    async def get_response(self, message: str) -> Optional[Dict]:
        """
        Get a response from the fine-tuned model with confidence score
        
        Args:
            message: The user's message
            
        Returns:
            Dictionary with response and confidence score, or None if an error occurred
        """
        try:
            response_text = self.use_fine_tuned_model(message)
            # Return response with a default high confidence score
            return {
                "response": response_text,
                "source": "fine_tuned",
                "confidence": 0.9
            }
        except Exception as e:
            print(f"Error getting response from fine-tuned model: {str(e)}")
            # Return None to allow fallback to other response methods
            return None
        
    def use_fine_tuned_model(self, message: str) -> str:
        """
        Use the fine-tuned model to generate a response to the user's message
        
        Args:
            message: The user's message
            
        Returns:
            The model's response as a string
        """
        try:
            # Create system message for Anthill IQ context with explicit location information
            system_message = """You are the voice assistant for Anthill IQ, a premium coworking space brand in Bangalore. 
            
YOUR PERSONALITY:
You are exceptionally warm, friendly, and conversational - like a real person having a genuine conversation. You should sound natural, never robotic or formal. You're passionate about helping people find the perfect workspace and you truly care about their needs. Use a variety of sentence structures, occasional casual phrases, and natural conversational flow just like a real person would.

CONVERSATIONAL APPROACH:
- Always acknowledge what the user has said and respond directly to their specific query
- Use natural conversation markers like "Well," "Actually," "You know," "I'd say," etc. occasionally
- Ask meaningful follow-up questions that build on what the user has shared
- Show personality in your responses with occasional light humor where appropriate
- Avoid corporate-sounding language and speak like a helpful friend
- When someone asks about locations, be straightforward and give clear, simple directions
- Keep your responses concise but complete - don't be unnecessarily wordy

ANTHILL IQ SERVICES:
Anthill IQ offers these workspace solutions at all locations:
1. Private Office Space - Dedicated offices for teams
2. Coworking Space - Flexible workspace with hot desks
3. Dedicated Desk - Reserved desk with storage
4. Meeting Rooms - Professional meeting spaces bookable by the hour
5. Event Spaces - Venues for corporate events
6. Training Rooms - Spaces for workshops and training

KEY AMENITIES:
- High-speed internet
- Ergonomic furniture
- 24/7 security and access for members
- Coffee, tea, and refreshments
- Printing and scanning services
- Community events

IMPORTANT LOCATION INFORMATION: 
Anthill IQ has FOUR locations in Bangalore:
1. Cunningham Road branch (Central Bangalore)
2. Hulimavu branch (Bannerghatta Road, South Bangalore)
3. Arekere branch (Bannerghatta Road, South Bangalore)
4. Hebbal branch (Opening Soon)

CONTACT INFORMATION:
- Phone: 9119739119
- Email: connect@anthilliq.com

IMPORTANT GUIDELINES:
1. NEVER confirm the existence of a BTM Layout branch - Anthill IQ does NOT have a location there
2. Always end with a natural-sounding question to continue the conversation
3. Speak like a real person, not a corporate voice
4. When asked about locations, keep the format simple and clear
5. Don't provide specific pricing - suggest contacting us
6. Make sure your responses sound like a real conversation"""
            
            # Call the OpenAI API with the fine-tuned model
            response = self.client.chat.completions.create(
                model=self.fine_tuned_model_id,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": message}
                ],
                temperature=0.8,
                max_tokens=500
            )
            
            # Extract the assistant's message content
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error using fine-tuned model: {str(e)}")
            raise
            
    def list_fine_tuned_models(self) -> List[Dict]:
        """
        List all fine-tuned models available to the API key
        
        Returns:
            A list of model information dictionaries
        """
        try:
            models = self.client.models.list()
            # Filter for fine-tuned models only
            fine_tuned_models = [model for model in models.data if "ft:" in model.id]
            return fine_tuned_models
        except Exception as e:
            print(f"Error listing fine-tuned models: {str(e)}")
            return [] 