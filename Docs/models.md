# Models Module Documentation

The `models.py` module defines data structures used throughout the research automation workflow. It contains type definitions that facilitate data validation, structured I/O, and state management.

## Core Data Structures

### ResearchState

A `TypedDict` that represents the complete state of the research workflow.

-   **Type**: `TypedDict`
-   **Fields**:
    -   `company`: `str` - The company being researched
    -   `company_keywords`: `str` - Keywords related to the company for focused searching
    -   `exclude_keywords`: `str` - Keywords to exclude from search results
    -   `report`: `str` - The generated markdown report
    -   `documents`: `Dict[str, Dict[Union[str, int], Union[str, float]]]` - Raw documents retrieved during research, indexed by URL
    -   `RAG_docs`: `Dict[str, Dict[Union[str, int], Union[str, float]]]` - Documents processed for RAG (Retrieval Augmented Generation)
    -   `messages`: `Annotated[List[AnyMessage], ...]` - List of conversation messages
    -   `iteration`: `int` - Current iteration count in the research process

### Citation

A Pydantic model for representing source citations in the final report.

-   **Type**: `BaseModel`
-   **Fields**:
    -   `source_id`: `str` - Source URL for citation
    -   `quote`: `str` - Verbatim quote from source

### QuotedAnswer

A Pydantic model for structured report output, including citations.

-   **Type**: `BaseModel`
-   **Fields**:
    -   `answer`: `str` - Full report content in markdown format
    -   `citations`: `List[Citation]` - List of source citations used in the report

## Search-Related Models

### TavilyQuery

A Pydantic model representing a single search query.

-   **Type**: `BaseModel`
-   **Fields**:
    -   `query`: `str` - Search query
    -   `topic`: `str` - Search type, either "general" or "news"
    -   `days`: `int` - Days back for news search

### TavilySearchInput

A Pydantic model for executing multiple searches in parallel.

-   **Type**: `BaseModel`
-   **Fields**:
    -   `sub_queries`: `List[TavilyQuery]` - List of search queries to execute in parallel

### TavilyExtractInput

A Pydantic model for specifying URLs to extract content from.

-   **Type**: `BaseModel`
-   **Fields**:
    -   `urls`: `List[str]` - List of URLs to extract content from, example: ["https://example.com/news", "https://example.com/press"]

## Dependencies

-   `typing`: For type annotations (TypedDict, List, Annotated, Union, Dict)
-   `pydantic`: For data validation and schema definitions (BaseModel, Field)
-   `langchain_core.messages`: For message type definitions (AnyMessage)