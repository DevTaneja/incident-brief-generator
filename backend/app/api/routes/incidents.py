"""Incident generation API routes."""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, status

from app.config import settings
from app.models.incident import (
    IncidentRequest,
    IncidentBrief,
    ErrorObservation,
    PerformanceInsight,
    TimelineEvent,
    RelatedIssue,
    ReportDownloadRequest,
    SplunkIncidentBrief
)
from app.integrations.splunk_client import SplunkSearchClient
from app.integrations.newrelic_client import NewRelicClient
from app.integrations.jira_client import JiraClient
from app.integrations.llm_client import llm_client
from app.core.exceptions import ValidationError

from app.services.report_generator import report_generator
from fastapi.responses import Response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/generate-brief", response_model=SplunkIncidentBrief)
async def generate_incident_brief(request: IncidentRequest):
    """
    Generate an incident brief based on request_id and time_range.
    Includes data from Splunk logs, New Relic metrics, Jira issues, and LLM analysis.
    """
    logger.info(f"Generating brief for request_id={request.request_id}")
    
    # Initialize Splunk client
    splunk = SplunkSearchClient(
        host=settings.splunk_host,
        port=settings.splunk_port,
        username=settings.splunk_username,
        password=settings.splunk_password
    )
    
    # Initialize New Relic client
    newrelic = NewRelicClient(
        api_key=settings.new_relic_api_key,
        account_id=settings.new_relic_account_id
    )
    
    # Initialize Jira client
    jira = JiraClient(
        url=settings.jira_url,
        email=settings.jira_email,
        api_token=settings.jira_api_token,
        project_key=settings.jira_project_key
    )

    # Search for logs in Splunk
    logs = await splunk.search_by_request_id(
        request_id=request.request_id,
        time_range=request.time_range,
        index="main"
    )

    # Get New Relic metrics
    nr_metrics = await newrelic.get_transactions_for_request(
        request_id=request.request_id,
        time_range=request.time_range
    )
    
    nr_errors = await newrelic.get_error_count(
        request_id=request.request_id,
        time_range=request.time_range
    )
    
    # Extract error message from logs
    error_message = ""
    errors = []
    
    if logs:
        errors = [log for log in logs if log.get("level") == "ERROR"]
        if errors:
            error_message = errors[0].get('message', '')
    
    # Search Jira using LLM-extracted keywords
    jira_issues = []
    llm_keywords = []
    
    if error_message:
        # Use LLM to extract keywords
        llm_keywords = await llm_client.extract_keywords(error_message)
        logger.info(f"LLM extracted keywords: {llm_keywords}")
        
        # Search Jira with extracted keywords
        if llm_keywords:
            jira_issues = await jira.search_by_keywords(llm_keywords, max_results=3)
            logger.info(f"Found {len(jira_issues)} related Jira issues")
    
    # Generate LLM analysis
    llm_analysis = {}
    if error_message:
        # Prepare metrics for LLM
        metrics_for_llm = {
            "average_duration_ms": nr_metrics.get('average_duration_ms'),
            "total_calls": nr_metrics.get('total_calls', 0),
            "error_count": nr_errors
        }
        
        llm_analysis = await llm_client.analyze_incident(
            error_message=error_message,
            logs=errors[:5],  # Send only errors
            metrics=metrics_for_llm,
            jira_issues=jira_issues
        )
        logger.info(f"LLM analysis generated")
    
    # Build response message components
    nr_message = ""
    avg_duration = nr_metrics.get('average_duration_ms')
    total_calls = nr_metrics.get('total_calls', 0)
    
    if nr_metrics.get("found"):
        if avg_duration is not None:
            nr_message = f" New Relic: {total_calls} transactions, {nr_errors} errors, avg duration {avg_duration:.2f}ms."
        else:
            nr_message = f" New Relic: {total_calls} transactions, {nr_errors} errors."
    else:
        nr_message = " New Relic: No transactions found for this requestId."
    
    # Build Jira message
    jira_message = ""
    if jira_issues:
        issue_keys = [i['key'] for i in jira_issues]
        jira_message = f" Found {len(jira_issues)} related Jira issues: {', '.join(issue_keys)}."
    
    # Use LLM summary if available, otherwise generate basic
    if llm_analysis and llm_analysis.get('summary'):
        summary = llm_analysis.get('summary')
        if nr_message:
            summary += nr_message
        if jira_message:
            summary += jira_message
    elif errors:
        summary = f"Found {len(errors)} error(s) in {len(logs)} total logs. "
        summary += f"First error: {errors[0].get('message', 'Unknown')}.{nr_message}{jira_message}"
    elif logs:
        summary = f"Found {len(logs)} logs, all at INFO level. No errors detected.{nr_message}{jira_message}"
    else:
        summary = f"No logs found for requestId={request.request_id}.{nr_message}{jira_message}"
    
    if not logs:
        return SplunkIncidentBrief(
            request_id=request.request_id,
            time_range=request.time_range,
            environment=request.environment,
            generated_at=datetime.utcnow(),
            summary=summary,
            errors_found=[],
            total_logs=0,
            timeline=[],
            suggested_next_steps=[
                "Verify the requestId is correct",
                "Check if time range includes the incident",
                "Ensure logs are being sent to Splunk",
                "Verify New Relic agent is sending data with requestId attribute"
            ],
            success=False,
            message="No logs found"
        )
    
    # Build timeline
    timeline = []
    for log in logs:
        timeline.append({
            "timestamp": log.get("timestamp"),
            "level": log.get("level"),
            "message": log.get("message"),
            "service": log.get("service", "unknown")
        })
    
    # Sort timeline by timestamp
    timeline.sort(key=lambda x: x.get("timestamp", ""))
    
    # Build suggested next steps (prioritize LLM recommendations)
    suggested_steps = []
    
    # Add LLM recommendations if available
    if llm_analysis and llm_analysis.get('recommendations'):
        suggested_steps.extend(llm_analysis.get('recommendations', [])[:3])
    
    # Add root cause if available
    if llm_analysis and llm_analysis.get('root_cause_analysis'):
        suggested_steps.insert(0, f"Root cause: {llm_analysis.get('root_cause_analysis')}")
    
    # Add Jira suggestions
    if jira_issues:
        suggested_steps.append(f"Check related Jira issue: {jira_issues[0]['key']} - {jira_issues[0]['summary']}")
        if jira_issues[0].get('status') == 'Resolved' or jira_issues[0].get('status') == 'Done':
            suggested_steps.append(f"Previous issue {jira_issues[0]['key']} was resolved - review the solution")
    
    # Add New Relic suggestions
    if nr_metrics.get("found") and avg_duration is not None and avg_duration > 100:
        suggested_steps.append(f"High average duration ({avg_duration:.2f}ms) - investigate performance")
    
    if nr_errors > 0:
        suggested_steps.append(f"New Relic shows {nr_errors} error(s) - check transaction errors")
    
    # Add fallback steps if no suggestions yet
    if not suggested_steps:
        suggested_steps.append("Check related services for similar errors")
        suggested_steps.append("Review recent deployments or changes")
    
    # Build message
    message = f"Found {len(logs)} logs. New Relic: {total_calls} transactions, {nr_errors} errors. Jira: {len(jira_issues)} related issues"
    if llm_analysis:
        message += f" LLM analysis: {llm_analysis.get('summary', '')[:100]}"
    
    return SplunkIncidentBrief(
        request_id=request.request_id,
        time_range=request.time_range,
        environment=request.environment,
        generated_at=datetime.utcnow(),
        summary=summary,
        errors_found=errors,
        total_logs=len(logs),
        timeline=timeline,
        suggested_next_steps=suggested_steps,
        success=True,
        message=message
    )


@router.post("/download-report")
async def download_report(request: ReportDownloadRequest):
    """
    Download the incident brief as PDF or Markdown.
    """
    logger.info(f"Generating {request.format} report for request_id={request.brief.request_id}")
    
    # Convert brief to dict
    brief_dict = request.brief.dict()
    
    if request.format == "markdown":
        markdown_content = report_generator.generate_markdown(brief_dict)
        
        return Response(
            content=markdown_content,
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename=incident_brief_{request.brief.request_id}.md"
            }
        )
    
    elif request.format == "pdf":
        pdf_content = report_generator.generate_pdf(brief_dict)
        
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=incident_brief_{request.brief.request_id}.pdf"
            }
        )
    
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
@router.get("/status")
async def status_check():
    """Check if the incident generation service is ready."""
    return {
        "service": "incident-generator",
        "status": "running",
        "integrations": {
            "splunk": "connected",
            "new_relic": "connected",
            "jira": "connected",
            "llm": "connected"
        }
    }