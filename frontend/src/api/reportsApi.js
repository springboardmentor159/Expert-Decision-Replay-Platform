import apiClient from "./apiClient";

/*
|--------------------------------------------------------------------------
| Helpers
|--------------------------------------------------------------------------
*/

const buildParams = (values = {}) => {
  const params = {};

  Object.entries(values).forEach(([key, value]) => {
    if (
      value !== undefined &&
      value !== null &&
      value !== ""
    ) {
      params[key] = value;
    }
  });

  return params;
};


/*
|--------------------------------------------------------------------------
| Decision Reports
|--------------------------------------------------------------------------
*/

export const getDecisionReport = async ({
  category = "",
  status = "",
  created_by = "",
  start_date = "",
  end_date = "",
  tag = "",
  page = 1,
  page_size = 20,
  sort_by = "created_at",
  order = "desc",
} = {}) => {
  const params = buildParams({
    category,
    status,
    created_by,
    start_date,
    end_date,
    tag,
    page,
    page_size,
    sort_by,
    order,
  });

  const response = await apiClient.get(
    "/reports/decisions",
    { params }
  );

  return response.data;
};


/*
|--------------------------------------------------------------------------
| Approval Reports
|--------------------------------------------------------------------------
*/

export const getApprovalReport = async ({
  status = "",
  reviewer = "",
  decision = "",
  approval_level = "",
  start_date = "",
  end_date = "",
  page = 1,
  page_size = 20,
  sort_by = "assigned_at",
  order = "desc",
} = {}) => {
  const params = buildParams({
    status,
    reviewer,
    decision,
    approval_level,
    start_date,
    end_date,
    page,
    page_size,
    sort_by,
    order,
  });

  const response = await apiClient.get(
    "/reports/approvals",
    { params }
  );

  return response.data;
};


/*
|--------------------------------------------------------------------------
| Team Reports
|--------------------------------------------------------------------------
*/

export const getTeamReport = async ({
  team = "",
  start_date = "",
  end_date = "",
  decision_status = "",
  category = "",
  page = 1,
  page_size = 20,
  sort_by = "team",
  order = "asc",
} = {}) => {
  const params = buildParams({
    team,
    start_date,
    end_date,
    decision_status,
    category,
    page,
    page_size,
    sort_by,
    order,
  });

  const response = await apiClient.get(
    "/reports/teams",
    { params }
  );

  return response.data;
};


/*
|--------------------------------------------------------------------------
| Audit Reports
|--------------------------------------------------------------------------
*/

export const getAuditReport = async ({
  user_id = "",
  action = "",
  entity_type = "",
  entity_id = "",
  start_date = "",
  end_date = "",
  page = 1,
  page_size = 20,
  sort_by = "created_at",
  order = "desc",
} = {}) => {
  const params = buildParams({
    user_id,
    action,
    entity_type,
    entity_id,
    start_date,
    end_date,
    page,
    page_size,
    sort_by,
    order,
  });

  const response = await apiClient.get(
    "/reports/audit",
    { params }
  );

  return response.data;
};


/*
|--------------------------------------------------------------------------
| PDF Export
|--------------------------------------------------------------------------
*/

export const exportDecisionReportPdf = async (
  filters = {}
) => {
  const params = buildParams({
    category: filters.category,
    status: filters.status,
    created_by: filters.created_by,
    start_date: filters.start_date,
    end_date: filters.end_date,
    tag: filters.tag,
    page_size: filters.page_size || 100,
    sort_by: filters.sort_by || "created_at",
    order: filters.order || "desc",
  });

  const response = await apiClient.get(
    "/reports/decisions/export/pdf",
    {
      params,
      responseType: "blob",
    }
  );

  return response;
};


export const exportApprovalReportPdf = async (
  filters = {}
) => {
  const params = buildParams({
    status: filters.status,
    reviewer: filters.reviewer,
    decision: filters.decision,
    approval_level: filters.approval_level,
    start_date: filters.start_date,
    end_date: filters.end_date,
    page_size: filters.page_size || 100,
    sort_by: filters.sort_by || "assigned_at",
    order: filters.order || "desc",
  });

  const response = await apiClient.get(
    "/reports/approvals/export/pdf",
    {
      params,
      responseType: "blob",
    }
  );

  return response;
};


export const exportTeamReportPdf = async (
  filters = {}
) => {
  const params = buildParams({
    team: filters.team,
    start_date: filters.start_date,
    end_date: filters.end_date,
    decision_status: filters.decision_status,
    category: filters.category,
    page_size: filters.page_size || 100,
    sort_by: filters.sort_by || "team",
    order: filters.order || "asc",
  });

  const response = await apiClient.get(
    "/reports/teams/export/pdf",
    {
      params,
      responseType: "blob",
    }
  );

  return response;
};


export const exportAuditReportPdf = async (
  filters = {}
) => {
  const params = buildParams({
    user_id: filters.user_id,
    action: filters.action,
    entity_type: filters.entity_type,
    entity_id: filters.entity_id,
    start_date: filters.start_date,
    end_date: filters.end_date,
    page_size: filters.page_size || 100,
    sort_by: filters.sort_by || "created_at",
    order: filters.order || "desc",
  });

  const response = await apiClient.get(
    "/reports/audit/export/pdf",
    {
      params,
      responseType: "blob",
    }
  );

  return response;
};


/*
|--------------------------------------------------------------------------
| Excel Export
|--------------------------------------------------------------------------
*/

export const exportDecisionReportExcel = async (
  filters = {}
) => {
  const params = buildParams({
    category: filters.category,
    status: filters.status,
    created_by: filters.created_by,
    start_date: filters.start_date,
    end_date: filters.end_date,
    tag: filters.tag,
    page_size: filters.page_size || 1000,
    sort_by: filters.sort_by || "created_at",
    order: filters.order || "desc",
  });

  const response = await apiClient.get(
    "/reports/decisions/export/excel",
    {
      params,
      responseType: "blob",
    }
  );

  return response;
};


export const exportApprovalReportExcel = async (
  filters = {}
) => {
  const params = buildParams({
    status: filters.status,
    reviewer: filters.reviewer,
    decision: filters.decision,
    approval_level: filters.approval_level,
    start_date: filters.start_date,
    end_date: filters.end_date,
    page_size: filters.page_size || 1000,
    sort_by: filters.sort_by || "assigned_at",
    order: filters.order || "desc",
  });

  const response = await apiClient.get(
    "/reports/approvals/export/excel",
    {
      params,
      responseType: "blob",
    }
  );

  return response;
};


export const exportTeamReportExcel = async (
  filters = {}
) => {
  const params = buildParams({
    team: filters.team,
    start_date: filters.start_date,
    end_date: filters.end_date,
    decision_status: filters.decision_status,
    category: filters.category,
    page_size: filters.page_size || 1000,
    sort_by: filters.sort_by || "team",
    order: filters.order || "asc",
  });

  const response = await apiClient.get(
    "/reports/teams/export/excel",
    {
      params,
      responseType: "blob",
    }
  );

  return response;
};


export const exportAuditReportExcel = async (
  filters = {}
) => {
  const params = buildParams({
    user_id: filters.user_id,
    action: filters.action,
    entity_type: filters.entity_type,
    entity_id: filters.entity_id,
    start_date: filters.start_date,
    end_date: filters.end_date,
    page_size: filters.page_size || 1000,
    sort_by: filters.sort_by || "created_at",
    order: filters.order || "desc",
  });

  const response = await apiClient.get(
    "/reports/audit/export/excel",
    {
      params,
      responseType: "blob",
    }
  );

  return response;
};


/*
|--------------------------------------------------------------------------
| Error Handling
|--------------------------------------------------------------------------
*/

export const getReportsErrorMessage = (error) => {
  const status = error?.response?.status;

  let detail =
    error?.response?.data?.detail;

  if (
    typeof detail !== "string"
  ) {
    detail = "";
  }

  if (status === 400) {
    return (
      detail ||
      "The report request is invalid."
    );
  }

  if (status === 401) {
    return (
      "Your session has expired. Please log in again."
    );
  }

  if (status === 403) {
    return (
      detail ||
      "You do not have permission to access this report."
    );
  }

  if (status === 404) {
    return (
      detail ||
      "The requested report was not found."
    );
  }

  if (status === 422) {
    return (
      detail ||
      "One or more report filter values are invalid."
    );
  }

  if (status >= 500) {
    return (
      "A server error occurred while generating the report. Please try again later."
    );
  }

  return (
    detail ||
    error?.message ||
    "Unable to load the report."
  );
};


/*
|--------------------------------------------------------------------------
| File Download Helper
|--------------------------------------------------------------------------
*/

export const downloadReportFile = (
  response,
  fallbackFilename
) => {
  const blob = response?.data;

  if (!blob) {
    throw new Error(
      "The server returned an empty report file."
    );
  }

  const contentDisposition =
    response.headers?.[
      "content-disposition"
    ];

  let filename =
    fallbackFilename;

  if (contentDisposition) {
    const match =
      contentDisposition.match(
        /filename="?([^"]+)"?/i
      );

    if (match?.[1]) {
      filename = match[1];
    }
  }

  const url =
    window.URL.createObjectURL(blob);

  const link =
    document.createElement("a");

  link.href = url;
  link.download = filename;

  document.body.appendChild(link);

  link.click();

  link.remove();

  window.URL.revokeObjectURL(url);
};