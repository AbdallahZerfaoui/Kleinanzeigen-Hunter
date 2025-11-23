"""Router for application generation endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from services.application_service import ApplicationService
from fastapi import Query

router = APIRouter(prefix="/applications", tags=["applications"])


class ApplicationMetadata(BaseModel):
    """Metadata about the generated application."""
    
    generated_at: str
    language: str
    affordability_score: float
    rent_to_income_ratio: float
    recommendation: str
    model_used: str


class RentalInfo(BaseModel):
    """Rental listing information."""
    
    adid: str
    title: Optional[str]
    price: Optional[int]
    location: Optional[str]
    rooms: Optional[float]
    space: Optional[float]
    deposit: Optional[float]
    additional_costs: Optional[float]
    available_from: Optional[str]
    url: str


class GenerateApplicationResponse(BaseModel):
    """Response model for generated applications."""
    
    success: bool
    subject: str
    message: str
    tips: List[str]
    rental_info: RentalInfo
    application_metadata: ApplicationMetadata


@router.get("/ad_id", response_model=GenerateApplicationResponse)
async def generate_application(
    ad_id: str = Query("3225566057", description="The rental listing ID from the database")
    ) -> GenerateApplicationResponse:
    """Generate a personalized rental application message using AI.
    
    This endpoint takes a rental listing ID as a path parameter and generates 
    a presentation message based on the ad description and system prompts.
    
    The generation includes:
    - Professional greeting
    - Expression of interest in the property
    - Brief self-introduction
    - Request for viewing or more information
    
    Args:
        ad_id: The rental listing ID from the database
    
    Returns:
        GenerateApplicationResponse: Generated application with metadata
        
    Raises:
        HTTPException: 404 if rental listing not found, 500 if generation fails
    """
    service = ApplicationService()
    
    try:
        result = await service.generate_message(ad_id=ad_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Rental listing with ad_id '{ad_id}' not found in database"
            )
        
        return {
            "success": True,
            **result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate application: {str(e)}"
        )
    finally:
        await service.close()


@router.get("/health")
async def health_check():
    """Health check endpoint for application service."""
    return {
        "status": "healthy",
        "service": "application_service_api",
        "endpoints": ["GET /applications/{ad_id}"]
    }
