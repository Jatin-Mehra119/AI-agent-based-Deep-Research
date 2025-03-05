# Models Module Documentation

The `models.py` module defines data structures used throughout the research automation workflow. It contains type definitions that facilitate data validation, structured I/O, and state management.

## Core Data Structures

### ResearchState

A `TypedDict` that represents the complete state of the research workflow.

-   **Type**: `TypedDict`
-   **Fields**:
    -   `company`: `str` - The company being researched
    -   `keywords`: `str` - Keywords relevant to the company for search filtering
    -   `exclude_keywords`: `str` - Keywords to exclude from search results
    -   `report`: `str` - The generated markdown report
    -   `collected_documents`: `Dict[str, Dict[Union[str, int], Union[str, float]]]` - All collected documents indexed by URL
    -   `curated_documents`: `Dict[str, Dict[Union[str, int], Union[str, float]]]` - Curated subset of documents for report generation
    -   `conversation_history`: `List[AnyMessage]` - Conversation history between system components
    -   `iteration_count`: `int` - Current iteration count of the research loop

### Citation

A Pydantic model for representing source citations in the final report.

-   **Type**: `BaseModel`
-   **Fields**:
    -   `url`: `str` - URL of the source document
    -   `quoted_text`: `str` - Verbatim text quoted from the source

### QuotedAnswer

A Pydantic model for structured report output, including citations.

-   **Type**: `BaseModel`
-   **Fields**:
    -   `content`: `str` - Complete markdown report content
    -   `citations`: `List[Citation]` - List of citations used in the report

## Search-Related Models

### TavilyQuery

A Pydantic model representing a single search query.

-   **Type**: `BaseModel`
-   **Fields**:
    -   `query`: `str` - The search query text
    -   `search_type`: `str` - Search type, either "general" or "news"
    -   `time_range`: `int` - Time range for news searches in days

### TavilySearchInput

A Pydantic model for executing multiple searches in parallel.

-   **Type**: `BaseModel`
-   **Fields**:
    -   `queries`: `List[TavilyQuery]` - List of search queries to execute concurrently

### TavilyExtractInput

A Pydantic model for specifying URLs to extract content from.

-   **Type**: `BaseModel`
-   **Fields**:
    -   `urls`: `List[str]` - List of URLs to extract content from

## Dependencies

-   `typing`: For type annotations
-   `pydantic`: For data validation and schema definitions
-   `langchain_core.messages`: For message type definitions