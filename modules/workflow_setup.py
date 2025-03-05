from langgraph.graph import StateGraph, END
from modules.models import ResearchState
from modules.workflow_nodes import research_model, tool_node, select_and_process, write_report, generate_pdf, should_continue

# Set up the state graph for the workflow
workflow = StateGraph(ResearchState)
workflow.add_node("research", research_model)
workflow.add_node("tools", tool_node)
workflow.add_node("curate", select_and_process)
workflow.add_node("write", write_report)
workflow.add_node("publish", generate_pdf)

workflow.set_entry_point("research")
workflow.add_conditional_edges("research", should_continue, {"tools": "tools", "curate": "curate"})
workflow.add_edge("tools", "research")  # Loop back to research after tool calls
workflow.add_edge("curate", "write")
workflow.add_edge("write", "publish")
workflow.add_edge("publish", END)

# Compile the workflow and export as 'app'
app = workflow.compile()
