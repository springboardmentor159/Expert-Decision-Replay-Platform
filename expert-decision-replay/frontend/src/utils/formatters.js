// Format date into readable format
export const formatDate = (dateValue) => {
  if (!dateValue) {
    return "N/A";
  }

  const date = new Date(dateValue);

  if (Number.isNaN(date.getTime())) {
    return "N/A";
  }

  return date.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
};

// Format date and time
export const formatDateTime = (dateValue) => {
  if (!dateValue) {
    return "N/A";
  }

  const date = new Date(dateValue);

  if (Number.isNaN(date.getTime())) {
    return "N/A";
  }

  return date.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

// Convert text into title case
export const formatTitle = (text) => {
  if (!text) {
    return "";
  }

  return text
    .toString()
    .toLowerCase()
    .replace(/\b\w/g, (character) => character.toUpperCase());
};

// Format status text
export const formatStatus = (status) => {
  if (!status) {
    return "Unknown";
  }

  return status
    .toString()
    .replace(/_/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
};

// Format role text
export const formatRole = (role) => {
  if (!role) {
    return "Unknown";
  }

  return role
    .toString()
    .replace(/_/g, " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
};

// Shorten long text
export const truncateText = (text, maxLength = 100) => {
  if (!text) {
    return "";
  }

  if (text.length <= maxLength) {
    return text;
  }

  return `${text.substring(0, maxLength)}...`;
};

// Format number
export const formatNumber = (numberValue) => {
  if (numberValue === null || numberValue === undefined) {
    return "0";
  }

  return Number(numberValue).toLocaleString("en-IN");
};