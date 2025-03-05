# Tools Module Documentation

The  tools.py  module provides utility tools for accessing external services like web search APIs. It's designed to work within a LangChain-compatible framework and integrates with Streamlit for error handling.

## Tools

### tavily_search

A LangChain tool that performs concurrent web searches using the Tavily search API.

-   **Decorator**:  `@tool("tavily_search", args_schema=TavilySearchInput, return_direct=True)`
-   **Parameters**:
    -   sub_queries: A list of  TavilyQuery  objects containing search parameters
-   **Returns**: A list of unique search results
-   **Features**:
    -   Executes multiple search queries in parallel using  asyncio
    -   Includes current month/year in search queries for recency
    -   Removes duplicate results based on URL
    -   Configures search with "advanced" depth and raw content inclusion
    -   Handles errors gracefully with Streamlit error displays

### Inner Functions

#### perform_search(query: TavilyQuery)

Helper function that executes a single search query.

-   **Parameters**:
    -   query: A  TavilyQuery  object containing search parameters
-   **Returns**: A list of search results or an empty list on error
-   **Implementation Details**:
    -   Appends current month/year to search queries
    -   Limits results to 5 per query
    -   Includes raw content but excludes Tavily's summarized answers

## Global Variables

-   **tavily_client**: An instance of  AsyncTavilyClient  for making API calls
-   **tools**: A list containing all available tools (currently only  tavily_search)
-   **tools_by_name**: A dictionary mapping tool names to their implementations for easy lookup

## Dependencies

-   **AsyncTavilyClient**: For making asynchronous API calls to Tavily
-   **TavilySearchInput**,  **TavilyQuery**: Schema classes for validating input
-   **streamlit**: For displaying errors in the UI
-   **langchain_core.tools**: For the  `@tool`  decorator