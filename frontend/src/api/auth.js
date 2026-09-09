import client from "./client";

// REGISTER — POST /users/
export async function registerUser(payload) {
  // payload: { full_name, email, role, password, employee_id, department, designation, phone_number }
  const res = await client.post("/users/", payload);
  return res.data;
}

// LOGIN — POST /users/login
// Backend uses OAuth2PasswordRequestForm, which requires
// application/x-www-form-urlencoded with "username" and "password" fields.
export async function loginUser(email, password) {
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", password);

  const res = await client.post("/users/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return res.data; // { access_token, token_type }
}

// There is no /users/me endpoint on the backend. The JWT "sub" claim is the
// user id, so we decode the token client-side and then fetch that user's
// own profile (self-access is always permitted by GET /users/{id}).
export function decodeUserIdFromToken(token) {
  try {
    const payload = token.split(".")[1];
    const decoded = JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/")));
    return decoded.sub ? parseInt(decoded.sub, 10) : null;
  } catch {
    return null;
  }
}

export async function fetchUser(userId) {
  const res = await client.get(`/users/${userId}`);
  return res.data;
}
