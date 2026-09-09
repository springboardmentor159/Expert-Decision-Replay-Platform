import apiClient from "./apiClient";


// =========================================================
// ERROR HANDLER
// =========================================================

function getErrorMessage(error, fallback = "Something went wrong.") {
  const status = error?.response?.status;
  const detail = error?.response?.data?.detail;

  if (status === 400) {
    return detail || "Invalid request.";
  }

  if (status === 401) {
    return "Your session has expired. Please log in again.";
  }

  if (status === 403) {
    return detail || "You are not authorized to perform this action.";
  }

  if (status === 404) {
    return detail || "The requested resource was not found.";
  }

  if (status === 422) {
    return detail || "The submitted information is invalid.";
  }

  if (status >= 500) {
    return "A server error occurred. Please try again later.";
  }

  return detail || error?.message || fallback;
}


// =========================================================
// GET / SEARCH DECISIONS
// =========================================================

export async function getDecisions({
  search = "",
  category = "",
  status = "",
  tag = "",
  page = 1,
  pageSize = 20,
  sortBy = "created_at",
  order = "desc",
} = {}) {
  try {
    const response = await apiClient.get("/decisions/search", {
      params: {
        q: search || undefined,
        category: category || undefined,
        decision_status: status || undefined,
        tag: tag || undefined,
        page,
        page_size: pageSize,
        sort_by: sortBy,
        order,
      },
    });

    return response.data;
  } catch (error) {
    console.error("Failed to get decisions:", error);

    throw new Error(
      getErrorMessage(error, "Unable to load decisions.")
    );
  }
}


// =========================================================
// GET SINGLE DECISION
// =========================================================

export async function getDecision(decisionId) {
  try {
    const response = await apiClient.get(
      `/decisions/${decisionId}`
    );

    console.log(
      "RAW GET DECISION RESPONSE:",
      response
    );

    console.log(
      "RAW GET DECISION DATA:",
      response.data
    );

    const data = response.data;

    /*
     * Backend GET /decisions/{id} returns the Decision
     * object directly.
     *
     * We still support wrapped responses so the frontend
     * remains compatible with any existing response format.
     */

    let source = data;

    if (
      data &&
      typeof data === "object" &&
      data.decision &&
      typeof data.decision === "object"
    ) {
      source = data.decision;
    } else if (
      data &&
      typeof data === "object" &&
      data.data &&
      typeof data.data === "object"
    ) {
      source = data.data;
    }

    console.log(
      "DECISION SOURCE USED BY FRONTEND:",
      source
    );

    if (!source || typeof source !== "object") {
      throw new Error(
        "The server returned an invalid decision response."
      );
    }

    /*
     * Normalize the decision into ONE consistent structure.
     */

    const normalizedDecision = {
      id:
        source.id ??
        source.decision_id ??
        Number(decisionId),

      title:
        source.title ??
        source.name ??
        "",

      problem_statement:
        source.problem_statement ??
        source.problemStatement ??
        "",

      rationale:
        source.rationale ??
        source.decision_rationale ??
        "",

      category:
        source.category ??
        "",

      status:
        source.status?.value ??
        source.status ??
        "",

      created_by:
        source.created_by ??
        source.creator_id ??
        source.createdBy ??
        null,

      created_at:
        source.created_at ??
        source.createdAt ??
        null,

      updated_at:
        source.updated_at ??
        source.updatedAt ??
        null,
    };

    console.log(
      "NORMALIZED DECISION:",
      normalizedDecision
    );

    return normalizedDecision;

  } catch (error) {
    console.error(
      "Failed to get decision:",
      error
    );

    /*
     * If this is our own Error, preserve its message.
     * Otherwise extract the Axios error properly.
     */
    if (
      error instanceof Error &&
      !error.response
    ) {
      throw error;
    }

    throw new Error(
      getErrorMessage(
        error,
        "Unable to load the decision."
      )
    );
  }
}


// =========================================================
// CREATE DECISION
// =========================================================

export async function createDecision(decisionData) {
  try {
    const response = await apiClient.post(
      "/decisions/",
      decisionData
    );

    return response.data;
  } catch (error) {
    console.error(
      "Failed to create decision:",
      error
    );

    throw new Error(
      getErrorMessage(
        error,
        "Unable to create decision."
      )
    );
  }
}


// =========================================================
// UPDATE DECISION
// =========================================================

export async function updateDecision(
  decisionId,
  decisionData
) {
  try {
    const response = await apiClient.put(
      `/decisions/${decisionId}`,
      decisionData
    );

    return response.data;
  } catch (error) {
    console.error(
      "Failed to update decision:",
      error
    );

    throw new Error(
      getErrorMessage(
        error,
        "Unable to update decision."
      )
    );
  }
}


// =========================================================
// DELETE DECISION
// =========================================================

export async function deleteDecision(decisionId) {
  try {
    const response = await apiClient.delete(
      `/decisions/${decisionId}`
    );

    return response.data;
  } catch (error) {
    console.error(
      "Failed to delete decision:",
      error
    );

    throw new Error(
      getErrorMessage(
        error,
        "Unable to delete decision."
      )
    );
  }
}


// =========================================================
// GET DECISION VERSIONS
// =========================================================

export async function getDecisionVersions(
  decisionId
) {
  try {
    const response = await apiClient.get(
      `/decisions/${decisionId}/versions`
    );

    return response.data;
  } catch (error) {
    console.error(
      "Failed to get decision versions:",
      error
    );

    throw new Error(
      getErrorMessage(
        error,
        "Unable to load decision versions."
      )
    );
  }
}


// =========================================================
// GET SPECIFIC VERSION
// =========================================================

export async function getDecisionVersion(
  decisionId,
  versionNumber
) {
  try {
    const response = await apiClient.get(
      `/decisions/${decisionId}/versions/${versionNumber}`
    );

    return response.data;
  } catch (error) {
    console.error(
      "Failed to get decision version:",
      error
    );

    throw new Error(
      getErrorMessage(
        error,
        "Unable to load the requested decision version."
      )
    );
  }
}


// =========================================================
// GET DECISION HISTORY
// =========================================================

export async function getDecisionHistory(
  decisionId
) {
  try {
    const response = await apiClient.get(
      `/decisions/${decisionId}/history`
    );

    return response.data;
  } catch (error) {
    console.error(
      "Failed to get decision history:",
      error
    );

    throw new Error(
      getErrorMessage(
        error,
        "Unable to load decision history."
      )
    );
  }
}


// =========================================================
// GET DECISION TIMELINE
// =========================================================

export async function getDecisionTimeline(
  decisionId
) {
  try {
    const response = await apiClient.get(
      `/decisions/${decisionId}/timeline`
    );

    return response.data;
  } catch (error) {
    console.error(
      "Failed to get decision timeline:",
      error
    );

    throw new Error(
      getErrorMessage(
        error,
        "Unable to load decision timeline."
      )
    );
  }
}


// =========================================================
// COMPARE ALTERNATIVES
// =========================================================

export async function compareAlternatives(
  decisionId
) {
  try {
    const response = await apiClient.get(
      `/decisions/${decisionId}/alternatives/compare`
    );

    return response.data;
  } catch (error) {
    console.error(
      "Failed to compare alternatives:",
      error
    );

    throw new Error(
      getErrorMessage(
        error,
        "Unable to compare alternatives."
      )
    );
  }
}


// =========================================================
// GET DECISION TAGS
// =========================================================

export async function getDecisionTags(
  decisionId
) {
  try {
    const response = await apiClient.get(
      `/decisions/${decisionId}/tags`
    );

    return response.data;
  } catch (error) {
    console.error(
      "Failed to get decision tags:",
      error
    );

    throw new Error(
      getErrorMessage(
        error,
        "Unable to load decision tags."
      )
    );
  }
}


// =========================================================
// ASSIGN TAGS
// =========================================================

export async function assignTags(
  decisionId,
  tagIds
) {
  try {
    const response = await apiClient.post(
      `/decisions/${decisionId}/tags`,
      {
        tag_ids: tagIds,
      }
    );

    return response.data;
  } catch (error) {
    console.error(
      "Failed to assign tags:",
      error
    );

    throw new Error(
      getErrorMessage(
        error,
        "Unable to assign tags."
      )
    );
  }
}


// =========================================================
// REMOVE TAG
// =========================================================

export async function removeDecisionTag(
  decisionId,
  tagId
) {
  try {
    const response = await apiClient.delete(
      `/decisions/${decisionId}/tags/${tagId}`
    );

    return response.data;
  } catch (error) {
    console.error(
      "Failed to remove decision tag:",
      error
    );

    throw new Error(
      getErrorMessage(
        error,
        "Unable to remove the decision tag."
      )
    );
  }
}