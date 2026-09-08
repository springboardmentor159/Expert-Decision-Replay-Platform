import React, { useEffect, useState } from 'react';
import { Pencil, Plus, Trash2 } from 'lucide-react';
import apiClient from '../api/client';
import { useToast } from '../context/ToastContext';
import Button from '../components/common/Button';
import Modal from '../components/common/Modal';
import Input from '../components/common/Input';
import Select from '../components/common/Select';
import FormField from '../components/common/FormField';
import Table from '../components/common/Table';
import Badge from '../components/common/Badge';

const blank = { full_name: '', email: '', password: '', employee_id: '', department: '', designation: '', phone_number: '', role: 'Employee' };
export const AdminUsersPage = () => {
  const [users, setUsers] = useState([]); const [form, setForm] = useState(blank); const [editing, setEditing] = useState(null); const [open, setOpen] = useState(false); const [loading, setLoading] = useState(true); const toast = useToast();
  const load = async () => { setLoading(true); try { const response = await apiClient.get('/users'); setUsers(response.data || []); } catch (error) { toast.error(error.formattedMessage || 'Unable to load users'); } finally { setLoading(false); } };
  useEffect(() => { load(); }, []);
  const save = async (event) => { event.preventDefault(); try { const payload = { ...form }; if (editing && !payload.password) delete payload.password; if (editing) await apiClient.put(`/users/${editing.id}`, payload); else await apiClient.post('/users', payload); setOpen(false); setEditing(null); setForm(blank); await load(); toast.success(editing ? 'User updated' : 'User created'); } catch (error) { toast.error(error.formattedMessage || 'Unable to save user'); } };
  const remove = async (id) => { if (!window.confirm('Delete this user?')) return; try { await apiClient.delete(`/users/${id}`); await load(); toast.success('User deleted'); } catch (error) { toast.error(error.formattedMessage || 'Unable to delete user'); } };
  const startEdit = (user) => { setEditing(user); setForm({ ...blank, ...user, password: '' }); setOpen(true); };
  const field = (key, label, type = 'text') => <FormField label={label}><Input type={type} value={form[key] || ''} onChange={(event) => setForm({ ...form, [key]: event.target.value })} /></FormField>;
  return <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}><div style={{ display: 'flex', justifyContent: 'space-between' }}><div><h1>User administration</h1><p style={{ color: 'var(--color-ink-muted-48)' }}>Manage accounts, roles, and profile details.</p></div><Button variant="primary" icon={Plus} onClick={() => { setEditing(null); setForm(blank); setOpen(true); }}>New user</Button></div><Table columns={[{ key: 'full_name', header: 'Name' }, { key: 'email', header: 'Email' }, { key: 'role', header: 'Role', render: (value) => <Badge variant="role">{value}</Badge> }, { key: 'department', header: 'Department' }, { key: 'actions', header: 'Actions', render: (_, row) => <div style={{ display: 'flex', gap: '6px' }}><Button variant="pearl" size="small" icon={Pencil} onClick={() => startEdit(row)}>Edit</Button><Button variant="danger" size="small" icon={Trash2} onClick={() => remove(row.id)}>Delete</Button></div> }]} data={users} loading={loading} emptyTitle="No users found" /><Modal isOpen={open} onClose={() => setOpen(false)} title={editing ? 'Edit user' : 'Create user'} footer={<><Button variant="pearl" onClick={() => setOpen(false)}>Cancel</Button><Button variant="primary" onClick={save}>Save user</Button></>}><form onSubmit={save} style={{ display: 'grid', gap: '12px' }}>{field('full_name', 'Full name')}{field('email', 'Email', 'email')}{field('password', editing ? 'New password' : 'Password', 'password')}{field('employee_id', 'Employee ID')}<FormField label="Role"><Select options={['Employee', 'Reviewer', 'Manager', 'Administrator']} value={form.role} onChange={(event) => setForm({ ...form, role: event.target.value })} /></FormField>{field('department', 'Department')}{field('designation', 'Designation')}{field('phone_number', 'Phone number')}</form></Modal></div>;
};
export default AdminUsersPage;
