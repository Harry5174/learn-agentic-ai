(function () {
  "use strict";

  const APPROVALS_ROUTE = "/operator/approvals";
  const DETAIL_ROUTE_TEMPLATE = "/operator/approvals/{approval_id}";
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

  function appendJsonSection(parent, title, value) {
    const section = document.createElement("section");
    section.className = "detail-section";

    const heading = document.createElement("h3");
    heading.textContent = title;
    section.appendChild(heading);

    const pre = document.createElement("pre");
    pre.textContent = JSON.stringify(value, null, 2);
    section.appendChild(pre);

    parent.appendChild(section);
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

  function renderDetail(approval) {
    selectedApprovalId = approval.approval_id;
    clearNode(approvalDetail);
    approvalDetail.classList.remove("empty-state");
    decisionForm.hidden = false;

    const summary = document.createElement("section");
    summary.className = "detail-section";
    const heading = document.createElement("h3");
    heading.textContent = approval.task || "Approval request";
    summary.appendChild(heading);
    appendField(summary, "Approval ID", approval.approval_id);
    appendField(summary, "Run ID", approval.run_id);
    appendField(summary, "Status", approval.status);
    appendField(summary, "Approval status", approval.approval_status);
    appendField(summary, "Risk", approval.risk_level);
    appendField(summary, "Policy", approval.policy_status);
    appendField(summary, "Tool", approval.tool_name);
    appendField(summary, "Target", approval.target);
    appendField(summary, "Requested by", approval.requested_by);
    appendField(summary, "Side effect ID", approval.side_effect_id);
    appendField(summary, "Args hash", approval.args_hash);
    approvalDetail.appendChild(summary);

    appendJsonSection(approvalDetail, "Execution mode", approval.execution_mode);
    appendJsonSection(approvalDetail, "Required scopes", approval.required_scopes);
    appendJsonSection(approvalDetail, "Proposal", approval.proposal);
    appendJsonSection(approvalDetail, "Policy decisions", approval.policy_decisions);
    appendJsonSection(
      approvalDetail,
      "Validated arguments",
      approval.validated_arguments,
    );
    appendJsonSection(approvalDetail, "Audit events", approval.audit_events);
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
      const approval = await fetchJson(routeFromTemplate(DETAIL_ROUTE_TEMPLATE, approvalId), {
        method: "GET",
      });
      renderDetail(approval);
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
      const result = await fetchJson(routeFromTemplate(template, selectedApprovalId), {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setMessage(`Decision recorded: ${result.decision}.`, false);
      decisionReason.value = "";
      decisionForm.hidden = true;
      selectedApprovalId = "";
      clearNode(approvalDetail);
      approvalDetail.className = "approval-detail empty-state";
      approvalDetail.textContent = "Select an approval to review local/demo details.";
      await loadApprovals();
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
