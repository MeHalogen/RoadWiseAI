# api_server.py
# FastAPI backend server for RoadWiseAI (Optional REST API)

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import json
from intervener_kb import InterventionKB
from intervener_retrieval import RetrievalEngine
from intervener_explainer import ExplanationLayer
from intervener_reporter import ReportGenerator

# Initialize app
app = FastAPI(
    title="RoadWiseAI API",
    description="Road Safety Intervention GPT - REST API",
    version="2.0.0"
)

# Initialize modules
kb = InterventionKB("GPT_Input_DB.xlsx")
retrieval_engine = RetrievalEngine(kb)
explainer = ExplanationLayer()
reporter = ReportGenerator()

# Request/Response models
class RecommendationRequest(BaseModel):
    """Request model for recommendations."""
    query: str
    road_type: Optional[str] = None
    environment: Optional[str] = None
    top_k: int = 3

class RecommendationResponse(BaseModel):
    """Response model for recommendations."""
    status: str
    query: dict
    recommendations: List[dict]
    total_recommendations: int
    metadata: dict

# Routes
@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": "RoadWiseAI API",
        "version": "2.0.0",
        "description": "Road Safety Intervention GPT",
        "endpoints": {
            "/suggest": "POST - Get intervention recommendations",
            "/health": "GET - Health check",
            "/kb/stats": "GET - Knowledge base statistics"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "kb_size": len(kb.get_all()),
        "service": "RoadWiseAI v2.0"
    }

@app.get("/kb/stats")
async def kb_statistics():
    """Get knowledge base statistics."""
    interventions = kb.get_all()
    road_types = set()
    priorities = {}
    
    for interv in interventions:
        for rt in interv['road_type_tags']:
            road_types.add(rt)
        priority = interv['priority']
        priorities[priority] = priorities.get(priority, 0) + 1
    
    return {
        "total_interventions": len(interventions),
        "road_types": list(road_types),
        "priority_breakdown": priorities,
        "sources": ["IRC 35", "IRC 67", "IRC 99", "IRC SP:84", "IRC SP:87"]
    }

@app.post("/suggest")
async def get_recommendations(request: RecommendationRequest) -> RecommendationResponse:
    """
    Get intervention recommendations for a road safety issue.
    
    Args:
        request (RecommendationRequest): Query details
        
    Returns:
        RecommendationResponse: Ranked recommendations with explanations
    """
    try:
        # Validate query
        if not request.query or not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Retrieve and rank
        scored_interventions = retrieval_engine.retrieve_and_rank(
            query=request.query,
            road_type=request.road_type,
            environment=request.environment,
            top_k=request.top_k
        )
        
        # Check threshold
        if not retrieval_engine.check_minimum_threshold(scored_interventions):
            return JSONResponse(
                status_code=200,
                content=explainer.generate_fallback_response(request.query)
            )
        
        # Format recommendations
        recommendations = [
            explainer.format_recommendation(interv, score)
            for interv, score in scored_interventions
        ]
        
        # Generate output
        output = explainer.generate_json_output(
            recommendations,
            request.query,
            request.road_type,
            request.environment
        )
        
        return JSONResponse(
            status_code=200,
            content=output
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/pdf")
async def generate_pdf(request: RecommendationRequest):
    """
    Generate a PDF report for recommendations.
    
    Args:
        request (RecommendationRequest): Query details
        
    Returns:
        FileResponse: PDF report file
    """
    try:
        scored_interventions = retrieval_engine.retrieve_and_rank(
            query=request.query,
            road_type=request.road_type,
            environment=request.environment,
            top_k=request.top_k
        )
        
        if not retrieval_engine.check_minimum_threshold(scored_interventions):
            raise HTTPException(status_code=400, detail="No suitable interventions found")
        
        recommendations = [
            explainer.format_recommendation(interv, score)
            for interv, score in scored_interventions
        ]
        
        pdf_path = "report.pdf"
        reporter.generate_pdf_report(
            recommendations,
            request.query,
            request.road_type,
            request.environment,
            pdf_path
        )
        
        return FileResponse(pdf_path, media_type="application/pdf", filename="RoadWiseAI_Report.pdf")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate/pptx")
async def generate_presentation(request: RecommendationRequest):
    """
    Generate a PowerPoint presentation for recommendations.
    
    Args:
        request (RecommendationRequest): Query details
        
    Returns:
        FileResponse: PowerPoint file
    """
    try:
        scored_interventions = retrieval_engine.retrieve_and_rank(
            query=request.query,
            road_type=request.road_type,
            environment=request.environment,
            top_k=request.top_k
        )
        
        if not retrieval_engine.check_minimum_threshold(scored_interventions):
            raise HTTPException(status_code=400, detail="No suitable interventions found")
        
        recommendations = [
            explainer.format_recommendation(interv, score)
            for interv, score in scored_interventions
        ]
        
        pptx_path = "presentation.pptx"
        reporter.generate_pptx_report(
            recommendations,
            request.query,
            request.road_type,
            request.environment,
            pptx_path
        )
        
        return FileResponse(
            pptx_path,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            filename="RoadWiseAI_Presentation.pptx"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)