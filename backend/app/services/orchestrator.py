"""
Orchestrator Service

Main coordinator for agent execution. Manages:
- Parallel agent execution (asyncio.gather)
- Sequential agent chains
- Result aggregation
- Progress tracking
- Error handling and graceful degradation
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Agent execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class ExecutionMode(str, Enum):
    """Agent execution mode"""
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"


class Phase:
    """Represents a phase in the orchestration plan"""
    def __init__(
        self,
        phase_id: int,
        name: str,
        agents: List[Dict[str, Any]],
        execution_mode: ExecutionMode = ExecutionMode.PARALLEL,
        timeout: Optional[int] = None
    ):
        self.phase_id = phase_id
        self.name = name
        self.agents = agents
        self.execution_mode = execution_mode
        self.timeout = timeout or 120  # Default 2 minutes
        self.status = AgentStatus.PENDING
        self.results: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert phase to dictionary"""
        return {
            "phase_id": self.phase_id,
            "name": self.name,
            "agents": self.agents,
            "execution_mode": self.execution_mode.value,
            "timeout": self.timeout,
            "status": self.status.value,
            "results": self.results,
            "errors": self.errors,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class OrchestratorService:
    """
    Main orchestrator for coordinating agent execution.

    Capabilities:
    - Execute agents in parallel (using asyncio.gather)
    - Execute agents sequentially with dependencies
    - Track progress and status
    - Aggregate results
    - Handle errors gracefully
    """

    def __init__(self):
        self.active_jobs: Dict[str, Dict[str, Any]] = {}

    async def execute_analysis(
        self,
        analysis_type: str,
        target: str,
        context: Optional[Dict[str, Any]] = None,
        simulate_failures: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Execute a complete analysis with multiple agents.

        Args:
            analysis_type: Type of analysis (company, market, competitive, etc.)
            target: Target of analysis (company name, industry, etc.)
            context: Additional context (user preferences, filters, etc.)
            simulate_failures: List of agent types to simulate failure (for testing)

        Returns:
            Aggregated results from all agents
        """
        job_id = str(uuid.uuid4())

        # Create execution plan based on analysis type
        plan = self._create_execution_plan(analysis_type, target, context)

        # Feature #161: Mark agents for simulated failure
        if simulate_failures:
            for phase in plan:
                for agent_config in phase.agents:
                    if agent_config["type"] in simulate_failures:
                        agent_config["simulate_error"] = True
                        agent_config["error_message"] = f"Simulated failure for testing: {agent_config['type']}"

        # Store job info
        self.active_jobs[job_id] = {
            "job_id": job_id,
            "analysis_type": analysis_type,
            "target": target,
            "plan": plan,
            "status": AgentStatus.RUNNING,
            "current_phase": None,
            "results": {},
            "created_at": datetime.utcnow(),
            "progress_percent": 0
        }

        try:
            # Execute all phases
            all_results = {}
            total_phases = len(plan)

            for phase_idx, phase in enumerate(plan):
                self.active_jobs[job_id]["current_phase"] = phase.name
                self.active_jobs[job_id]["progress_percent"] = int((phase_idx / total_phases) * 100)

                logger.info(f"[{job_id}] Starting phase {phase.phase_id}: {phase.name}")
                phase.started_at = datetime.utcnow()
                phase.status = AgentStatus.RUNNING

                # Execute phase (parallel or sequential)
                if phase.execution_mode == ExecutionMode.PARALLEL:
                    phase_results = await self._execute_phase_parallel(phase, all_results)
                else:
                    phase_results = await self._execute_phase_sequential(phase, all_results)

                # Store results
                phase.results = phase_results
                phase.completed_at = datetime.utcnow()
                phase.status = AgentStatus.COMPLETED

                # Merge into all_results
                all_results.update(phase_results)

                logger.info(f"[{job_id}] Completed phase {phase.phase_id}: {phase.name}")

            # Mark job as completed
            self.active_jobs[job_id]["status"] = AgentStatus.COMPLETED
            self.active_jobs[job_id]["progress_percent"] = 100
            self.active_jobs[job_id]["results"] = all_results
            self.active_jobs[job_id]["completed_at"] = datetime.utcnow()

            # Feature #161: Collect all errors from all phases
            all_errors = []
            failed_agents = []
            successful_agents = []

            for phase in plan:
                if phase.errors:
                    all_errors.extend(phase.errors)
                # Count failed/successful agents
                for agent_config in phase.agents:
                    agent_type = agent_config["type"]
                    agent_result = phase.results.get(agent_type, {})
                    if isinstance(agent_result, dict) and agent_result.get("status") == "error":
                        failed_agents.append(agent_type)
                    else:
                        successful_agents.append(agent_type)

            return {
                "job_id": job_id,
                "status": "completed",
                "results": all_results,
                "execution_plan": [phase.to_dict() for phase in plan],
                "summary": {
                    "total_agents": len(successful_agents) + len(failed_agents),
                    "successful_agents": len(successful_agents),
                    "failed_agents": len(failed_agents),
                    "success_rate": (len(successful_agents) / (len(successful_agents) + len(failed_agents)) * 100) if (len(successful_agents) + len(failed_agents)) > 0 else 0,
                    "errors": all_errors,
                    "failed_agent_list": failed_agents,
                    "successful_agent_list": successful_agents
                }
            }

        except Exception as e:
            logger.error(f"[{job_id}] Orchestration failed: {str(e)}")
            self.active_jobs[job_id]["status"] = AgentStatus.ERROR
            self.active_jobs[job_id]["error"] = str(e)

            raise

    async def _execute_phase_parallel(
        self,
        phase: Phase,
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute all agents in a phase in parallel using asyncio.gather.

        Args:
            phase: Phase to execute
            previous_results: Results from previous phases

        Returns:
            Combined results from all agents in phase
        """
        logger.info(f"Executing phase {phase.name} in PARALLEL mode with {len(phase.agents)} agents")

        # Create tasks for all agents
        tasks = []
        for agent_config in phase.agents:
            task = self._execute_agent(
                agent_type=agent_config["type"],
                agent_config=agent_config,
                context=previous_results
            )
            tasks.append(task)

        # Execute all tasks in parallel
        try:
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error in parallel execution: {str(e)}")
            raise

        # Combine results
        combined_results = {}
        for i, (agent_config, result) in enumerate(zip(phase.agents, results_list)):
            agent_type = agent_config["type"]

            if isinstance(result, Exception):
                logger.error(f"Agent {agent_type} failed: {str(result)}")
                phase.errors.append(f"{agent_type}: {str(result)}")
                combined_results[agent_type] = {"error": str(result), "status": "error"}
            else:
                combined_results[agent_type] = result
                logger.info(f"Agent {agent_type} completed successfully")

        return combined_results

    async def _execute_phase_sequential(
        self,
        phase: Phase,
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute agents in a phase sequentially (one after another).

        Args:
            phase: Phase to execute
            previous_results: Results from previous phases

        Returns:
            Combined results from all agents in phase
        """
        logger.info(f"Executing phase {phase.name} in SEQUENTIAL mode with {len(phase.agents)} agents")

        combined_results = {}
        cumulative_context = {**previous_results}

        for agent_config in phase.agents:
            agent_type = agent_config["type"]

            try:
                result = await self._execute_agent(
                    agent_type=agent_type,
                    agent_config=agent_config,
                    context=cumulative_context
                )
                combined_results[agent_type] = result

                # Add result to cumulative context for next agent
                cumulative_context[agent_type] = result

                logger.info(f"Agent {agent_type} completed successfully (sequential)")

            except Exception as e:
                logger.error(f"Agent {agent_type} failed: {str(e)}")
                phase.errors.append(f"{agent_type}: {str(e)}")
                combined_results[agent_type] = {"error": str(e), "status": "error"}

                # Continue with next agent (graceful degradation)

        return combined_results

    async def _execute_agent(
        self,
        agent_type: str,
        agent_config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single agent.

        Args:
            agent_type: Type of agent to execute
            agent_config: Configuration for the agent
            context: Context from previous agents

        Returns:
            Agent execution result
        """
        logger.info(f"Executing agent: {agent_type}")

        # Feature #161: Simulate agent failure for testing
        if agent_config.get("simulate_error"):
            error_msg = agent_config.get("error_message", "Simulated agent failure")
            logger.error(f"Agent {agent_type} simulating failure: {error_msg}")
            raise Exception(error_msg)

        # Simulate agent execution with delay
        # In real implementation, this would call actual agent services
        await asyncio.sleep(0.5 + (hash(agent_type) % 10) / 10)  # 0.5-1.4s variability

        # Mock result based on agent type
        if agent_type == "company_profile":
            return {
                "company_name": agent_config.get("target", "Unknown"),
                "status": "active",
                "industry": "Manufacturing",
                "employees": "50-100",
                "founded": 2010,
                "execution_time_ms": 850
            }
        elif agent_type == "financial_analysis":
            return {
                "revenue": 10500000,
                "revenue_growth": 15.5,
                "profit_margin": 12.3,
                "debt_ratio": 0.45,
                "execution_time_ms": 1200
            }
        elif agent_type == "digital_presence":
            return {
                "website": "https://example.com",
                "social_media": ["linkedin", "facebook"],
                "online_reviews": 4.2,
                "execution_time_ms": 650
            }
        elif agent_type == "competitor_mapping":
            return {
                "competitors_found": 5,
                "direct_competitors": 3,
                "indirect_competitors": 2,
                "execution_time_ms": 950
            }
        elif agent_type == "fact_checker":
            fact_checker_input = {k: v for k, v in context.items() if k != "fact_checker"}
            return {
                "verified_facts": len(fact_checker_input),
                "confidence_score": 0.85,
                "conflicts_detected": 0,
                "execution_time_ms": 450
            }
        elif agent_type == "insight_generator":
            return {
                "insights_generated": 8,
                "opportunities": 3,
                "risks": 2,
                "recommendations": 5,
                "execution_time_ms": 720
            }
        elif agent_type == "report_composer":
            return {
                "sections": 6,
                "total_pages": 12,
                "format": "comprehensive",
                "execution_time_ms": 340
            }
        else:
            return {
                "agent_type": agent_type,
                "status": "completed",
                "execution_time_ms": 500
            }

    def _create_execution_plan(
        self,
        analysis_type: str,
        target: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Phase]:
        """
        Create an execution plan based on analysis type.

        Args:
            analysis_type: Type of analysis
            target: Target entity
            context: Additional context

        Returns:
            List of phases to execute
        """
        if analysis_type == "comprehensive":
            # Multi-phase comprehensive analysis
            return [
                Phase(
                    phase_id=1,
                    name="data_collection",
                    execution_mode=ExecutionMode.PARALLEL,
                    agents=[
                        {"type": "company_profile", "target": target, "priority": "high"},
                        {"type": "financial_analysis", "target": target, "priority": "high"},
                        {"type": "digital_presence", "target": target, "priority": "medium"},
                    ],
                    timeout=120
                ),
                Phase(
                    phase_id=2,
                    name="enrichment",
                    execution_mode=ExecutionMode.PARALLEL,
                    agents=[
                        {"type": "competitor_mapping", "industry": "manufacturing", "priority": "medium"},
                    ],
                    timeout=90
                ),
                Phase(
                    phase_id=3,
                    name="analysis",
                    execution_mode=ExecutionMode.PARALLEL,
                    agents=[
                        {"type": "fact_checker", "priority": "high"},
                        {"type": "insight_generator", "priority": "high"},
                    ],
                    timeout=60
                ),
                Phase(
                    phase_id=4,
                    name="synthesis",
                    execution_mode=ExecutionMode.SEQUENTIAL,
                    agents=[
                        {"type": "report_composer", "format": "comprehensive", "priority": "high"},
                    ],
                    timeout=30
                ),
            ]
        elif analysis_type == "company":
            # Simple company analysis
            return [
                Phase(
                    phase_id=1,
                    name="company_data",
                    execution_mode=ExecutionMode.PARALLEL,
                    agents=[
                        {"type": "company_profile", "target": target},
                        {"type": "financial_analysis", "target": target},
                    ]
                )
            ]
        else:
            # Default simple plan
            return [
                Phase(
                    phase_id=1,
                    name="default_analysis",
                    execution_mode=ExecutionMode.PARALLEL,
                    agents=[
                        {"type": "company_profile", "target": target},
                    ]
                )
            ]

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a running or completed job"""
        return self.active_jobs.get(job_id)


# Singleton instance
orchestrator_service = OrchestratorService()
