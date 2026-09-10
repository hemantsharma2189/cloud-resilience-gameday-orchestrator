from enum import Enum

from pydantic import BaseModel, Field


class FailureType(str, Enum):
    POD_CRASH = "pod_crash"
    CPU_STRESS = "cpu_stress"
    NETWORK_LATENCY = "network_latency"
    DEPENDENCY_FAILURE = "dependency_failure"


class Target(BaseModel):
    namespace: str = "default"
    deployment: str
    selector: str | None = None


class SuccessCriteria(BaseModel):
    max_recovery_seconds: int = Field(default=120, gt=0)
    minimum_availability_percent: float = Field(default=99.0, ge=0, le=100)
    maximum_error_rate_percent: float = Field(default=5.0, ge=0, le=100)


class GameDayScenario(BaseModel):
    name: str
    description: str
    failure_type: FailureType
    target: Target
    duration_seconds: int = Field(default=30, gt=0, le=600)
    dry_run: bool = True
    require_approval: bool = True
    success_criteria: SuccessCriteria = Field(default_factory=SuccessCriteria)


class GameDayResult(BaseModel):
    scenario_name: str
    status: str
    dry_run: bool
    recovery_seconds: float
    availability_percent: float
    error_rate_percent: float
    passed: bool
    observations: list[str] = Field(default_factory=list)
