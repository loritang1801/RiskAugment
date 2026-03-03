"""
Tool executor with error handling and timeout control.
"""

import logging
import time
from typing import Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executor for tools with error handling and timeout control."""
    
    def __init__(self, timeout_seconds: int = 30, max_workers: int = 4):
        """
        Initialize tool executor.
        
        Args:
            timeout_seconds: Timeout for each tool execution
            max_workers: Maximum number of worker threads
        """
        self.timeout_seconds = timeout_seconds
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.execution_logs = []
    
    def execute_tool(
        self,
        tool_name: str,
        tool_func: Callable,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute a tool with timeout and error handling.
        
        Args:
            tool_name: Name of the tool
            tool_func: Tool execution function
            **kwargs: Tool arguments
            
        Returns:
            Execution result with status, data, and metadata
        """
        start_time = time.time()
        
        try:
            logger.info(f"Executing tool: {tool_name}")
            
            # Execute with timeout
            future = self.executor.submit(tool_func, **kwargs)
            result = future.result(timeout=self.timeout_seconds)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            # Log execution
            log_entry = {
                'tool': tool_name,
                'status': result.get('status', 'unknown'),
                'execution_time_ms': execution_time,
                'timestamp': time.time()
            }
            self.execution_logs.append(log_entry)
            
            logger.info(f"Tool {tool_name} completed in {execution_time}ms")
            
            return {
                'status': result.get('status', 'success'),
                'data': result.get('data'),
                'tool': tool_name,
                'execution_time_ms': execution_time
            }
        
        except FuturesTimeoutError:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"Tool {tool_name} timed out after {execution_time}ms")
            
            log_entry = {
                'tool': tool_name,
                'status': 'timeout',
                'execution_time_ms': execution_time,
                'timestamp': time.time()
            }
            self.execution_logs.append(log_entry)
            
            return {
                'status': 'timeout',
                'error': f'Tool execution timed out after {self.timeout_seconds}s',
                'tool': tool_name,
                'execution_time_ms': execution_time
            }
        
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            
            log_entry = {
                'tool': tool_name,
                'status': 'error',
                'error': str(e),
                'execution_time_ms': execution_time,
                'timestamp': time.time()
            }
            self.execution_logs.append(log_entry)
            
            return {
                'status': 'error',
                'error': str(e),
                'tool': tool_name,
                'execution_time_ms': execution_time
            }
    
    def execute_tools_sequentially(
        self,
        tools: Dict[str, Callable],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute multiple tools sequentially.
        
        Args:
            tools: Dict of tool_name -> tool_func
            **kwargs: Arguments to pass to all tools
            
        Returns:
            Dict of tool_name -> execution_result
        """
        results = {}
        
        for tool_name, tool_func in tools.items():
            result = self.execute_tool(tool_name, tool_func, **kwargs)
            results[tool_name] = result
            
            # Continue even if a tool fails
            if result['status'] != 'success':
                logger.warning(f"Tool {tool_name} failed: {result.get('error', 'unknown error')}")
        
        return results
    
    def execute_tools_with_fallback(
        self,
        tools: Dict[str, Callable],
        fallback_func: Optional[Callable] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute tools with fallback support.
        
        Args:
            tools: Dict of tool_name -> tool_func
            fallback_func: Function to call if all tools fail
            **kwargs: Arguments to pass to tools
            
        Returns:
            Execution results
        """
        results = self.execute_tools_sequentially(tools, **kwargs)
        
        # Check if any tool succeeded
        any_success = any(r.get('status') == 'success' for r in results.values())
        
        if not any_success and fallback_func:
            logger.warning("All tools failed, executing fallback")
            fallback_result = self.execute_tool('fallback', fallback_func, **kwargs)
            results['fallback'] = fallback_result
        
        return results
    
    def get_execution_logs(self) -> list:
        """Get execution logs."""
        return self.execution_logs
    
    def clear_execution_logs(self) -> None:
        """Clear execution logs."""
        self.execution_logs = []
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary."""
        if not self.execution_logs:
            return {
                'total_executions': 0,
                'successful': 0,
                'failed': 0,
                'timeout': 0,
                'average_execution_time_ms': 0
            }
        
        total = len(self.execution_logs)
        successful = sum(1 for log in self.execution_logs if log['status'] == 'success')
        failed = sum(1 for log in self.execution_logs if log['status'] == 'error')
        timeout = sum(1 for log in self.execution_logs if log['status'] == 'timeout')
        avg_time = sum(log['execution_time_ms'] for log in self.execution_logs) / total
        
        return {
            'total_executions': total,
            'successful': successful,
            'failed': failed,
            'timeout': timeout,
            'average_execution_time_ms': int(avg_time)
        }
    
    def shutdown(self) -> None:
        """Shutdown executor."""
        self.executor.shutdown(wait=True)
