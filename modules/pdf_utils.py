import re
from fpdf import FPDF

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
        return f"PDF generated: {filename}"
    except Exception as e:
        return f"Error generating PDF: {e}"
