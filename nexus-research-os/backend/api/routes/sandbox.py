"""
Code Sandbox API Routes
Endpoints for secure code execution
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from backend.services.sandbox.code_executor import get_code_sandbox_service
from backend.auth.dependencies import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/api/v1/sandbox", tags=["sandbox"])

class CodeExecutionRequest(BaseModel):
    code: str
    language: str = "python"
    timeout: int = 30
    packages: Optional[List[str]] = None
    
@router.post("/execute")
async def execute_code(
    request: CodeExecutionRequest,
    current_user: User = Depends(get_current_user)
):
    """Execute code in isolated sandbox"""
    sandbox = get_code_sandbox_service()
    
    try:
        result = await sandbox.execute_code(
            code=request.code,
            language=request.language,
            timeout=request.timeout,
            packages=request.packages
        )
        
        return {
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "exit_code": result.exit_code,
            "execution_time": result.execution_time,
            "memory_used": result.memory_used
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")

@router.get("/containers")
async def list_active_containers(
    current_user: User = Depends(get_current_user)
):
    """List active sandbox containers"""
    sandbox = get_code_sandbox_service()
    
    containers = sandbox.list_active_containers()
    
    return {
        "active_containers": containers,
        "count": len(containers)
    }

@router.post("/containers/{container_id}/stop")
async def stop_container(
    container_id: str,
    current_user: User = Depends(get_current_user)
):
    """Stop a running container"""
    sandbox = get_code_sandbox_service()
    
    try:
        sandbox.stop_container(container_id)
        return {"message": f"Container {container_id} stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop container: {str(e)}")
