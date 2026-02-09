from app.schemas.resume import ResumeData

def render_resume_html(data: ResumeData) -> str:
    """
    Renders ResumeData into a clean, professional HTML string for frontend preview.
    Uses inline CSS for maximum compatibility and modern look.
    """
    
    # --- Helper for list items ---
    def render_list(items):
        return "".join([f"<li>{item}</li>" for item in items])

    # --- Header with Photo logic ---
    photo_html = ""
    if data.photo_url:
        photo_html = f'''
        <div style="flex-shrink: 0; margin-left: 20px;">
            <img src="{data.photo_url}" alt="Profile" style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px; border: 2px solid #e5e7eb;">
        </div>
        '''

    # --- HTML Template ---
    html = f'''
    <div style="font-family: 'Inter', sans-serif; color: #1f2937; max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);">
        
        <!-- Header -->
        <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #3b82f6; padding-bottom: 20px; margin-bottom: 20px;">
            <div style="flex-grow: 1;">
                <h1 style="font-size: 32px; font-weight: 800; color: #111827; margin: 0 0 8px 0;">{data.full_name}</h1>
                <div style="color: #4b5563; font-size: 14px; display: flex; flex-wrap: wrap; gap: 12px;">
                    <span>📧 {data.email}</span>
                    {f"<span>📱 {data.phone}</span>" if data.phone else ""}
                    {f"<span>🔗 <a href='{data.linkedin_url}' style='color: #3b82f6; text-decoration: none;'>LinkedIn</a></span>" if data.linkedin_url else ""}
                </div>
            </div>
            {photo_html}
        </div>

        <!-- Summary -->
        <section style="margin-bottom: 24px;">
            <h2 style="font-size: 18px; font-weight: 700; color: #3b82f6; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px;">Professional Summary</h2>
            <p style="font-size: 15px; line-height: 1.6; color: #374151;">{data.professional_summary}</p>
        </section>

        <!-- Skills -->
        <section style="margin-bottom: 24px;">
            <h2 style="font-size: 18px; font-weight: 700; color: #3b82f6; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px;">Technical Skills</h2>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                {"".join([f'<span style="background: #eff6ff; color: #1e40af; padding: 4px 12px; border-radius: 9999px; font-size: 13px; font-weight: 500;">{skill}</span>' for skill in data.skills])}
            </div>
        </section>

        <!-- Experience -->
        <section style="margin-bottom: 24px;">
            <h2 style="font-size: 18px; font-weight: 700; color: #3b82f6; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px;">Experience</h2>
            {"".join([f'''
            <div style="margin-bottom: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;">
                    <h3 style="font-size: 16px; font-weight: 700; color: #111827; margin: 0;">{exp.title}</h3>
                    <span style="font-size: 13px; color: #6b7280; font-weight: 500;">{exp.duration}</span>
                </div>
                <div style="font-size: 14px; color: #4b5563; font-style: italic; margin-bottom: 8px;">{exp.company}</div>
                <ul style="font-size: 14px; line-height: 1.5; color: #374151; margin: 0; padding-left: 20px;">
                    {render_list(exp.description)}
                </ul>
            </div>
            ''' for exp in data.experience])}
        </section>

        <!-- Education -->
        <section style="margin-bottom: 24px;">
            <h2 style="font-size: 18px; font-weight: 700; color: #3b82f6; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px;">Education</h2>
            {"".join([f'''
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;">
                <div>
                    <h3 style="font-size: 15px; font-weight: 700; color: #111827; margin: 0;">{edu.institution}</h3>
                    <div style="font-size: 14px; color: #4b5563;">{edu.degree}</div>
                </div>
                <span style="font-size: 13px; color: #6b7280;">{edu.year}</span>
            </div>
            ''' for edu in data.education])}
        </section>

        <!-- Projects -->
        {f'''
        <section>
            <h2 style="font-size: 18px; font-weight: 700; color: #3b82f6; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; border-bottom: 1px solid #e5e7eb; padding-bottom: 4px;">Projects</h2>
            {"".join([f'''
            <div style="margin-bottom: 12px;">
                <h3 style="font-size: 15px; font-weight: 700; color: #111827; margin: 0 0 4px 0;">{proj.name}</h3>
                <p style="font-size: 14px; line-height: 1.5; color: #374151; margin: 0 0 4px 0;">{proj.description}</p>
                <div style="font-size: 12px; color: #6b7280; font-style: italic;">Tech: {", ".join(proj.tech_stack)}</div>
            </div>
            ''' for proj in data.projects])}
        </section>
        ''' if data.projects else ""}

    </div>
    '''
    
    return html