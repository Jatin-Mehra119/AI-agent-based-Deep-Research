# Tools Module Documentation

The  tools.py  module provides utility tools for accessing external services like web search APIs. It's designed to work within a LangChain-compatible framework and integrates with Streamlit for error handling.

## Tools

### tavily_search

A LangChain tool that performs concurrent web searches using the Tavily search API.

-   **Decorator**:  `@tool("tavily_search", args_schema=TavilySearchInput)`
-   **Parameters**:
    -   sub_queries: A list of  TavilyQuery  objects containing search parameters
-   **Returns**: A list of search results combined from all queries
-   **Features**:
    -   Executes multiple search queries in parallel using  asyncio
    -   Includes current month/year in search queries for recency
    -   Configures search with topic and date range filtering
    -   Limits results to 10 per query

### tavily_extract

A utility function for extracting content from URLs using the Tavily API.

-   **Parameters**:
    -   urls: A list of URLs to extract content from
-   **Returns**: Extracted content from the provided URLs
-   **Implementation Details**:
    -   Handles errors gracefully with error logging
    -   Returns an empty results list on error

### Inner Functions

#### perform_search(query: TavilyQuery)

Helper function that executes a single search query.

-   **Parameters**:
    -   itm: A  TavilyQuery  object containing search parameters
-   **Returns**: A list of search results or an empty list on error
-   **Implementation Details**:
    -   Appends current month/year to search queries
    -   Limits results to 10 per query
    -   Uses topic and days parameters for filtering
    -   Includes error handling with logging

## Global Variables

-   **tavily_client**: An instance of  AsyncTavilyClient  for making API calls
-   **tools**: A list containing all available tools (currently only  tavily_search)
-   **tools_by_name**: A dictionary mapping tool names to their implementations for easy lookup

## Dependencies

-   **AsyncTavilyClient**: For making asynchronous API calls to Tavily
-   **TavilySearchInput**,  **TavilyQuery**: Schema classes for validating input
-   **asyncio**: For parallel execution of search queries
-   **langchain_core.tools**: For the  `@tool`  decorator