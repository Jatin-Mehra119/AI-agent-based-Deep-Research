import asyncio
from datetime import datetime
from typing import List

from tavily import AsyncTavilyClient
from langchain_core.tools import tool
from modules.models import TavilySearchInput, TavilyQuery

# Initialize the Tavily client
tavily_client = AsyncTavilyClient()

@tool("tavily_search", args_schema=TavilySearchInput)
async def tavily_search(sub_queries: List[TavilyQuery]):
    """
    Perform searches for each sub-query using the Tavily search tool concurrently.
    """
    # Define a coroutine function to perform a single search with error handling
    async def perform_search(itm):
        try:
            # Add date to the query as we need the most recent results
            query_with_date = f"{itm.query} {datetime.now().strftime('%m-%Y')}"
            
            # Attempt to perform the search (using parameters from the original notebook)
            response = await tavily_client.search(
                query=query_with_date, 
                topic=itm.topic, 
                days=itm.days, 
                max_results=10
            )
            return response['results']
        except Exception as e:
            # Log error but don't stop workflow
            print(f"Error occurred during search for query '{itm.query}': {str(e)}")
            return []
    
    # Run all the search tasks in parallel
    search_tasks = [perform_search(itm) for itm in sub_queries]
    search_responses = await asyncio.gather(*search_tasks)
    
    # Combine the results from all the responses
    search_results = []
    for response in search_responses:
        search_results.extend(response)
    
    return search_results

# Define the extract function (separate from the tool)
async def tavily_extract(urls):
    """Extract raw content from urls to gather additional information."""
    try:
        response = await tavily_client.extract(urls=urls)
        return response
    except Exception as e:
        print(f"Error occurred during extract: {str(e)}")
        return {"results": []}

# Export the tools and a lookup dictionary for workflow nodes
tools = [tavily_search]
tools_by_name = {tool.name: tool for tool in tools}