import api from "./api";

export type UserRole = "Employee" | "Reviewer" | "Manager" | "Administrator";

export interface PlatformUser {
  id: number;
  full_name: string;
  email: string;
  role: UserRole;
  employee_id: string;
  department: string;
  designation: string;
  phone_number: string;
}

export interface UserCreatePayload {
  full_name: string; email: string; role: UserRole; password: string;
  employee_id: string; department: string; designation: string; phone_number: string;
}

export interface UserUpdatePayload {
  full_name?: string; email?: string; role?: UserRole; employee_id?: string;
  department?: string; designation?: string; phone_number?: string;
}

export async function getUsers(): Promise<PlatformUser[]> {
  const response = await api.get<PlatformUser[]>("/users");
  return response.data;
}

export async function createUser(payload: UserCreatePayload): Promise<PlatformUser> {
  const response = await api.post<PlatformUser>("/users", payload);
  return response.data;
}

export async function updateUser(userId: number, payload: UserUpdatePayload): Promise<PlatformUser> {
  const response = await api.put<PlatformUser>(`/users/${userId}`, payload);
  return response.data;
}

export async function deleteUser(userId: number): Promise<void> {
  await api.delete(`/users/${userId}`);
}
