(function () {
  "use strict";

  const APPROVALS_ROUTE = "/operator/approvals";
  const DETAIL_ROUTE_TEMPLATE = "/operator/approvals/{approval_id}";
  const STATUS_ROUTE_TEMPLATE = "/operator/approvals/{approval_id}/status";
  const AUDIT_ROUTE_TEMPLATE = "/operator/approvals/{approval_id}/audit";
  const SIDE_EFFECT_ROUTE_TEMPLATE = "/operator/side-effects/{side_effect_id}";
  const APPROVE_ROUTE_TEMPLATE = "/operator/approvals/{approval_id}/approve";
  const REJECT_ROUTE_TEMPLATE = "/operator/approvals/{approval_id}/reject";

  let apiKey = "";
  let selectedApprovalId = "";

  const keyForm = document.getElementById("key-form");
  const keyInput = document.getElementById("api-key");
  const refreshButton = document.getElementById("refresh-button");
  const approvalList = document.getElementById("approval-list");
  const approvalDetail = document.getElementById("approval-detail");
  const decisionForm = document.getElementById("decision-form");
  const decisionReason = document.getElementById("decision-reason");
  const approveButton = document.getElementById("approve-button");
  const rejectButton = document.getElementById("reject-button");
  const message = document.getElementById("message");

  function routeFromTemplate(template, approvalId) {
    return template.replace("{approval_id}", encodeURIComponent(approvalId));
  }

  function sideEffectRoute(sideEffectId) {
    return SIDE_EFFECT_ROUTE_TEMPLATE.replace(
      "{side_effect_id}",
      encodeURIComponent(sideEffectId),
    );
  }

  function setMessage(text, isError) {
    message.textContent = text;
    message.classList.toggle("is-error", Boolean(isError));
  }

  function requireKey() {
    if (!apiKey) {
      setMessage("Paste a local demo API key before loading approvals.", true);
      keyInput.focus();
      return false;
    }
    return true;
  }

  async function fetchJson(path, options) {
    const response = await fetch(path, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": apiKey,
        ...(options && options.headers ? options.headers : {}),
      },
    });
    const text = await response.text();
    let body = {};

    if (text) {
      try {
        body = JSON.parse(text);
      } catch (_error) {
        body = { detail: text };
      }
    }

    if (!response.ok) {
      const detail = body.detail || `Request failed with ${response.status}.`;
      throw new Error(Array.isArray(detail) ? JSON.stringify(detail) : detail);
    }

    return body;
  }

  function clearNode(node) {
    while (node.firstChild) {
      node.removeChild(node.firstChild);
    }
  }

  function appendText(parent, text) {
    const span = document.createElement("span");
    span.textContent = text;
    parent.appendChild(span);
    return span;
  }

  function appendField(parent, label, value) {
    const row = document.createElement("div");
    row.className = "field-row";

    const name = document.createElement("strong");
    name.textContent = `${label}:`;
    row.appendChild(name);
    appendText(row, value === null || value === undefined ? "none" : String(value));

    parent.appendChild(row);
  }

  function appendSection(parent, title) {
    const section = document.createElement("section");
    section.className = "detail-section";

    const heading = document.createElement("h3");
    heading.textContent = title;
    section.appendChild(heading);

    parent.appendChild(section);
    return section;
  }

  function appendJsonSection(parent, title, value) {
    const section = appendSection(parent, title);

    const pre = document.createElement("pre");
    pre.textContent = JSON.stringify(value, null, 2);
    section.appendChild(pre);

    parent.appendChild(section);
  }

  function appendTimeline(parent, events) {
    if (!events || !events.length) {
      appendText(parent, "No local/demo audit events are available.");
      return;
    }

    const list = document.createElement("ol");
    list.className = "timeline-list";

    events.forEach((event) => {
      const item = document.createElement("li");
      const title = document.createElement("strong");
      title.textContent = `${event.sequence}. ${event.event_type}`;
      item.appendChild(title);
      appendField(item, "Actor", event.actor_id);
      appendField(item, "Timestamp", event.timestamp);
      appendField(item, "Tool", event.tool_name);
      appendField(item, "Message", event.message);
      appendJsonSection(item, "Metadata", event.metadata);
      list.appendChild(item);
    });

    parent.appendChild(list);
  }

  function appendDecisionHistory(parent, decisions) {
    if (!decisions || !decisions.length) {
      appendText(parent, "No operator decision has been recorded.");
      return;
    }

    decisions.forEach((decision) => {
      const item = document.createElement("div");
      item.className = "decision-history-item";
      appendField(item, "Decision", decision.decision);
      appendField(item, "Actor", decision.actor_id);
      appendField(item, "Role", decision.actor_role);
      appendField(item, "Reason", decision.reason);
      appendField(item, "Timestamp", decision.timestamp);
      parent.appendChild(item);
    });
  }

  function renderEmptyList(text) {
    clearNode(approvalList);
    const item = document.createElement("li");
    item.className = "empty-state";
    item.textContent = text;
    approvalList.appendChild(item);
  }

  function renderApprovals(approvals) {
    clearNode(approvalList);

    if (!approvals.length) {
      renderEmptyList("No pending local/demo approvals.");
      return;
    }

    approvals.forEach((approval) => {
      const item = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "approval-card";
      button.classList.toggle(
        "is-selected",
        approval.approval_id === selectedApprovalId,
      );

      const title = document.createElement("strong");
      title.textContent = approval.task || approval.approval_id;
      button.appendChild(title);

      const meta = document.createElement("div");
      meta.className = "meta-row";
      appendText(meta, approval.status || "unknown status");
      appendText(meta, approval.risk_level || "unknown risk");
      appendText(meta, approval.policy_status || "unknown policy");
      button.appendChild(meta);

      const tool = document.createElement("div");
      tool.className = "meta-row";
      appendText(tool, approval.tool_name || "no tool");
      button.appendChild(tool);

      button.addEventListener("click", () => {
        loadDetail(approval.approval_id);
      });

      item.appendChild(button);
      approvalList.appendChild(item);
    });
  }

  function renderDetail(approval, status, audit, sideEffect) {
    const base = approval || status;
    selectedApprovalId = base.approval_id;
    clearNode(approvalDetail);
    approvalDetail.classList.remove("empty-state");
    const canDecide = Boolean(status.can_approve || status.can_reject);
    decisionForm.hidden = !canDecide;
    approveButton.disabled = !status.can_approve;
    rejectButton.disabled = !status.can_reject;

    const currentStatus = appendSection(approvalDetail, "Current Status");
    appendField(currentStatus, "Approval ID", base.approval_id);
    appendField(currentStatus, "Run ID", base.run_id);
    appendField(currentStatus, "Status", status.status);
    appendField(currentStatus, "Approval status", status.approval_status);
    appendField(currentStatus, "Decision state", status.decision_state);
    appendField(currentStatus, "Task", status.task || base.task);
    appendField(currentStatus, "Risk", approval ? approval.risk_level : null);
    appendField(currentStatus, "Policy", approval ? approval.policy_status : null);
    appendField(currentStatus, "Tool", status.tool_name || base.tool_name);
    appendField(currentStatus, "Target", status.target || base.target);
    appendField(currentStatus, "Side effect ID", status.side_effect_id);
    appendField(currentStatus, "Args hash", status.args_hash);
    appendField(currentStatus, "Can approve", status.can_approve);
    appendField(currentStatus, "Can reject", status.can_reject);
    appendField(
      currentStatus,
      "Action unavailable",
      status.action_unavailable_reason,
    );
    appendField(currentStatus, "Updated", status.updated_at);

    const decisionHistory = appendSection(approvalDetail, "Decision History");
    appendDecisionHistory(decisionHistory, status.decision_history);

    const auditTimeline = appendSection(approvalDetail, "Audit Timeline");
    appendField(auditTimeline, "Scope", audit.audit_scope);
    appendField(auditTimeline, "Limitations", audit.audit_limitations);
    appendTimeline(auditTimeline, audit.events);

    const ledger = appendSection(approvalDetail, "Side-Effect / Ledger");
    if (sideEffect) {
      appendField(ledger, "Side effect ID", sideEffect.side_effect_id);
      appendField(ledger, "Ledger status", sideEffect.ledger_status);
      appendField(ledger, "Status", sideEffect.status);
      appendField(ledger, "Record available", sideEffect.record_available);
      appendField(ledger, "Source", sideEffect.source);
      appendField(ledger, "Repository", sideEffect.repository);
      appendField(ledger, "Issue", sideEffect.issue_number);
      appendField(ledger, "Duplicate status", sideEffect.duplicate_status);
      appendField(ledger, "Message", sideEffect.message);
      appendJsonSection(
        ledger,
        "External result summary",
        sideEffect.external_result_summary,
      );
      appendJsonSection(ledger, "Error summary", sideEffect.error_summary);
    } else {
      appendText(ledger, "No side-effect id is available for this local/demo run.");
    }

    appendJsonSection(
      approvalDetail,
      "Execution Result",
      status.execution_result,
    );
    appendJsonSection(approvalDetail, "Execution mode", status.execution_mode);

    if (approval) {
      appendJsonSection(approvalDetail, "Proposal", approval.proposal);
      appendJsonSection(
        approvalDetail,
        "Policy decisions",
        approval.policy_decisions,
      );
      appendJsonSection(
        approvalDetail,
        "Validated arguments",
        approval.validated_arguments,
      );
    }

    const limits = appendSection(approvalDetail, "Known Local/Demo Limitations");
    appendText(
      limits,
      "Local/demo audit and ledger visibility is limited to current process state. Fake/default execution only. No live GitHub execution. No GitHub token or .env required.",
    );
  }

  async function loadApprovals() {
    if (!requireKey()) {
      return;
    }

    setMessage("Loading approvals.", false);

    try {
      const body = await fetchJson(APPROVALS_ROUTE, { method: "GET" });
      renderApprovals(body.approvals || []);
      setMessage("Approvals loaded.", false);
    } catch (error) {
      renderEmptyList("Unable to load approvals.");
      setMessage(error.message, true);
    }
  }

  async function loadDetail(approvalId) {
    if (!requireKey()) {
      return;
    }

    selectedApprovalId = approvalId;
    setMessage("Loading approval detail.", false);

    try {
      const status = await fetchJson(routeFromTemplate(STATUS_ROUTE_TEMPLATE, approvalId), {
        method: "GET",
      });
      const audit = await fetchJson(routeFromTemplate(AUDIT_ROUTE_TEMPLATE, approvalId), {
        method: "GET",
      });
      let approval = null;
      let sideEffect = null;

      try {
        approval = await fetchJson(routeFromTemplate(DETAIL_ROUTE_TEMPLATE, approvalId), {
          method: "GET",
        });
      } catch (_error) {
        approval = null;
      }

      if (status.side_effect_id) {
        sideEffect = await fetchJson(sideEffectRoute(status.side_effect_id), {
          method: "GET",
        });
      }

      renderDetail(approval, status, audit, sideEffect);
      await loadApprovals();
      setMessage("Approval detail loaded.", false);
    } catch (error) {
      setMessage(error.message, true);
    }
  }

  async function decide(template, fallbackReason) {
    if (!selectedApprovalId || !requireKey()) {
      setMessage("Select an approval before sending a decision.", true);
      return;
    }

    const reason = decisionReason.value.trim();
    const payload = reason ? { decision_reason: reason } : {};
    if (fallbackReason && !reason) {
      payload.decision_reason = fallbackReason;
    }

    setMessage("Sending decision.", false);

    try {
      const decidedApprovalId = selectedApprovalId;
      const result = await fetchJson(routeFromTemplate(template, decidedApprovalId), {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setMessage(`Decision recorded: ${result.decision}.`, false);
      decisionReason.value = "";
      await loadDetail(decidedApprovalId);
    } catch (error) {
      setMessage(error.message, true);
    }
  }

  keyForm.addEventListener("submit", (event) => {
    event.preventDefault();
    apiKey = keyInput.value;
    setMessage("Local demo API key is active for this page session.", false);
    loadApprovals();
  });

  refreshButton.addEventListener("click", loadApprovals);
  approveButton.addEventListener("click", () => {
    decide(APPROVE_ROUTE_TEMPLATE, "Approved from local demo workbench.");
  });
  rejectButton.addEventListener("click", () => {
    decide(REJECT_ROUTE_TEMPLATE, "");
  });

  renderEmptyList("Paste a local demo API key, then refresh approvals.");
})();
