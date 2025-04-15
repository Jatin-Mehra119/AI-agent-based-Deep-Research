"""
Models Module for AI Agent Research Pipeline

This module defines the data models used throughout the research workflow,
including state management, citation handling, and search query structures.
These Pydantic models ensure type safety and provide schema validation.
"""

from typing import TypedDict, List, Annotated, Union, Dict
from pydantic import BaseModel, Field
from langchain_core.messages import AnyMessage

# Define the state of research as a TypedDict for our workflow
class ResearchState(TypedDict):
    """
    Represents the complete state of a research workflow.
    
    This TypedDict maintains all necessary data throughout the research process,
    including the target company, search parameters, accumulated documents,
    and the current state of the report being generated.
    """
    company: str  # Target company name
    company_keywords: str  # Keywords related to the company for focused searching
    exclude_keywords: str  # Keywords to exclude from search results
    report: str  # Current state of the generated report
    documents: Dict[str, Dict[Union[str, int], Union[str, float]]]  # Raw documents retrieved during research
    RAG_docs: Dict[str, Dict[Union[str, int], Union[str, float]]]  # Documents processed for RAG (Retrieval Augmented Generation)
    messages: Annotated[List[AnyMessage], ...]  # List of conversation messages
    iteration: int  # Current iteration count in the research process

# Citation model for source referencing in the report
class Citation(BaseModel):
    """
    Represents a citation from a source document.
    
    Used to maintain provenance of information in the research report by
    tracking both the source URL and the specific quoted text.
    """
    source_id: str = Field(..., description="Source URL for citation")
    quote: str = Field(..., description="Verbatim quote from source")

# Structured answer model for report generation
class QuotedAnswer(BaseModel):
    """
    Represents a complete research report with source citations.
    
    Combines the full markdown-formatted answer content with a list of
    citations that provide attribution for information in the report.
    """
    answer: str = Field(..., description="Full report content in markdown format")
    citations: List[Citation] = Field(..., description="List of source citations")

# Model for a single search query
class TavilyQuery(BaseModel):
    """
    Represents a single search query for the Tavily search API.
    
    Defines parameters for an individual search request, including
    the query text, topic type, and time window for news searches.
    """
    query: str = Field(..., description="Search query")
    topic: str = Field(..., description="Search type: 'general' or 'news'")
    days: int = Field(..., description="Days back for news search")

# Input schema for executing multiple search queries in parallel
class TavilySearchInput(BaseModel):
    """
    Input structure for batch execution of multiple search queries.
    
    Enables parallel processing of multiple search queries to efficiently
    gather diverse information on a research topic.
    """
    sub_queries: List[TavilyQuery] = Field(..., description="List of search queries to execute in parallel")

# Input schema for URL content extraction
class TavilyExtractInput(BaseModel):
    """
    Input structure for batch URL content extraction.
    
    Used to extract and process content from multiple web pages
    for inclusion in the research process.
    """
    urls: List[str] = Field(..., description="List of URLs to extract content from", example=["https://example.com/news", "https://example.com/press"])