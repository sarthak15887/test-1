from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
import uuid
from datetime import datetime

from app.core.config import get_settings
from app.services.llm import LLMService

settings = get_settings()


class AgentState(TypedDict):
    """State for agent execution graph."""
    messages: List[BaseMessage]
    context: Dict[str, Any]
    hypothesis: Optional[str]
    research_plan: Optional[List[str]]
    findings: List[Dict[str, Any]]
    current_step: int
    max_steps: int
    errors: List[str]


class ResearchAgent:
    """Base research agent with LangGraph orchestration."""
    
    def __init__(self, llm_service: LLMService, agent_type: str = "general"):
        self.llm_service = llm_service
        self.agent_type = agent_type
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the agent execution graph."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze", self.analyze_request)
        workflow.add_node("plan", self.create_research_plan)
        workflow.add_node("execute", self.execute_research_step)
        workflow.add_node("synthesize", self.synthesize_findings)
        workflow.add_node("verify", self.verify_results)
        
        # Set entry point
        workflow.set_entry_point("analyze")
        
        # Define edges
        workflow.add_conditional_edges(
            "analyze",
            self.should_plan,
            {
                "plan": "plan",
                "end": END
            }
        )
        
        workflow.add_edge("plan", "execute")
        
        workflow.add_conditional_edges(
            "execute",
            self.should_continue,
            {
                "continue": "execute",
                "synthesize": "synthesize"
            }
        )
        
        workflow.add_edge("synthesize", "verify")
        
        workflow.add_conditional_edges(
            "verify",
            self.should_accept,
            {
                "accept": END,
                "revise": "execute"
            }
        )
        
        return workflow.compile()
    
    def analyze_request(self, state: AgentState) -> AgentState:
        """Analyze the user's research request."""
        system_prompt = f"""You are a {self.agent_type} research assistant. 
        Analyze the user's request and determine the key research questions, 
        required information, and potential approaches."""
        
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = self.llm_service.generate(messages, temperature=0.3)
        
        state["context"]["analysis"] = response.content
        state["current_step"] += 1
        
        return state
    
    def should_plan(self, state: AgentState) -> str:
        """Determine if planning is needed."""
        if state["current_step"] >= state["max_steps"]:
            return "end"
        return "plan"
    
    def create_research_plan(self, state: AgentState) -> AgentState:
        """Create a step-by-step research plan."""
        system_prompt = """Create a detailed research plan with specific steps.
        Each step should be actionable and build upon previous findings.
        Format as a numbered list."""
        
        analysis = state["context"].get("analysis", "")
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Based on this analysis, create a research plan:\n{analysis}")
        ]
        
        response = self.llm_service.generate(messages, temperature=0.5)
        
        # Parse plan into steps
        plan_steps = [step.strip() for step in response.content.split('\n') if step.strip()]
        state["research_plan"] = plan_steps
        state["current_step"] += 1
        
        return state
    
    def execute_research_step(self, state: AgentState) -> AgentState:
        """Execute a single research step."""
        plan = state.get("research_plan", [])
        current_idx = state["current_step"] - 2  # Adjust for previous steps
        
        if current_idx >= len(plan):
            return state
        
        current_task = plan[current_idx]
        
        system_prompt = f"""Execute this research task: {current_task}
        Gather relevant information, analyze data, and document findings.
        Be thorough and cite sources when applicable."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Previous findings: {state['findings']}")
        ]
        
        response = self.llm_service.generate(messages, temperature=0.7)
        
        # Store findings
        finding = {
            "step": current_idx + 1,
            "task": current_task,
            "content": response.content,
            "timestamp": datetime.utcnow().isoformat()
        }
        state["findings"].append(finding)
        state["current_step"] += 1
        
        return state
    
    def should_continue(self, state: AgentState) -> str:
        """Determine if more research steps are needed."""
        plan = state.get("research_plan", [])
        current_idx = state["current_step"] - 2
        
        if current_idx < len(plan) and state["current_step"] < state["max_steps"]:
            return "continue"
        return "synthesize"
    
    def synthesize_findings(self, state: AgentState) -> AgentState:
        """Synthesize all research findings into conclusions."""
        system_prompt = """Synthesize all research findings into coherent conclusions.
        Identify patterns, contradictions, and key insights.
        Formulate evidence-based conclusions."""
        
        findings_text = "\n\n".join([f["content"] for f in state["findings"]])
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Synthesize these findings:\n{findings_text}")
        ]
        
        response = self.llm_service.generate(messages, temperature=0.3)
        state["context"]["synthesis"] = response.content
        state["current_step"] += 1
        
        return state
    
    def verify_results(self, state: AgentState) -> AgentState:
        """Verify the quality and accuracy of results."""
        system_prompt = """Critically evaluate the research results.
        Check for logical consistency, evidence quality, and potential biases.
        Identify any gaps or areas needing further investigation."""
        
        synthesis = state["context"].get("synthesis", "")
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Evaluate this synthesis:\n{synthesis}")
        ]
        
        response = self.llm_service.generate(messages, temperature=0.2)
        state["context"]["verification"] = response.content
        state["current_step"] += 1
        
        return state
    
    def should_accept(self, state: AgentState) -> str:
        """Determine if results are acceptable or need revision."""
        verification = state["context"].get("verification", "")
        
        # Simple heuristic - in production, use LLM to decide
        if "critical error" in verification.lower() or "major gap" in verification.lower():
            return "revise"
        return "accept"
    
    async def run(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run the agent with the given query."""
        initial_state: AgentState = {
            "messages": [HumanMessage(content=query)],
            "context": context or {},
            "hypothesis": None,
            "research_plan": None,
            "findings": [],
            "current_step": 0,
            "max_steps": settings.MAX_AGENT_ITERATIONS,
            "errors": []
        }
        
        try:
            result = await self.graph.ainvoke(initial_state)
            return {
                "success": True,
                "result": result,
                "summary": result["context"].get("synthesis", ""),
                "findings": result["findings"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "result": None
            }


class LiteratureReviewAgent(ResearchAgent):
    """Specialized agent for literature review tasks."""
    
    def __init__(self, llm_service: LLMService):
        super().__init__(llm_service, agent_type="literature_review")


class HypothesisGenerationAgent(ResearchAgent):
    """Specialized agent for generating research hypotheses."""
    
    def __init__(self, llm_service: LLMService):
        super().__init__(llm_service, agent_type="hypothesis_generation")


class ExperimentalDesignAgent(ResearchAgent):
    """Specialized agent for designing experiments."""
    
    def __init__(self, llm_service: LLMService):
        super().__init__(llm_service, agent_type="experimental_design")
