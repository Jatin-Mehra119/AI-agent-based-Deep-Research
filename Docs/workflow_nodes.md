# Workflow Nodes Module Documentation

The  workflow_nodes.py module implements a research workflow as a series of modular nodes that process and transform research state. Each node performs a specific task in the research pipeline, from information gathering to report generation.

## Core Functions

### tool_node(state: ResearchState)

Executes tool calls, particularly web searches, and adds results to the document collection.

-   **Parameters**:
    -   workflow_nodes.py: The current research state
-   **Returns**: Updated state with new documents and messages
-   **Behavior**:
    -   Processes tool calls from the last message
    -   Executes Tavily web searches
    -   Adds new documents to the state while avoiding duplicates
    -   Increments the iteration counter

### research_model(state: ResearchState)

Performs research using the Groq LLM API with the current state context.

-   **Parameters**:
    -   workflow_nodes.py: The current research state
-   **Returns**: Updated state with new AI messages
-   **Behavior**:
    -   Creates a prompt including research target and keywords
    -   Uses llama-3.1-8b-instant model with appropriate tools
    -   Implements rate limiting using  `rate_limited_execute`

### should_continue(state: ResearchState) -> str

Determines the next workflow step based on the current state.

-   **Parameters**:
    -   workflow_nodes.py: The current research state
-   **Returns**:
    -   `"tools"`  if more tool calls should be executed
    -   `"curate"`  if it's time to process collected documents
-   **Decision Logic**:
    -   Returns "curate" after 3 iterations
    -   Returns "tools" if the last message contains tool calls

### select_and_process(state: ResearchState)

Curates and extracts content from collected documents.

-   **Parameters**:
    -   workflow_nodes.py: The current research state
-   **Returns**: Updated state with filtered documents
-   **Behavior**:
    -   Uses AI to identify most relevant documents
    -   Extracts full content from selected URLs using Tavily API
    -   Filters documents based on relevance to research target

### write_report(state: ResearchState)

Generates a structured markdown report based on collected information.

-   **Parameters**:
    -   workflow_nodes.py: The current research state
-   **Returns**: Updated state with generated report
-   **Behavior**:
    -   Creates a comprehensive report with predefined sections
    -   Includes citations from source documents
    -   Handles errors gracefully
    -   Uses structured output schema for consistent formatting

### generate_pdf(state: ResearchState)

Converts the markdown report to a PDF file.

-   **Parameters**:
    -   workflow_nodes.py: The current research state
-   **Returns**: Updated state with PDF generation message
-   **Behavior**:
    -   Creates a reports directory if it doesn't exist
    -   Generates a timestamped PDF filename
    -   Uses  `generate_pdf_from_md`  to create the PDF

## Report Structure

The generated reports follow a standardized format:

1.  Executive Summary
2.  Company Background
3.  Financial Overview
4.  Market & Competitive Landscape
5.  Recent News & Developments
6.  Future Outlook & Recommendations
7.  References

## Dependencies

-   **langchain_core**: For message types and tool handling
-   **langchain_groq**: For AI model interactions
-   **modules.models**: For custom data structures
-   **modules.rate_limiter**: For API rate limiting
-   **modules.pdf_utils**: For PDF generation
-   **modules.tools**: For search functionality
