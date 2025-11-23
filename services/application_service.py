"""Service for generating personalized rental applications using LLM."""

import json
from typing import Optional, Dict, Any
from datetime import datetime
from utils.database import get_rental_by_adid
from utils.llm_client import OpenRouterClient, load_prompt
from models.results import RealEstateResult


class ApplicationService:
    """Service for generating personalized rental application messages."""
    
    def __init__(self):
        """Initialize the application service."""
        self.llm_client = None
    
    async def _get_llm_client(self) -> OpenRouterClient:
        """Get or create LLM client instance."""
        if self.llm_client is None:
            self.llm_client = OpenRouterClient()
        return self.llm_client
    
    async def generate_message(
        self,
        ad_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Generate presentation message using LLM based on ad description.
        
        Args:
            ad_id: The rental listing ID from database
            
        Returns:
            Dict with generated message, subject, and rental info
        """
        # Get rental from shared database
        rental_data = get_rental_by_adid(ad_id)
        if not rental_data:
            return None
        
        # Validate and parse rental data
        rental = RealEstateResult(**rental_data)
        
        # Build context for LLM
        user_prompt = self._build_user_prompt(rental=rental)
        
        # Load system prompt
        system_prompt = load_prompt("system_prompt.txt")
        
        # Generate application using LLM
        llm_client = await self._get_llm_client()
        try:
            response_text = await llm_client.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.7,
                max_tokens=1000,
            )
            
            # Parse JSON response
            response_data = self._parse_llm_response(response_text)
            
            return {
                "subject": response_data.get("subject", "Interesse an Ihrer Wohnung"),
                "message": response_data.get("message", ""),
                "tips": response_data.get("tips", []),
                "rental_info": {
                    "adid": rental.id,
                    "title": rental.title,
                    "price": rental.price,
                    "location": rental.location,
                    "rooms": rental.nbr_rooms,
                    "space": rental.rental_space,
                    "deposit": rental.deposit,
                    "additional_costs": rental.additional_costs,
                    "available_from": rental.available_from,
                    "url": rental.url,
                },
                "application_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "language": "german",
                    "affordability_score": 0.0,
                    "rent_to_income_ratio": 0.0,
                    "recommendation": "N/A",
                    "model_used": "google/gemini-2.0-flash-exp:free",
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate application: {str(e)}")
    
    def _build_user_prompt(
        self,
        rental: RealEstateResult,
    ) -> str:
        """Build the user prompt from rental details."""
        # Build a simple prompt with the rental information
        prompt = f"""Generate a professional, friendly presentation message in German for the following rental listing.

**Rental Details:**
- Title: {rental.title or 'N/A'}
- Location: {rental.location or 'N/A'}
- Price: {rental.price or 'N/A'} EUR/month
- Space: {rental.rental_space or 'N/A'} m²
- Rooms: {rental.nbr_rooms or 'N/A'}
- Deposit: {rental.deposit or 'N/A'} EUR
- Additional Costs: {rental.additional_costs or 'N/A'} EUR
- Available From: {rental.available_from or 'Nach Vereinbarung'}

The message should:
1. Express genuine interest in the property
2. Be polite and professional (use formal "Sie")
3. Request more information or a viewing
4. Be concise (3-5 sentences)
5. Sound natural and personal

Return a JSON object with:
{{
  "subject": "A short, appropriate subject line",
  "message": "The complete message text",
  "tips": ["Optional tip 1", "Optional tip 2"]
}}
"""
        return prompt
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response, handling potential JSON formatting issues."""
        try:
            # Try to find JSON block in response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback: treat entire response as message
                return {
                    "subject": "Bewerbung für Wohnung",
                    "message": response_text,
                    "tips": []
                }
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "subject": "Bewerbung für Wohnung",
                "message": response_text,
                "tips": []
            }
    
    async def close(self):
        """Close LLM client connection."""
        if self.llm_client:
            await self.llm_client.close()
