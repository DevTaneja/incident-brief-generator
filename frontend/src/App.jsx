import React, { useState } from "react";
import axios from "axios";
import "./App.css";

const Icon = {
  Alert: () => (
    <svg viewBox="0 0 24 24">
      <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  ),
  FileText: () => (
    <svg viewBox="0 0 24 24">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
      <polyline points="14,2 14,8 20,8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
      <polyline points="10,9 9,9 8,9" />
    </svg>
  ),
  Clock: () => (
    <svg viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10" />
      <polyline points="12,6 12,12 16,14" />
    </svg>
  ),
  List: () => (
    <svg viewBox="0 0 24 24">
      <line x1="8" y1="6" x2="21" y2="6" />
      <line x1="8" y1="12" x2="21" y2="12" />
      <line x1="8" y1="18" x2="21" y2="18" />
      <line x1="3" y1="6" x2="3.01" y2="6" />
      <line x1="3" y1="12" x2="3.01" y2="12" />
      <line x1="3" y1="18" x2="3.01" y2="18" />
    </svg>
  ),
  Zap: () => (
    <svg viewBox="0 0 24 24">
      <polygon points="13,2 3,14 12,14 11,22 21,10 12,10 13,2" />
    </svg>
  ),
  Info: () => (
    <svg viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="16" x2="12" y2="12" />
      <line x1="12" y1="8" x2="12.01" y2="8" />
    </svg>
  ),
  XCircle: () => (
    <svg viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10" />
      <line x1="15" y1="9" x2="9" y2="15" />
      <line x1="9" y1="9" x2="15" y2="15" />
    </svg>
  ),
  Send: () => (
    <svg viewBox="0 0 24 24">
      <line x1="22" y1="2" x2="11" y2="13" />
      <polygon points="22,2 15,22 11,13 2,9 22,2" />
    </svg>
  ),
  Inbox: () => (
    <svg viewBox="0 0 24 24">
      <polyline points="22,12 16,12 14,15 10,15 8,12 2,12" />
      <path d="M5.45 5.11L2 12v6a2 2 0 002 2h16a2 2 0 002-2v-6l-3.45-6.89A2 2 0 0016.76 4H7.24a2 2 0 00-1.79 1.11z" />
    </svg>
  ),
  Download: () => (
    <svg viewBox="0 0 24 24">
      <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
      <polyline points="7,10 12,15 17,10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  ),
  FilePdf: () => (
    <svg viewBox="0 0 24 24">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
      <polyline points="14,2 14,8 20,8" />
      <path d="M9 13h1.5a1 1 0 010 2H9v-4h1.5a1 1 0 010 2" />
      <line x1="15" y1="11" x2="15" y2="15" />
      <line x1="13" y1="13" x2="17" y2="13" />
    </svg>
  ),
  FileMd: () => (
    <svg viewBox="0 0 24 24">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
      <polyline points="14,2 14,8 20,8" />
      <polyline points="10,15 12,13 14,15" />
      <line x1="12" y1="13" x2="12" y2="17" />
    </svg>
  ),
};

function App() {
  const [requestId, setRequestId] = useState("");
  const [timeRange, setTimeRange] = useState("1h");
  const [environment, setEnvironment] = useState("prod");
  const [loading, setLoading] = useState(false);
  const [brief, setBrief] = useState(null);
  const [error, setError] = useState(null);

  const API_URL = "/api/v1";

  const generateBrief = async () => {
    if (!requestId.trim()) {
      setError("Request ID is required.");
      return;
    }
    setLoading(true);
    setError(null);
    setBrief(null);
    try {
      const response = await axios.post(`${API_URL}/generate-brief`, {
        request_id: requestId,
        time_range: timeRange,
        environment: environment,
      });
      setBrief(response.data);
    } catch (err) {
      setError(
        err.response?.data?.message ||
          "Failed to generate incident brief. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) =>
    new Date(dateString).toLocaleString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });

  const levelClass = (level = "") => level.toLowerCase();

  const downloadReport = (format) => {
    if (!brief) return;

    if (format === "markdown") {
      const lines = [
        `# Incident Brief — ${brief.request_id}`,
        ``,
        `| Field | Value |`,
        `|---|---|`,
        `| Request ID | ${brief.request_id} |`,
        `| Time Range | ${brief.time_range} |`,
        `| Environment | ${brief.environment} |`,
        `| Generated | ${formatDate(brief.generated_at)} |`,
        ``,
        `## Summary`,
        ``,
        brief.summary || "_No summary available._",
        ``,
      ];
      if (brief.errors_found?.length) {
        lines.push(`## Errors Detected (${brief.errors_found.length})`);
        brief.errors_found.forEach((e, i) => {
          lines.push(``, `### Error ${i + 1}`, `**Message:** ${e.message}`);
          lines.push(
            `**Time:** ${formatDate(e.timestamp)}  |  **Service:** ${e.service}`,
          );
          if (e.stack_trace) lines.push(``, "```", e.stack_trace, "```");
        });
        lines.push(``);
      }
      if (brief.timeline?.length) {
        lines.push(`## Event Timeline (${brief.total_logs} events)`, ``);
        lines.push(`| Timestamp | Level | Message | Service |`);
        lines.push(`|---|---|---|---|`);
        brief.timeline.forEach((ev) =>
          lines.push(
            `| ${formatDate(ev.timestamp)} | ${ev.level} | ${ev.message} | ${ev.service} |`,
          ),
        );
        lines.push(``);
      }
      if (brief.suggested_next_steps?.length) {
        lines.push(`## Suggested Next Steps`, ``);
        brief.suggested_next_steps.forEach((s, i) =>
          lines.push(`${i + 1}. ${s}`),
        );
        lines.push(``);
      }
      if (brief.message) lines.push(`## Additional Notes`, ``, brief.message);
      const blob = new Blob([lines.join("\n")], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `incident-brief-${brief.request_id}.md`;
      a.click();
      URL.revokeObjectURL(url);
    }

    if (format === "pdf") {
      const win = window.open("", "_blank");
      if (!win) return;
      const errorsHtml = brief.errors_found?.length
        ? `<h2>Errors Detected (${brief.errors_found.length})</h2>` +
          brief.errors_found
            .map(
              (e, i) => `
            <div class="error-block">
              <p><strong>Error ${i + 1}:</strong> ${e.message}</p>
              <p class="meta">Time: ${formatDate(e.timestamp)} &nbsp;|&nbsp; Service: ${e.service}</p>
              ${e.stack_trace ? `<pre>${e.stack_trace}</pre>` : ""}
            </div>`,
            )
            .join("")
        : "";
      const timelineHtml = brief.timeline?.length
        ? `<h2>Event Timeline (${brief.total_logs} events)</h2>
           <table><thead><tr><th>Timestamp</th><th>Level</th><th>Message</th><th>Service</th></tr></thead><tbody>` +
          brief.timeline
            .map(
              (ev) =>
                `<tr><td>${formatDate(ev.timestamp)}</td><td>${ev.level}</td><td>${ev.message}</td><td>${ev.service}</td></tr>`,
            )
            .join("") +
          `</tbody></table>`
        : "";
      const stepsHtml = brief.suggested_next_steps?.length
        ? `<h2>Suggested Next Steps</h2><ol>${brief.suggested_next_steps.map((s) => `<li>${s}</li>`).join("")}</ol>`
        : "";
      win.document.write(`<!DOCTYPE html><html><head><meta charset="utf-8">
        <title>Incident Brief — ${brief.request_id}</title>
        <style>
          body{font-family:-apple-system,sans-serif;font-size:13px;color:#111;max-width:900px;margin:40px auto;padding:0 24px;line-height:1.6}
          h1{font-size:20px;font-weight:600;margin-bottom:4px}
          h2{font-size:14px;font-weight:600;margin:24px 0 8px;border-bottom:1px solid #e2e4e9;padding-bottom:4px}
          .meta-row{display:flex;gap:24px;font-size:12px;color:#50566b;margin-bottom:20px;flex-wrap:wrap}
          .summary{background:#f8f9fa;border:1px solid #e2e4e9;border-radius:6px;padding:12px;color:#50566b}
          .error-block{background:#fef2f2;border:1px solid #fca5a5;border-radius:6px;padding:12px;margin-bottom:8px}
          .meta{font-size:11px;color:#888;margin:4px 0 0}
          pre{background:#1a1d23;color:#abb2bf;padding:10px;border-radius:4px;font-size:11px;overflow-x:auto}
          table{width:100%;border-collapse:collapse;font-size:12px;margin-top:8px}
          th{text-align:left;font-weight:500;color:#50566b;padding:6px 8px;background:#f8f9fa;border:1px solid #e2e4e9}
          td{padding:6px 8px;border:1px solid #e2e4e9}
          ol{padding-left:20px}li{margin-bottom:6px}
        </style></head><body>
        <h1>Incident Brief</h1>
        <div class="meta-row">
          <span>Request ID: <strong>${brief.request_id}</strong></span>
          <span>Time Range: <strong>${brief.time_range}</strong></span>
          <span>Environment: <strong>${brief.environment}</strong></span>
          <span>Generated: <strong>${formatDate(brief.generated_at)}</strong></span>
        </div>
        <h2>Summary</h2>
        <div class="summary">${brief.summary || "No summary available."}</div>
        ${errorsHtml}${timelineHtml}${stepsHtml}
        ${brief.message ? `<h2>Additional Notes</h2><p>${brief.message}</p>` : ""}
        </body></html>`);
      win.document.close();
      win.focus();
      setTimeout(() => win.print(), 400);
    }
  };

  return (
    <div className="App">
      <header className="header">
        <div className="header-brand">
          <div className="header-icon">
            <Icon.Alert />
          </div>
          <h1>Incident Brief Generator</h1>
        </div>
        <span className="header-badge">Internal Operations</span>
      </header>

      <div className="layout">
        {/* ─── Sidebar ─────────────────────────────────────────────────── */}
        <aside className="sidebar">
          <div>
            <p className="panel-title">Query Parameters</p>
            <div className="field-group">
              <div className="field">
                <label className="field-required">Request ID</label>
                <input
                  type="text"
                  value={requestId}
                  onChange={(e) => setRequestId(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && generateBrief()}
                  placeholder="e.g. abc-123 or UUID"
                  className="input"
                />
              </div>
              <div className="field">
                <label>Time Range</label>
                <select
                  value={timeRange}
                  onChange={(e) => setTimeRange(e.target.value)}
                  className="select"
                >
                  <option value="5m">Last 5 minutes</option>
                  <option value="30m">Last 30 minutes</option>
                  <option value="1h">Last 1 hour</option>
                  <option value="6h">Last 6 hours</option>
                  <option value="24h">Last 24 hours</option>
                </select>
              </div>
              <div className="field">
                <label>Environment</label>
                <select
                  value={environment}
                  onChange={(e) => setEnvironment(e.target.value)}
                  className="select"
                >
                  <option value="prod">Production</option>
                  <option value="staging">Staging</option>
                  <option value="dev">Development</option>
                </select>
              </div>
            </div>
          </div>

          <div className="divider" />

          <button
            onClick={generateBrief}
            disabled={loading}
            className="btn-primary"
          >
            {loading ? (
              <>
                <span className="spinner" />
                Generating...
              </>
            ) : (
              <>
                <Icon.Send />
                Generate Brief
              </>
            )}
          </button>
        </aside>

        {/* ─── Main Content ─────────────────────────────────────────────── */}
        <main className="main">
          {error && (
            <div className="alert alert-danger">
              <Icon.XCircle />
              {error}
            </div>
          )}

          {!brief && !error && (
            <div className="empty-state">
              <div className="empty-state-icon">
                <Icon.Inbox />
              </div>
              <h3>No report generated</h3>
              <p>
                Enter a Request ID and submit to generate an incident brief.
              </p>
            </div>
          )}

          {brief && (
            <>
              {/* Report Header */}
              <div className="report-header">
                <div>
                  <div className="report-title">Incident Brief</div>
                  <div className="report-meta">
                    <span className="meta-chip">
                      Request ID <strong>{brief.request_id}</strong>
                    </span>
                    <span className="meta-chip">
                      Time Range <strong>{brief.time_range}</strong>
                    </span>
                    <span className="meta-chip">
                      Env <strong>{brief.environment}</strong>
                    </span>
                    <span className="meta-chip">
                      Generated{" "}
                      <strong>{formatDate(brief.generated_at)}</strong>
                    </span>
                  </div>
                </div>
                <div className="download-actions">
                  <button
                    onClick={() => downloadReport("pdf")}
                    className="btn-download btn-download-pdf"
                  >
                    <Icon.FilePdf />
                    Export PDF
                  </button>
                  <button
                    onClick={() => downloadReport("markdown")}
                    className="btn-download btn-download-md"
                  >
                    <Icon.FileMd />
                    Export Markdown
                  </button>
                </div>
              </div>

              {/* Summary */}
              <div className="section-card">
                <div className="section-card-header">
                  <span className="section-card-title">
                    <Icon.FileText />
                    Summary
                  </span>
                </div>
                <div className="section-card-body">
                  <p className="summary-text">{brief.summary}</p>
                </div>
              </div>

              {/* Errors */}
              {brief.errors_found?.length > 0 && (
                <div className="section-card">
                  <div className="section-card-header">
                    <span className="section-card-title">
                      <Icon.XCircle />
                      Errors Detected
                    </span>
                    <span className="count-badge">
                      {brief.errors_found.length}
                    </span>
                  </div>
                  <div className="section-card-body">
                    {brief.errors_found.map((err, idx) => (
                      <div key={idx} className="error-item">
                        <div className="error-item-header">
                          <Icon.XCircle />
                          <span className="error-message">{err.message}</span>
                        </div>
                        {err.stack_trace && (
                          <pre className="stack-trace">{err.stack_trace}</pre>
                        )}
                        <div className="error-meta-row">
                          <span>Time: {formatDate(err.timestamp)}</span>
                          <span>Service: {err.service}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Timeline */}
              {brief.timeline?.length > 0 && (
                <div className="section-card">
                  <div className="section-card-header">
                    <span className="section-card-title">
                      <Icon.Clock />
                      Event Timeline
                    </span>
                    <span className="count-badge">
                      {brief.total_logs} events
                    </span>
                  </div>
                  <div
                    className="section-card-body"
                    style={{ padding: "0 16px" }}
                  >
                    <div className="timeline-wrapper">
                      {brief.timeline.map((event, idx) => (
                        <div key={idx} className="timeline-item">
                          <span className="timeline-time">
                            {formatDate(event.timestamp)}
                          </span>
                          <span
                            className={`level-badge ${levelClass(event.level)}`}
                          >
                            {event.level}
                          </span>
                          <span
                            className="timeline-message"
                            title={event.message}
                          >
                            {event.message}
                          </span>
                          <span
                            className="timeline-service"
                            title={event.service}
                          >
                            {event.service}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Next Steps */}
              {brief.suggested_next_steps?.length > 0 && (
                <div className="section-card">
                  <div className="section-card-header">
                    <span className="section-card-title">
                      <Icon.Zap />
                      Suggested Next Steps
                    </span>
                  </div>
                  <div className="section-card-body">
                    <ul className="steps-list">
                      {brief.suggested_next_steps.map((step, idx) => (
                        <li key={idx}>
                          <span className="step-num">{idx + 1}</span>
                          {step}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* Additional Info */}
              {brief.message && (
                <div className="info-card">
                  <strong>Note:</strong> {brief.message}
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
