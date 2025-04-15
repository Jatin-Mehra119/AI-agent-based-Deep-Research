from langgraph.graph import StateGraph, END
from modules.models import ResearchState
from modules.workflow_nodes import research_model, tool_node, select_and_process, write_report, generate_pdf, should_continue

# Set up the state graph for the workflow.
# This defines the sequence and logic of the research automation pipeline.

# Initialize the workflow with the ResearchState data model.
workflow = StateGraph(ResearchState)

# Add nodes to the workflow graph.
# Each node represents a step in the research process.
workflow.add_node("research", research_model)      # Node to generate research prompts and tool calls.
workflow.add_node("tools", tool_node)              # Node to execute tools (e.g., search).
workflow.add_node("curate", select_and_process)    # Node to curate and process relevant documents.
workflow.add_node("write", write_report)           # Node to generate the markdown report.
workflow.add_node("publish", generate_pdf)         # Node to convert the report to PDF.

# Set the entry point of the workflow (where execution starts).
workflow.set_entry_point("research")

# Add conditional and sequential edges to define workflow transitions.
# After 'research', decide whether to use tools again or move to curation.
workflow.add_conditional_edges("research", should_continue, {"tools": "tools", "curate": "curate"})
workflow.add_edge("tools", "research")     # After tools, loop back to research for further processing.
workflow.add_edge("curate", "write")       # After curation, proceed to report writing.
workflow.add_edge("write", "publish")      # After writing, proceed to publishing (PDF generation).
workflow.add_edge("publish", END)          # End the workflow after publishing.

# Compile the workflow graph into an executable app.
app = workflow.compile()
