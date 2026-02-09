import io
import requests
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, HRFlowable, Table, TableStyle, Image
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from app.schemas.resume import ResumeData

class ResumePDFBuilder:
    def __init__(self, resume_data: ResumeData):
        self.data = resume_data
        self.buffer = io.BytesIO()
        self.styles = getSampleStyleSheet()
        self.elements = []

    def _get_image_from_url(self, url):
        """Helper to fetch and prepare an image from a URL for ReportLab."""
        try:
            response = requests.get(url, stream=True, timeout=5)
            if response.status_code == 200:
                img_data = io.BytesIO(response.content)
                # Create ReportLab Image: width=25mm, height=25mm (square-ish aspect ratio preserved)
                img = Image(img_data, width=25*mm, height=25*mm)
                return img
        except Exception as e:
            print(f"Failed to load image: {e}")
        return None

    def create_bullet_list(self, items: list[str], style):
        """Creates a formatted list of bullet points."""
        bullets = []
        for item in items:
            bullets.append(
                ListItem(
                    Paragraph(item, style),
                    leftIndent=15,
                    value='circle'
                )
            )
        return ListFlowable(bullets, bulletType='bullet', start='circle', leftIndent=10)

    def build_classic(self):
        """
        Builds a Classic, ATS-friendly resume layout.
        Features: Times New Roman, clear hierarchy, standard formatting.
        """
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=LETTER,
            rightMargin=0.75*inch, leftMargin=0.75*inch,
            topMargin=0.75*inch, bottomMargin=0.75*inch
        )

        # --- Custom Styles ---
        header_name_style = ParagraphStyle('Name', parent=self.styles['Heading1'], alignment=TA_LEFT, fontName='Times-Bold', fontSize=20, spaceAfter=2)
        header_contact_style = ParagraphStyle('Contact', parent=self.styles['Normal'], alignment=TA_LEFT, fontName='Times-Roman', fontSize=10, textColor=colors.darkgrey)
        section_header_style = ParagraphStyle('Section', parent=self.styles['Heading2'], fontName='Times-Bold', fontSize=12, spaceBefore=12, spaceAfter=6, textTransform='uppercase', borderWidth=1, borderColor=colors.black, borderPadding=2, borderBottom=True)
        job_title_style = ParagraphStyle('JobTitle', parent=self.styles['Normal'], fontName='Times-Bold', fontSize=11)
        company_style = ParagraphStyle('Company', parent=self.styles['Normal'], fontName='Times-Italic', fontSize=11)
        date_style = ParagraphStyle('Date', parent=self.styles['Normal'], fontName='Times-Roman', fontSize=10, alignment=TA_RIGHT)
        body_style = ParagraphStyle('Body', parent=self.styles['Normal'], fontName='Times-Roman', fontSize=10.5, leading=14)

        # --- 1. Header Area (Name + Photo) ---
        contact_text = f"{self.data.email}"
        if self.data.phone: contact_text += f" | {self.data.phone}"
        if self.data.linkedin_url: contact_text += f" | {self.data.linkedin_url}"

        name_para = Paragraph(self.data.full_name, header_name_style)
        contact_para = Paragraph(contact_text, header_contact_style)

        # Fetch photo if exists
        photo_img = None
        if self.data.photo_url:
            photo_img = self._get_image_from_url(self.data.photo_url)

        if photo_img:
            # Table Layout: [Text Info (80%)] [Photo (20%)]
            header_data = [[ [name_para, contact_para], photo_img ]]
            t = Table(header_data, colWidths=[5.5*inch, 1.5*inch])
            t.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (1,0), (1,0), 'RIGHT'), # Align photo right
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ]))
            self.elements.append(t)
        else:
            # Text Only Layout
            self.elements.append(name_para)
            self.elements.append(contact_para)

        self.elements.append(Spacer(1, 10))
        self.elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))

        # --- 2. Professional Summary ---
        if self.data.professional_summary:
            self.elements.append(Paragraph("Professional Summary", section_header_style))
            self.elements.append(Paragraph(self.data.professional_summary, body_style))

        # --- 3. Skills ---
        if self.data.skills:
            self.elements.append(Paragraph("Technical Skills", section_header_style))
            skills_text = ", ".join(self.data.skills)
            self.elements.append(Paragraph(skills_text, body_style))

        # --- 4. Experience ---
        self.elements.append(Paragraph("Experience", section_header_style))
        for exp in self.data.experience:
            # Header Line: Title ..... Date
            # Subheader Line: Company
            
            # Using a Table for the "Title ... Date" split ensures perfect alignment
            title_para = Paragraph(f"<b>{exp.title}</b>", job_title_style)
            date_para = Paragraph(exp.duration, date_style)
            
            # Table: [Title (Left), Date (Right)]
            t_job = Table([[title_para, date_para]], colWidths=[5.5*inch, 1.5*inch])
            t_job.setStyle(TableStyle([
                ('ALIGN', (1,0), (1,0), 'RIGHT'),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ]))
            self.elements.append(t_job)
            
            self.elements.append(Paragraph(exp.company, company_style))
            self.elements.append(Spacer(1, 3))
            
            # Bullets
            self.elements.append(self.create_bullet_list(exp.description, body_style))
            self.elements.append(Spacer(1, 10))

        # --- 5. Education ---
        if self.data.education:
            self.elements.append(Paragraph("Education", section_header_style))
            for edu in self.data.education:
                edu_text = f"<b>{edu.institution}</b> - {edu.degree}"
                self.elements.append(Paragraph(edu_text, body_style))
                self.elements.append(Paragraph(f"<i>{edu.year}</i>", date_style))
                self.elements.append(Spacer(1, 5))

        # Build PDF
        doc.build(self.elements)
        return self.buffer.getvalue()

def generate_pdf_from_template(data: ResumeData, template_name: str = "classic") -> bytes:
    builder = ResumePDFBuilder(data)
    # You can add logic here to switch between builder.build_modern() etc.
    return builder.build_classic()