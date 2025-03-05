import asyncio
import streamlit as st
from datetime import datetime
from modules.models import TavilySearchInput, TavilyQuery
from tavily import AsyncTavilyClient
from langchain_core.tools import tool

# Initialize the Tavily client
tavily_client = AsyncTavilyClient()

@tool("tavily_search", args_schema=TavilySearchInput, return_direct=True)
async def tavily_search(sub_queries):
    """
    Perform parallel web searches using the Tavily API.
    """
    async def perform_search(query: TavilyQuery):
        try:
            response = await tavily_client.search(
                query=f"{query.query} {datetime.now().strftime('%Y-%m')}",
                search_depth="advanced",
                topic=query.topic,
                max_results=5,
                include_answer=False,
                include_raw_content=True
            )
            return response.get('results', [])
        except Exception as e:
            st.error(f"Search error: {str(e)}")
            return []
    
    # Execute all search queries concurrently
    search_results = await asyncio.gather(*[perform_search(q) for q in sub_queries])
    
    # Flatten the results and remove duplicates
    unique_results = {}
    for result_group in search_results:
        for result in result_group:
            if result['url'] not in unique_results:
                unique_results[result['url']] = result
    
    return list(unique_results.values())

# Export the tools and a lookup dictionary for workflow nodes
tools = [tavily_search]
tools_by_name = {tool.name: tool for tool in tools}
