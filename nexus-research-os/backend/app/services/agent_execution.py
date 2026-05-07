"""
Agent Execution Service - Manages agent runs with real-time streaming.
"""
import asyncio
import uuid
from typing import Dict, Optional, AsyncGenerator
from datetime import datetime
from loguru import logger

from app.websocket_manager import manager
from app.services.llm_service import LLMService
from app.agents.chief_scientist import ChiefScientistAgent
from app.models.agent_run import AgentRun, RunStatus, RunStep


class AgentExecutionService:
    def __init__(self):
        self.llm_service = LLMService()
        self.active_runs: Dict[str, dict] = {}
    
    async def start_agent_run(
        self,
        user_id: str,
        project_id: str,
        task_description: str,
        agent_config: Optional[dict] = None
    ) -> AgentRun:
        """Start a new agent run and return the run object."""
        run_id = str(uuid.uuid4())
        
        # Create initial run record
        run = AgentRun(
            id=run_id,
            user_id=user_id,
            project_id=project_id,
            task_description=task_description,
            status=RunStatus.PENDING,
            config=agent_config or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Store active run metadata
        self.active_runs[run_id] = {
            "run": run,
            "task": asyncio.create_task(
                self._execute_agent_run(run, task_description)
            )
        }
        
        logger.info(f"Started agent run {run_id} for user {user_id}")
        return run
    
    async def _execute_agent_run(self, run: AgentRun, task: str):
        """Execute the agent workflow with real-time updates."""
        run_id = run.id
        
        try:
            # Update status to running
            run.status = RunStatus.RUNNING
            run.updated_at = datetime.utcnow()
            
            await manager.send_agent_update(run_id, "system", "running", {
                "message": "Agent execution started"
            })
            
            # Initialize chief scientist agent
            chief_agent = ChiefScientistAgent(self.llm_service)
            
            # Step 1: Plan the research approach
            await manager.send_agent_update(run_id, "chief_scientist", "planning", {
                "message": "Analyzing task and creating research plan"
            })
            
            plan = await chief_agent.plan(task)
            run.steps.append(RunStep(
                step_type="planning",
                agent_name="chief_scientist",
                output=plan,
                completed_at=datetime.utcnow()
            ))
            
            await manager.send_agent_update(run_id, "chief_scientist", "completed", {
                "message": "Research plan created",
                "plan": plan
            })
            
            # Step 2: Execute sub-tasks (simplified for now)
            await manager.send_agent_update(run_id, "chief_scientist", "executing", {
                "message": "Executing research tasks"
            })
            
            # Simulate multi-agent collaboration
            results = await chief_agent.execute(task, plan)
            
            run.steps.append(RunStep(
                step_type="execution",
                agent_name="chief_scientist",
                output=results,
                completed_at=datetime.utcnow()
            ))
            
            await manager.send_agent_update(run_id, "chief_scientist", "completed", {
                "message": "Research tasks completed",
                "results": results
            })
            
            # Complete the run
            run.status = RunStatus.COMPLETED
            run.result = results
            run.completed_at = datetime.utcnow()
            
            await manager.send_agent_update(run_id, "system", "completed", {
                "message": "Agent run completed successfully"
            })
            
        except Exception as e:
            logger.error(f"Agent run {run_id} failed: {str(e)}")
            run.status = RunStatus.FAILED
            run.error_message = str(e)
            
            await manager.send_agent_update(run_id, "system", "failed", {
                "message": f"Agent run failed: {str(e)}"
            })
        
        finally:
            run.updated_at = datetime.utcnow()
            if run_id in self.active_runs:
                del self.active_runs[run_id]
    
    async def stream_agent_run(self, run_id: str) -> AsyncGenerator[dict, None]:
        """Stream real-time updates for an agent run."""
        if run_id not in self.active_runs:
            yield {"type": "error", "message": "Run not found or completed"}
            return
        
        # This would be enhanced with a proper event queue
        yield {"type": "info", "message": "Connected to run stream"}
    
    def get_run_status(self, run_id: str) -> Optional[AgentRun]:
        """Get current status of a run."""
        if run_id in self.active_runs:
            return self.active_runs[run_id]["run"]
        return None
    
    def cancel_run(self, run_id: str) -> bool:
        """Cancel an active run."""
        if run_id in self.active_runs:
            task = self.active_runs[run_id]["task"]
            task.cancel()
            del self.active_runs[run_id]
            logger.info(f"Cancelled run {run_id}")
            return True
        return False


# Global instance
agent_execution_service = AgentExecutionService()
