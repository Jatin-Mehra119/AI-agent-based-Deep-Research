# Workflow Nodes Module Documentation

The `workflow_nodes.py` module defines the core functions that implement each node in the AI research workflow pipeline. Each node represents a distinct step in the research process, handling everything from information gathering to report generation and publishing.

## Node Functions

The workflow consists of six primary node functions, each implementing a specific phase of the research process:

1. **`research_model`**: Uses Google Generative AI (Gemini) to perform research
   - Builds a research prompt with company information and keywords
   - Initializes a Gemini model with appropriate tool bindings
   - Returns updated state with model's response messages
   - Includes error handling with Streamlit feedback

2. **`tool_node`**: Executes AI-requested tools (like search operations)
   - Processes tool calls made by the AI model
   - Invokes appropriate tools and collects new documents
   - Handles deduplication of documents based on URLs
   - Returns updated messages, documents, and iteration count

3. **`should_continue`**: Determines the next workflow step based on current state
   - Decision logic:
     - If max iterations reached (5) → curate
     - If model wants to use more tools → tools
     - If model indicates completion → curate
     - Default → tools

4. **`select_and_process`**: Analyzes and selects relevant documents
   - Filters collected documents to identify those most relevant
   - Considers company keywords and exclusion criteria
   - Extracts raw content from selected URLs using Tavily API
   - Returns updated state with selected documents and content

5. **`write_report`**: Generates a comprehensive markdown report
   - Uses Gemini model to create a detailed, well-formatted report
   - Includes citations and references to source documents
   - Uses structured output format (QuotedAnswer) for proper citations
   - Returns updated state with generated report

6. **`generate_pdf`**: Converts markdown report to PDF
   - Takes generated markdown report and converts to PDF document
   - Saves in the 'reports' directory with filename based on company name
   - Creates reports directory if it doesn't exist
   - Returns PDF generation status message

## Function Parameters and Return Values

All functions work with a `ResearchState` object that maintains the workflow state:

- **Input**: `state: ResearchState` - Current state including messages, documents, company info
- **Output**: Dictionary with updated state components (varies by function)

## Dependencies

The module relies on several key dependencies:

- **Google Generative AI**: For the Gemini language model
- **LangChain Core**: For message handling and tool integration
- **Tavily API**: For web search and content extraction
- **PDF Utils**: For markdown-to-PDF conversion
- **Streamlit**: For progress tracking and error reporting

## Workflow Integration

These node functions are integrated into a directed graph workflow in the `workflow_setup.py` module. The flow control is managed by the `should_continue` function, which determines routing between nodes based on the current state.
