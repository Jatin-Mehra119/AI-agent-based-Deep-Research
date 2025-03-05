from typing import TypedDict, List, Annotated, Union, Dict
from pydantic import BaseModel, Field
from langchain_core.messages import AnyMessage

# Define the state of research as a TypedDict for our workflow
class ResearchState(TypedDict):
    company: str
    company_keywords: str
    exclude_keywords: str
    report: str
    documents: Dict[str, Dict[Union[str, int], Union[str, float]]]
    RAG_docs: Dict[str, Dict[Union[str, int], Union[str, float]]]
    messages: Annotated[List[AnyMessage], ...]  # list of messages
    iteration: int

# Citation model for source referencing in the report
class Citation(BaseModel):
    source_id: str = Field(..., description="Source URL for citation")
    quote: str = Field(..., description="Verbatim quote from source")

# Structured answer model for report generation
class QuotedAnswer(BaseModel):
    answer: str = Field(..., description="Full report content in markdown format")
    citations: List[Citation] = Field(..., description="List of source citations")

# Model for a single search query
class TavilyQuery(BaseModel):
    query: str = Field(..., description="Search query")
    topic: str = Field(..., description="Search type: 'general' or 'news'")
    days: int = Field(..., description="Days back for news search")

# Input schema for executing multiple search queries in parallel
class TavilySearchInput(BaseModel):
    sub_queries: List[TavilyQuery] = Field(..., description="List of search queries to execute in parallel")

# Input schema for URL content extraction
class TavilyExtractInput(BaseModel):
    urls: List[str] = Field(..., description="List of URLs to extract content from", example=["https://example.com/news", "https://example.com/press"])