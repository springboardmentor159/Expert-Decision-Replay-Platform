import client from "./client";

export async function getDecisionReport(params = {}) {
  const res = await client.get("/reports/decisions", { params });
  return res.data;
}

export async function getApprovalReport(params = {}) {
  const res = await client.get("/reports/approvals", { params });
  return res.data;
}

export async function getTeamReport(params = {}) {
  const res = await client.get("/reports/teams", { params });
  return res.data;
}

export async function getAuditReport(params = {}) {
  const res = await client.get("/reports/audit", { params });
  return res.data;
}

// Triggers a browser download for a file-returning endpoint.
async function downloadFile(path, params, fallbackName) {
  const res = await client.get(path, { params, responseType: "blob" });

  const disposition = res.headers["content-disposition"];
  let filename = fallbackName;
  if (disposition) {
    const match = disposition.match(/filename="?([^"]+)"?/);
    if (match) filename = match[1];
  }

  const url = window.URL.createObjectURL(new Blob([res.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

export const exportDecisionReportPdf = (params) => downloadFile("/reports/decisions/export/pdf", params, "decision-report.pdf");
export const exportDecisionReportExcel = (params) => downloadFile("/reports/decisions/export/excel", params, "decision-report.xlsx");

export const exportApprovalReportPdf = (params) => downloadFile("/reports/approvals/export/pdf", params, "approval-report.pdf");
export const exportApprovalReportExcel = (params) => downloadFile("/reports/approvals/export/excel", params, "approval-report.xlsx");

export const exportTeamReportPdf = (params) => downloadFile("/reports/teams/export/pdf", params, "team-report.pdf");
export const exportTeamReportExcel = (params) => downloadFile("/reports/teams/export/excel", params, "team-report.xlsx");

export const exportAuditReportPdf = (params) => downloadFile("/reports/audit/export/pdf", params, "audit-report.pdf");
export const exportAuditReportExcel = (params) => downloadFile("/reports/audit/export/excel", params, "audit-report.xlsx");
