import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import { Edit3, Plus, RefreshCw, Search, ShieldCheck, Trash2, Users, X } from "lucide-react";
import Alert from "../components/Alert";
import Button from "../components/Button";
import { useAuth } from "../auth/AuthContext";
import { createUser, deleteUser, getUsers, updateUser, type PlatformUser, type UserRole } from "../services/userService";
import "./AdminUsersPage.css";

const ROLES: UserRole[] = ["Employee", "Reviewer", "Manager", "Administrator"];
const emptyForm = { full_name: "", email: "", role: "Employee" as UserRole, password: "", employee_id: "", department: "", designation: "", phone_number: "" };

function statusMessage(error: unknown, fallback: string) {
  const response = (error as { response?: { status?: number; data?: { detail?: string } } })?.response;
  if (response?.status === 401) return "Your session has expired. Please sign in again.";
  if (response?.status === 403) return "Administrator access is required for user management.";
  if (response?.status === 409) return response.data?.detail || "The email or employee ID is already in use.";
  if (response?.status === 422) return "Please check the entered user information.";
  if (response?.status && response.status >= 500) return "The server is temporarily unavailable. Please try again.";
  return response?.data?.detail || fallback;
}

export default function AdminUsersPage() {
  const { user } = useAuth();
  const [users, setUsers] = useState<PlatformUser[]>([]);
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [editing, setEditing] = useState<PlatformUser | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [isSaving, setIsSaving] = useState(false);

  const load = useCallback(async () => {
    setIsLoading(true); setError("");
    try { setUsers(await getUsers()); } catch (e) { setError(statusMessage(e, "Unable to load users.")); } finally { setIsLoading(false); }
  }, []);

  useEffect(() => { if (user?.role === "administrator") void load(); }, [user, load]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return users;
    return users.filter((item) => [item.full_name, item.email, item.employee_id, item.department, item.role].some((value) => value.toLowerCase().includes(q)));
  }, [users, query]);

  function openCreate() { setEditing(null); setForm(emptyForm); setNotice(""); setError(""); setIsOpen(true); }
  function openEdit(item: PlatformUser) { setEditing(item); setForm({ full_name: item.full_name, email: item.email, role: item.role, password: "", employee_id: item.employee_id, department: item.department, designation: item.designation, phone_number: item.phone_number }); setNotice(""); setError(""); setIsOpen(true); }

  async function submit(event: FormEvent) {
    event.preventDefault(); setError(""); setNotice("");
    if (!form.full_name.trim() || !form.email.trim() || !form.employee_id.trim() || !form.department.trim() || !form.designation.trim() || !form.phone_number.trim() || (!editing && form.password.length < 8)) { setError(editing ? "Complete all required fields." : "Complete all fields and use a password of at least 8 characters."); return; }
    setIsSaving(true);
    try {
      if (editing) {
        const updated = await updateUser(editing.id, { full_name: form.full_name.trim(), email: form.email.trim(), role: form.role, employee_id: form.employee_id.trim(), department: form.department.trim(), designation: form.designation.trim(), phone_number: form.phone_number.trim() });
        setUsers((items) => items.map((item) => item.id === updated.id ? updated : item));
        setNotice("User profile updated successfully.");
      } else {
        const created = await createUser({ ...form, full_name: form.full_name.trim(), email: form.email.trim(), employee_id: form.employee_id.trim(), department: form.department.trim(), designation: form.designation.trim(), phone_number: form.phone_number.trim() });
        setUsers((items) => [created, ...items]); setNotice("User created successfully.");
      }
      setIsOpen(false);
    } catch (e) { setError(statusMessage(e, "Unable to save the user.")); } finally { setIsSaving(false); }
  }

  async function remove(item: PlatformUser) {
    if (!window.confirm(`Delete ${item.full_name}'s account? This cannot be undone.`)) return;
    setError(""); setNotice("");
    try { await deleteUser(item.id); setUsers((items) => items.filter((candidate) => candidate.id !== item.id)); setNotice("User deleted successfully."); } catch (e) { setError(statusMessage(e, "Unable to delete the user.")); }
  }

  if (user?.role !== "administrator") return <div className="admin-users-page"><Alert variant="error">You do not have permission to access user management.</Alert></div>;

  return <div className="admin-users-page">
    <header className="admin-users-header"><div><span className="admin-users-kicker">ADMINISTRATION</span><h1>User management</h1><p>Manage platform accounts, roles, and organizational profile information.</p></div><Button onClick={openCreate}><Plus size={16} aria-hidden="true" />Add user</Button></header>
    {error && <Alert variant="error">{error}</Alert>} {notice && <Alert variant="success">{notice}</Alert>}
    <section className="admin-users-toolbar"><div className="admin-users-search"><Search size={17} aria-hidden="true" /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search name, email, employee ID, department..." aria-label="Search users" /></div><div className="admin-users-count"><Users size={16} aria-hidden="true" />{filtered.length} users</div><Button variant="secondary" onClick={() => void load()} disabled={isLoading}><RefreshCw size={15} className={isLoading ? "admin-spin" : ""} aria-hidden="true" />Refresh</Button></section>
    <section className="admin-users-card">{isLoading ? <div className="admin-users-empty">Loading user directory...</div> : filtered.length === 0 ? <div className="admin-users-empty"><Users size={28} aria-hidden="true" /><h2>No users found</h2><p>Try a different search or create a new account.</p></div> : <div className="admin-users-table-wrap"><table><thead><tr><th>User</th><th>Role</th><th>Department</th><th>Designation</th><th>Contact</th><th aria-label="Actions" /></tr></thead><tbody>{filtered.map((item) => <tr key={item.id}><td><div className="admin-user-cell"><span className="admin-user-avatar">{item.full_name.split(/\s+/).slice(0,2).map((part) => part[0]).join("").toUpperCase()}</span><div><strong>{item.full_name}</strong><span>{item.email}</span><small>{item.employee_id}</small></div></div></td><td><span className={`admin-role admin-role-${item.role.toLowerCase()}`}><ShieldCheck size={13} aria-hidden="true" />{item.role}</span></td><td>{item.department}</td><td>{item.designation}</td><td>{item.phone_number}</td><td><div className="admin-row-actions"><button type="button" onClick={() => openEdit(item)} aria-label={`Edit ${item.full_name}`}><Edit3 size={15} /></button><button type="button" onClick={() => void remove(item)} aria-label={`Delete ${item.full_name}`} disabled={item.id === user.id}><Trash2 size={15} /></button></div></td></tr>)}</tbody></table></div>}</section>
    {isOpen && <div className="admin-modal-backdrop" role="presentation" onMouseDown={(e) => { if (e.currentTarget === e.target) setIsOpen(false); }}><section className="admin-modal" role="dialog" aria-modal="true" aria-labelledby="admin-user-modal-title"><div className="admin-modal-header"><div><span className="admin-users-kicker">ACCOUNT</span><h2 id="admin-user-modal-title">{editing ? "Edit user" : "Create user"}</h2></div><button type="button" onClick={() => setIsOpen(false)} aria-label="Close"><X size={18} /></button></div><form onSubmit={submit} className="admin-user-form"><label>Full name<input value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required /></label><label>Email<input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required /></label><label>Role<select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value as UserRole })}>{ROLES.map((role) => <option key={role}>{role}</option>)}</select></label><label>Employee ID<input value={form.employee_id} onChange={(e) => setForm({ ...form, employee_id: e.target.value })} required /></label><label>Department<input value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} required /></label><label>Designation<input value={form.designation} onChange={(e) => setForm({ ...form, designation: e.target.value })} required /></label><label>Phone number<input value={form.phone_number} onChange={(e) => setForm({ ...form, phone_number: e.target.value })} required /></label>{!editing && <label>Password<input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} minLength={8} required /></label>}<div className="admin-modal-actions"><Button variant="secondary" type="button" onClick={() => setIsOpen(false)}>Cancel</Button><Button type="submit" disabled={isSaving}>{isSaving ? "Saving..." : editing ? "Save changes" : "Create user"}</Button></div></form></section></div>}
  </div>;
}
