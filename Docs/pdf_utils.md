# PDF Utils Module Documentation

The pdf_utils.py module provides functionality for converting Markdown content to PDF files using a hybrid approach with pdfkit (wkhtmltopdf) and FPDF library. This module includes utilities for handling text sanitization and PDF generation.

## Classes

### PDF

A subclass of FPDF that customizes the header and footer sections of PDF documents.

-   **header()**: Sets up a blank header with Arial font
-   **footer()**: Adds page numbers at the bottom of each page

## Functions

### sanitize_content(content: str) -> str

Sanitizes the input string to ensure it can be properly encoded in the PDF.

-   **Parameters**:
    -   content: The text to sanitize
-   **Returns**: Sanitized string with invalid characters removed
-   **Behavior**: First attempts UTF-8 encoding, falls back to ASCII if that fails

### replace_problematic_characters(content: str) -> str

Replaces common problematic Unicode characters with their ASCII equivalents.

-   **Parameters**:
    -   content: String containing potentially problematic characters
-   **Returns**: String with problematic characters replaced
-   **Replacements**:
    -   En dash (–) → hyphen (-)
    -   Em dash (—) → double hyphen (--)
    -   Smart quotes ('') → straight quotes (')
    -   Smart double quotes ("") → straight double quotes (")

### generate_pdf_from_md(content: str, filename: str = 'output.pdf') -> str

Converts Markdown content to a PDF file using a hybrid approach.

-   **Parameters**:
    -   content: Markdown formatted text to convert
    -   filename: Output PDF file path (defaults to 'output.pdf')
-   **Returns**: Success message with filename or error message
-   **Approach**:
    -   Primary method: Uses pdfkit (wkhtmltopdf) to convert markdown to HTML and then to PDF
    -   Fallback method: Uses FPDF if the pdfkit method fails
-   **Features**:
    -   Supports markdown extensions: 'extra', 'smarty', 'tables'
    -   Applies custom HTML styling including font, colors, and formatting
    -   Handles markdown headers with appropriate formatting
    -   Maintains paragraph spacing and styling

### fallback_pdf_generation(content: str, filename: str) -> str

Provides a fallback method for PDF generation using FPDF when the primary pdfkit method fails.

-   **Parameters**:
    -   content: Markdown formatted text to convert
    -   filename: Output PDF file path
-   **Returns**: Success message with filename or error message
-   **Features**:
    -   Handles Markdown headers (# to ####) with appropriate formatting
    -   Removes bold asterisks from headers
    -   Applies proper font sizes based on header levels
    -   Maintains paragraph spacing