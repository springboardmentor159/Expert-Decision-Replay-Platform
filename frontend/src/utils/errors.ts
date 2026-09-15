export function getApiErrorMessage(
  error: any,
  fallback = "Something went wrong. Please try again.",
) {
  const status = error?.response?.status;
  const detail = error?.response?.data?.detail;

  if (status === 401) {
    return "Your session has expired. Please log in again.";
  }

  if (status === 403) {
    return "You do not have permission to perform this action.";
  }

  if (status === 404) {
    return "The requested resource was not found.";
  }

  if (status === 422) {
    if (Array.isArray(detail)) {
      return detail
        .map((item: any) => {
          if (typeof item === "string") {
            return item;
          }

          return item?.msg || "Invalid input.";
        })
        .join(", ");
    }

    return detail || "Please check the entered information.";
  }

  if (typeof detail === "string") {
    return detail;
  }

  return fallback;
}