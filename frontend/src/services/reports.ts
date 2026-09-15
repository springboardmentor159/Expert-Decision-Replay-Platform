import api from "./api";

export interface DecisionReportItem {
  decision_id: number;
  title: string;
  category?: string;
  status?: string;
  created_by?: number;
  created_date?: string;
  updated_date?: string;
  alternatives_count?: number;
  approvals_count?: number;
  tags?: string[];
}

export interface DecisionReportSummary {
  total_decisions: number;
  draft_decisions: number;
  under_review_decisions: number;
  approved_decisions: number;
  rejected_decisions: number;
  archived_decisions: number;
}

export interface DecisionReportResponse {
  items: DecisionReportItem[];
  summary: DecisionReportSummary;
  page: number;
  page_size: number;
  total: number;
}

export interface ApprovalReportItem {
  approval_id: number;
  decision_id: number;
  decision_title: string;
  reviewer_id: number;
  approval_level: number;
  status: string;
  assigned_date?: string;
  completed_date?: string | null;
  turnaround_days?: number | null;
}

export interface ApprovalReportSummary {
  total_approvals: number;
  pending_approvals: number;
  approved_approvals: number;
  rejected_approvals: number;
  average_turnaround_days?: number | null;
  completion_rate: number;
}

export interface ApprovalReportResponse {
  items: ApprovalReportItem[];
  summary: ApprovalReportSummary;
  page: number;
  page_size: number;
  total: number;
}

export interface TeamReportItem {
  team_name: string;
  members: number;
  total_decisions: number;
  approved_decisions: number;
  rejected_decisions: number;
  pending_decisions: number;
  approval_rate: number;
}

export interface TeamReportSummary {
  total_teams: number;
  total_members: number;
  total_decisions: number;
  total_approved: number;
  total_rejected: number;
  total_pending: number;
}

export interface TeamReportResponse {
  items: TeamReportItem[];
  summary: TeamReportSummary;
  page: number;
  page_size: number;
  total: number;
}

export interface AuditReportItem {
  audit_id: number;
  user_id: number;
  action: string;
  entity_type: string;
  entity_id?: number | null;
  description?: string;
  timestamp?: string;
  ip_address?: string | null;
}

export interface AuditReportSummary {
  total_audit_logs: number;
  create_actions: number;
  update_actions: number;
  delete_actions: number;
  approve_actions: number;
  reject_actions: number;
  access_actions: number;
  login_actions: number;
  logout_actions: number;
  submit_actions: number;
  archive_actions: number;
}

export interface AuditReportResponse {
  items: AuditReportItem[];
  summary: AuditReportSummary;
  page: number;
  page_size: number;
  total: number;
}

export interface ReportFilters {
  category?: string;
  status?: string;
  created_by?: number;
  start_date?: string;
  end_date?: string;
  tag?: string;
  reviewer_id?: number;
  decision_id?: number;
  approval_level?: number;
  team?: string;
  user_id?: number;
  action?: string;
  entity_type?: string;
  entity_id?: number;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: string;
}

export async function getDecisionReport(
  params?: ReportFilters,
) {
  const response = await api.get<DecisionReportResponse>(
    "/reports/decisions",
    {
      params,
    },
  );

  return response.data;
}

export async function getApprovalReport(
  params?: ReportFilters,
) {
  const response = await api.get<ApprovalReportResponse>(
    "/reports/approvals",
    {
      params,
    },
  );

  return response.data;
}

export async function getTeamReport(
  params?: ReportFilters,
) {
  const response = await api.get<TeamReportResponse>(
    "/reports/teams",
    {
      params,
    },
  );

  return response.data;
}

export async function getAuditReport(
  params?: ReportFilters,
) {
  const response = await api.get<AuditReportResponse>(
    "/reports/audit",
    {
      params,
    },
  );

  return response.data;
}

function downloadBlob(
  blob: Blob,
  filename: string,
) {
  const url = window.URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = filename;

  document.body.appendChild(link);
  link.click();

  link.remove();

  window.URL.revokeObjectURL(url);
}

export async function exportDecisionPdf(
  params?: ReportFilters,
) {
  const response = await api.get(
    "/reports/decisions/export/pdf",
    {
      params,
      responseType: "blob",
    },
  );

  downloadBlob(
    response.data,
    "decision_report.pdf",
  );
}

export async function exportDecisionExcel(
  params?: ReportFilters,
) {
  const response = await api.get(
    "/reports/decisions/export/excel",
    {
      params,
      responseType: "blob",
    },
  );

  downloadBlob(
    response.data,
    "decision_report.xlsx",
  );
}

export async function exportApprovalPdf(
  params?: ReportFilters,
) {
  const response = await api.get(
    "/reports/approvals/export/pdf",
    {
      params,
      responseType: "blob",
    },
  );

  downloadBlob(
    response.data,
    "approval_report.pdf",
  );
}

export async function exportApprovalExcel(
  params?: ReportFilters,
) {
  const response = await api.get(
    "/reports/approvals/export/excel",
    {
      params,
      responseType: "blob",
    },
  );

  downloadBlob(
    response.data,
    "approval_report.xlsx",
  );
}

export async function exportTeamPdf(
  params?: ReportFilters,
) {
  const response = await api.get(
    "/reports/teams/export/pdf",
    {
      params,
      responseType: "blob",
    },
  );

  downloadBlob(
    response.data,
    "team_report.pdf",
  );
}

export async function exportTeamExcel(
  params?: ReportFilters,
) {
  const response = await api.get(
    "/reports/teams/export/excel",
    {
      params,
      responseType: "blob",
    },
  );

  downloadBlob(
    response.data,
    "team_report.xlsx",
  );
}

export async function exportAuditPdf(
  params?: ReportFilters,
) {
  const response = await api.get(
    "/reports/audit/export/pdf",
    {
      params,
      responseType: "blob",
    },
  );

  downloadBlob(
    response.data,
    "audit_report.pdf",
  );
}

export async function exportAuditExcel(
  params?: ReportFilters,
) {
  const response = await api.get(
    "/reports/audit/export/excel",
    {
      params,
      responseType: "blob",
    },
  );

  downloadBlob(
    response.data,
    "audit_report.xlsx",
  );
}