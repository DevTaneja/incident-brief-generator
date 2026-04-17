"""Pydantic models for incident brief requests and responses."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


class IncidentRequest(BaseModel):
    """Request model for incident brief generation."""
    
    request_id: str = Field(
        ..., 
        description="Correlation ID to trace across systems",
        min_length=1,
        max_length=100
    )
    time_range: str = Field(
        ...,
        description="Time range for data retrieval (e.g., '1h', '30m', '24h')"
    )
    environment: str = Field(
        default="prod",
        description="Environment to query (prod, staging, dev)"
    )
    
    @validator('time_range')
    def validate_time_range(cls, v):
        """Validate time range format."""
        import re
        pattern = r'^(\d+)(m|h|d)$'
        if not re.match(pattern, v):
            raise ValueError('time_range must be format: <number>m/h/d (e.g., 30m, 2h, 1d)')
        return v
    
    @validator('environment')
    def validate_environment(cls, v):
        """Validate environment value."""
        allowed = ['prod', 'staging', 'dev']
        if v not in allowed:
            raise ValueError(f'environment must be one of: {allowed}')
        return v


class ErrorObservation(BaseModel):
    """Model for an error observed in logs."""
    
    timestamp: datetime
    error_message: str
    stack_trace: Optional[str] = None
    request_id: Optional[str] = None
    service: Optional[str] = None
    severity: str = "error"


class PerformanceInsight(BaseModel):
    """Model for performance insights."""
    
    metric_name: str
    average_value: float
    peak_value: float
    unit: str
    time_range: str
    anomaly_detected: bool = False


class TimelineEvent(BaseModel):
    """Model for timeline events."""
    
    timestamp: datetime
    event_type: str  # error, deploy, anomaly, etc.
    description: str
    source: str  # newrelic, splunk, jira


class RelatedIssue(BaseModel):
    """Model for related Jira issues."""
    
    issue_key: str
    summary: str
    status: str
    priority: str
    created_date: datetime
    url: str
    relevance_score: float = Field(ge=0, le=1)


class IncidentBrief(BaseModel):
    """Response model for incident brief."""
    
    request_id: str
    generated_at: datetime
    environment: str
    time_range: str
    
    # Sections
    summary: str
    errors_observed: List[ErrorObservation]
    performance_insights: List[PerformanceInsight]
    timeline: List[TimelineEvent]
    related_jira_issues: List[RelatedIssue]
    suggested_next_steps: List[str]
    
    # Metadata
    data_sources_used: List[str]
    is_inference: bool = Field(
        default=False,
        description="True if LLM inferred some insights, False if purely factual"
    )


class ReportDownloadRequest(BaseModel):
    """Request model for report download."""
    
    brief: IncidentBrief
    format: str = Field(default="pdf", description="pdf or markdown")


class SplunkIncidentBrief(BaseModel):
    """Simplified incident brief from Splunk logs only."""
    
    request_id: str
    time_range: str
    environment: str
    generated_at: datetime
    
    # Main sections
    summary: str
    errors_found: List[Dict[str, Any]]
    total_logs: int
    timeline: List[Dict[str, Any]]
    suggested_next_steps: List[str]
    
    # Metadata
    success: bool = True
    message: str = ""