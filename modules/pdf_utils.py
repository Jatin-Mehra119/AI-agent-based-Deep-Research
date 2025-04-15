import re
import os
from fpdf import FPDF
import markdown
import tempfile
import pdfkit

# A simple PDF class that extends FPDF to add a header and footer and to handle UTF-8 encoding issues.
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "", 0, 1, "C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

def sanitize_content(content: str) -> str:
    try:
        return content.encode('utf-8', 'ignore').decode('utf-8')
    except Exception:
        return content.encode('ascii', 'ignore').decode('ascii')

def replace_problematic_characters(content: str) -> str:
    replacements = {
        '\u2013': '-', '\u2014': '--',
        '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"'
    }
    for char, replacement in replacements.items():
        content = content.replace(char, replacement)
    return content

def generate_pdf_from_md(content: str, filename: str = 'output.pdf') -> str:
    """
    Generate a PDF from markdown content using a hybrid approach:
    1. First try using pdfkit (which uses wkhtmltopdf)
    2. Fall back to the custom FPDF implementation if that fails
    """
    try:
        # Try the pdfkit method first (better markdown support)
        sanitized = replace_problematic_characters(sanitize_content(content))
        
        # Create HTML from markdown
        html = markdown.markdown(
            sanitized,
            extensions=['extra', 'smarty', 'tables']
        )
        
        # Add some basic styling 
        styled_html = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1 {{ color: #2c3e50; }}
                    h2 {{ color: #3498db; }}
                    h3 {{ color: #2980b9; }}
                    a {{ color: #2980b9; }}
                    blockquote {{ 
                        background: #f9f9f9; 
                        border-left: 10px solid #ccc;
                        margin: 1.5em 10px;
                        padding: 0.5em 10px;
                    }}
                    code {{ background: #f4f4f4; padding: 2px 4px; }}
                    pre {{ background: #f4f4f4; padding: 10px; }}
                </style>
            </head>
            <body>
                {html}
            </body>
        </html>
        """
        
        # Write to temp file then convert to PDF
        with tempfile.NamedTemporaryFile('w', suffix='.html', delete=False) as f:
            f.write(styled_html)
            temp_html = f.name
        
        try:
            # Try using pdfkit to convert HTML to PDF
            options = {
                'page-size': 'A4',
                'margin-top': '20mm',
                'margin-right': '20mm',
                'margin-bottom': '20mm',
                'margin-left': '20mm',
                'encoding': 'UTF-8',
            }
            pdfkit.from_file(temp_html, filename, options=options)
            os.unlink(temp_html)  # Clean up the temp file
            return f"PDF generated: {filename}"
        
        except Exception as e:
            # Fall back to FPDF method if pdfkit fails
            os.unlink(temp_html)  # Clean up the temp file
            return fallback_pdf_generation(sanitized, filename)
    
    except Exception as e:
        # Fall back to the original method
        return fallback_pdf_generation(content, filename)

def fallback_pdf_generation(content: str, filename: str) -> str:
    """Original FPDF-based method as a fallback"""
    try:
        pdf = PDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font('Arial', '', 12)

        sanitized = replace_problematic_characters(sanitize_content(content))
        
        for line in sanitized.split('\n'):
            if line.startswith('#'):
                header_level = min(line.count('#'), 4)
                header_text = re.sub(r'\*{2,}', '', line.strip('# ').strip())
                pdf.set_font('Arial', 'B', 12 + (4 - header_level) * 2)
                pdf.multi_cell(0, 10, header_text)
                pdf.set_font('Arial', '', 12)
            else:
                pdf.write(10, line)
            pdf.ln(10)
        pdf.output(filename)
        return f"PDF generated (fallback method): {filename}"
    except Exception as e:
        return f"Error generating PDF: {e}"