export const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function validateRegistration(form) {
  if (!form.full_name.trim() || !form.email.trim() || !form.password || !form.confirmPassword || !form.employee_id.trim() || !form.department.trim() || !form.designation.trim() || !form.phone_number.trim()) return 'Complete all required fields.';
  if (!emailPattern.test(form.email)) return 'Enter a valid work email address.';
  if (form.password.length < 8 || form.password.length > 128) return 'Password must contain 8 to 128 characters.';
  if (form.password !== form.confirmPassword) return 'Passwords do not match.';
  return '';
}

export function validateDecision(form) {
  if (form.title.trim().length < 3) return 'Decision title must contain at least 3 characters.';
  if (form.title.trim().length > 160) return 'Decision title cannot exceed 160 characters.';
  if (form.problem_statement.trim().length < 10) return 'Problem statement must contain at least 10 characters.';
  if (form.problem_statement.trim().length > 4000) return 'Problem statement cannot exceed 4,000 characters.';
  if (form.rationale.length > 4000) return 'Rationale cannot exceed 4,000 characters.';
  return '';
}

export function validateAlternative(form) {
  const cost = Number(form.estimated_cost);
  const feasibility = Number(form.feasibility_score);
  if (!form.name.trim() || !form.description.trim() || !form.pros.trim() || !form.cons.trim()) return 'Complete the alternative name, description, pros, and cons.';
  if (!Number.isFinite(cost) || cost < 0) return 'Estimated cost must be zero or greater.';
  if (!Number.isInteger(feasibility) || feasibility < 1 || feasibility > 5) return 'Feasibility score must be an integer from 1 to 5.';
  if (!['Low', 'Medium', 'High', 'Critical'].includes(form.risk_level)) return 'Choose a valid risk level.';
  return '';
}

export function validateDateRange(startDate, endDate) {
  if (startDate && endDate && endDate < startDate) return 'End date must be on or after the start date.';
  return '';
}
