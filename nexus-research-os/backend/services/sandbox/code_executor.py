"""
Code Sandbox Service
Provides isolated execution environment for user code using Docker
"""
import docker
import json
import tempfile
import os
import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging
import uuid

logger = logging.getLogger(__name__)

@dataclass
class ExecutionResult:
    success: bool
    output: str
    error: str
    exit_code: int
    execution_time: float
    memory_used: int

class CodeSandboxService:
    def __init__(self):
        self.client = docker.from_env()
        self.active_containers: Dict[str, Any] = {}
        
    async def execute_code(
        self, 
        code: str, 
        language: str = "python",
        timeout: int = 30,
        memory_limit: str = "512m",
        packages: List[str] = None
    ) -> ExecutionResult:
        """Execute code in an isolated Docker container"""
        
        container_id = f"sandbox-{uuid.uuid4().hex[:8]}"
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Create temporary file with code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
                
            # Prepare Docker run configuration
            image = "python:3.11-slim"
            command = f"python /app/code.py"
            
            # Install additional packages if requested
            if packages:
                install_cmd = " && ".join([f"pip install {pkg}" for pkg in packages])
                command = f"bash -c '{install_cmd} && python /app/code.py'"
                
            # Run container with resource limits
            container = self.client.containers.run(
                image=image,
                command=command,
                volumes={temp_file: {'bind': '/app/code.py', 'mode': 'ro'}},
                network_disabled=True,  # No network access for security
                mem_limit=memory_limit,
                cpu_quota=50000,  # 50% of one CPU
                pids_limit=50,  # Limit number of processes
                remove=True,  # Auto-remove after execution
                name=container_id,
                detach=True,
                stdout=True,
                stderr=True
            )
            
            self.active_containers[container_id] = container
            
            # Wait for completion with timeout
            try:
                result = container.wait(timeout=timeout)
                exit_code = result.get('StatusCode', -1)
            except Exception as e:
                # Timeout occurred
                container.kill()
                return ExecutionResult(
                    success=False,
                    output="",
                    error=f"Execution timeout after {timeout} seconds",
                    exit_code=-1,
                    execution_time=timeout,
                    memory_used=0
                )
                
            # Get logs
            logs = container.logs().decode('utf-8')
            output_lines = logs.split('\n')
            
            # Separate stdout and stderr (simplified approach)
            output = '\n'.join([line for line in output_lines if not line.startswith('Traceback')])
            error = '\n'.join([line for line in output_lines if line.startswith('Traceback') or 'Error' in line])
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            # Get memory usage (approximate)
            stats = container.stats(stream=False)
            memory_used = stats['memory_stats'].get('usage', 0)
            
            return ExecutionResult(
                success=(exit_code == 0),
                output=output.strip(),
                error=error.strip() if error else "",
                exit_code=exit_code,
                execution_time=execution_time,
                memory_used=memory_used
            )
            
        except Exception as e:
            logger.error(f"Sandbox execution error: {e}")
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                exit_code=-1,
                execution_time=0,
                memory_used=0
            )
        finally:
            # Cleanup temp file
            try:
                os.unlink(temp_file)
            except:
                pass
                
            # Remove from active containers
            self.active_containers.pop(container_id, None)
            
    async def execute_notebook_cell(
        self, 
        code: str, 
        context: Dict[str, Any] = None
    ) -> ExecutionResult:
        """Execute a Jupyter notebook-style cell with persistent context"""
        # For now, wrap in a simple execution with context injection
        # In production, this would use a real Jupyter kernel
        
        context_setup = ""
        if context:
            for key, value in context.items():
                context_setup += f"{key} = {json.dumps(value)}\n"
                
        full_code = context_setup + code
        return await self.execute_code(full_code)
        
    def stop_container(self, container_id: str):
        """Stop a running container"""
        if container_id in self.active_containers:
            try:
                container = self.active_containers[container_id]
                container.stop()
                del self.active_containers[container_id]
                logger.info(f"Stopped container {container_id}")
            except Exception as e:
                logger.error(f"Error stopping container: {e}")
                
    def list_active_containers(self) -> List[str]:
        """List all active sandbox containers"""
        return list(self.active_containers.keys())
        
    def cleanup_all(self):
        """Stop and remove all active containers"""
        for container_id in list(self.active_containers.keys()):
            self.stop_container(container_id)
        logger.info("Cleaned up all sandbox containers")

# Singleton instance
_sandbox_service = None

def get_code_sandbox_service() -> CodeSandboxService:
    global _sandbox_service
    if _sandbox_service is None:
        _sandbox_service = CodeSandboxService()
    return _sandbox_service
