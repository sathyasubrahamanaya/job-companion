from typing import Dict, Any, Literal
from fastapi import APIRouter, Body, HTTPException, Response, Query, Depends
from app.schemas.response import APIResponse
from app.agents.resume_agent import get_resume_builder_agent
from app.utils.resume_renderer import render_resume_html
from app.utils.pdf_generator import generate_pdf_from_template
from app.schemas.resume import ResumeInput, ResumeData
from app.dependencies import get_current_user
from app.db.datamodels import User

router = APIRouter()

# --- 1. BUILD / PREVIEW (Returns JSON + HTML) ---
@router.post("/build", response_model=APIResponse[Dict[str, Any]])
async def build_resume(
    resume_input: ResumeInput = Body(..., description="Structured data from the UI form"),
    current_user: User = Depends(get_current_user) # Optional: Require login
):
    """
    Step 1: Takes raw form data, uses AI to polish it, and returns structured data + HTML preview.
    """
    agent = get_resume_builder_agent()
    
    try:
        # 1. Convert Pydantic model to a clean JSON string for the Agent
        input_json = resume_input.model_dump_json()
        
        # 2. Run the Agent
        # We ask the agent to enhance the data but keep the structure
        response = agent.run(f"Enhance this resume data: {input_json}")
        
        if not response or not response.content:
            raise ValueError("AI failed to generate resume data")
            
        # 3. Extract Structured Data
        polished_data: ResumeData = response.content

        # 4. Generate HTML for Frontend Preview
        html_content = render_resume_html(polished_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume generation failed: {str(e)}")

    return APIResponse[Dict[str, Any]](
        ErrorCode=0,
        Data={
            "json_data": polished_data.model_dump(),
            "html_content": html_content
        },
        Message="Resume polished and generated successfully"
    )

# --- 2. DOWNLOAD PDF (Returns Binary File) ---
@router.post("/download-pdf")
async def download_resume_pdf(
    resume_data: ResumeData = Body(..., description="Final polished data to print"),
    template: Literal["classic", "modern", "creative"] = Query("classic", description="Visual style"),
    current_user: User = Depends(get_current_user) # Optional: Require login
):
    """
    Step 2: Takes the final (approved) JSON data and generates a downloadable PDF.
    Styles: 'classic', 'modern', 'creative'
    """
    try:
        # 1. Generate PDF Bytes using ReportLab
        pdf_bytes = generate_pdf_from_template(resume_data, template_name=template)

        # 2. Create Filename
        clean_name = resume_data.full_name.replace(" ", "_")
        filename = f"{clean_name}_Resume_{template}.pdf"

        # 3. Return as File Download
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")