import React, { useState, useEffect, useCallback } from 'react';
import { Users, Shield, Search, UserCheck, Briefcase, Building, Plus, Trash2, UserPlus, Folder } from 'lucide-react';
import { usersApi } from '../../api/users';
import { teamsApi } from '../../api/teams';
import { organizationsApi } from '../../api/organizations';
import { useAuth } from '../../context/AuthContext';
import { useNotification } from '../../context/NotificationContext';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { RoleBadge } from '../../components/common/StatusBadge';
import { EmptyState } from '../../components/common/EmptyState';
import { Modal } from '../../components/common/Modal';

export function UserManagementPage() {
  const { isAdmin } = useAuth();
  const { success, error } = useNotification();

  const [activeMainTab, setActiveMainTab] = useState('users'); // 'users' | 'teams'

  // Users state
  const [users, setUsers] = useState([]);
  const [orgMap, setOrgMap] = useState({});
  const [loadingUsers, setLoadingUsers] = useState(true);
  const [activeRoleTab, setActiveRoleTab] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');

  // Teams state
  const [teams, setTeams] = useState([]);
  const [loadingTeams, setLoadingTeams] = useState(false);
  const [showCreateTeamModal, setShowCreateTeamModal] = useState(false);
  const [teamForm, setTeamForm] = useState({ name: '', description: '', lead_id: '' });
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [showAddMemberModal, setShowAddMemberModal] = useState(false);
  const [selectedMemberUserId, setSelectedMemberUserId] = useState('');

  const loadUsers = useCallback(async () => {
    setLoadingUsers(true);
    try {
      const [list, orgs] = await Promise.all([
        usersApi.getUsers(),
        organizationsApi.getPublicList().catch(() => []),
      ]);
      const map = {};
      if (Array.isArray(orgs)) {
        orgs.forEach((o) => {
          map[o.id] = o.name;
        });
      }
      setOrgMap(map);
      setUsers(list || []);
    } catch (err) {
      error(err.message || 'Failed to fetch users');
    } finally {
      setLoadingUsers(false);
    }
  }, [error]);

  const loadTeams = useCallback(async () => {
    setLoadingTeams(true);
    try {
      const data = await teamsApi.getTeams();
      setTeams(data || []);
    } catch (err) {
      error(err.message || 'Failed to fetch teams');
    } finally {
      setLoadingTeams(false);
    }
  }, [error]);

  useEffect(() => {
    loadUsers();
  }, [loadUsers]);

  useEffect(() => {
    if (activeMainTab === 'teams') {
      loadTeams();
    }
  }, [activeMainTab, loadTeams]);

  if (!isAdmin) {
    return (
      <EmptyState
        icon={Shield}
        title="Admin Access Required"
        description="Only Administrators can access user directory and team management."
      />
    );
  }

  const roleCounts = {
    Employee: users.filter((u) => u.role === 'Employee').length,
    Reviewer: users.filter((u) => u.role === 'Reviewer').length,
    Manager: users.filter((u) => u.role === 'Manager').length,
    Administrator: users.filter((u) => u.role === 'Administrator').length,
  };

  const filteredUsers = users.filter((u) => {
    const matchesRole = activeRoleTab === 'ALL' || u.role === activeRoleTab;
    const term = searchTerm.toLowerCase().trim();
    const matchesSearch =
      !term ||
      u.full_name?.toLowerCase().includes(term) ||
      u.email?.toLowerCase().includes(term) ||
      u.department?.toLowerCase().includes(term) ||
      u.employee_id?.toLowerCase().includes(term);

    return matchesRole && matchesSearch;
  });

  const handleCreateTeam = async (e) => {
    e.preventDefault();
    if (!teamForm.name.trim()) return;
    try {
      await teamsApi.createTeam({
        name: teamForm.name.trim(),
        description: teamForm.description.trim() || null,
        lead_id: teamForm.lead_id ? Number(teamForm.lead_id) : null,
      });
      success(`Team "${teamForm.name}" created successfully`);
      setShowCreateTeamModal(false);
      setTeamForm({ name: '', description: '', lead_id: '' });
      loadTeams();
    } catch (err) {
      error(err.message || 'Failed to create team');
    }
  };

  const handleDeleteTeam = async (teamId, teamName) => {
    if (!window.confirm(`Are you sure you want to delete team "${teamName}"?`)) return;
    try {
      await teamsApi.deleteTeam(teamId);
      success(`Team "${teamName}" deleted.`);
      loadTeams();
    } catch (err) {
      error(err.message || 'Failed to delete team');
    }
  };

  const handleAddMember = async (e) => {
    e.preventDefault();
    if (!selectedTeam || !selectedMemberUserId) return;
    try {
      await teamsApi.addMember(selectedTeam.id, Number(selectedMemberUserId));
      success('Team member added.');
      setShowAddMemberModal(false);
      setSelectedMemberUserId('');
      loadTeams();
    } catch (err) {
      error(err.message || 'Failed to add member');
    }
  };

  const handleRemoveMember = async (teamId, userId) => {
    try {
      await teamsApi.removeMember(teamId, userId);
      success('Team member removed.');
      loadTeams();
    } catch (err) {
      error(err.message || 'Failed to remove member');
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Users size={26} style={{ color: 'var(--primary)' }} /> User & Team Management
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Manage organizational member identities, roles, and departmental team structures.
        </p>
      </div>

      {/* Main Tab Switcher */}
      <div style={{ display: 'flex', borderBottom: '1px solid var(--border-color)', gap: '1rem' }}>
        <button
          onClick={() => setActiveMainTab('users')}
          style={{
            padding: '0.75rem 1.25rem',
            border: 'none',
            background: 'transparent',
            borderBottom: `2px solid ${activeMainTab === 'users' ? 'var(--primary)' : 'transparent'}`,
            color: activeMainTab === 'users' ? 'var(--primary)' : 'var(--text-secondary)',
            fontWeight: activeMainTab === 'users' ? 700 : 500,
            cursor: 'pointer',
            fontSize: '0.95rem',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
          }}
        >
          <Users size={16} /> Users & Roles ({users.length})
        </button>
        <button
          onClick={() => setActiveMainTab('teams')}
          style={{
            padding: '0.75rem 1.25rem',
            border: 'none',
            background: 'transparent',
            borderBottom: `2px solid ${activeMainTab === 'teams' ? 'var(--primary)' : 'transparent'}`,
            color: activeMainTab === 'teams' ? 'var(--primary)' : 'var(--text-secondary)',
            fontWeight: activeMainTab === 'teams' ? 700 : 500,
            cursor: 'pointer',
            fontSize: '0.95rem',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
          }}
        >
          <Folder size={16} /> Team Management ({teams.length})
        </button>
      </div>

      {/* TAB 1: USERS DIRECTORY */}
      {activeMainTab === 'users' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Role Summary KPI Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div
              className="card card-interactive"
              onClick={() => setActiveRoleTab('Employee')}
              style={{
                borderColor: activeRoleTab === 'Employee' ? 'var(--primary)' : 'var(--border-color)',
                background: activeRoleTab === 'Employee' ? 'var(--bg-active)' : 'var(--bg-card)',
              }}
            >
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                Employees
              </div>
              <div style={{ fontSize: '1.75rem', fontWeight: 700, fontFamily: 'Outfit', color: 'var(--primary)', marginTop: '4px' }}>
                {roleCounts.Employee}
              </div>
            </div>

            <div
              className="card card-interactive"
              onClick={() => setActiveRoleTab('Reviewer')}
              style={{
                borderColor: activeRoleTab === 'Reviewer' ? 'var(--primary)' : 'var(--border-color)',
                background: activeRoleTab === 'Reviewer' ? 'var(--bg-active)' : 'var(--bg-card)',
              }}
            >
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                Reviewers
              </div>
              <div style={{ fontSize: '1.75rem', fontWeight: 700, fontFamily: 'Outfit', color: 'var(--info)', marginTop: '4px' }}>
                {roleCounts.Reviewer}
              </div>
            </div>

            <div
              className="card card-interactive"
              onClick={() => setActiveRoleTab('Manager')}
              style={{
                borderColor: activeRoleTab === 'Manager' ? 'var(--primary)' : 'var(--border-color)',
                background: activeRoleTab === 'Manager' ? 'var(--bg-active)' : 'var(--bg-card)',
              }}
            >
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                Managers
              </div>
              <div style={{ fontSize: '1.75rem', fontWeight: 700, fontFamily: 'Outfit', color: 'var(--purple)', marginTop: '4px' }}>
                {roleCounts.Manager}
              </div>
            </div>

            <div
              className="card card-interactive"
              onClick={() => setActiveRoleTab('Administrator')}
              style={{
                borderColor: activeRoleTab === 'Administrator' ? 'var(--primary)' : 'var(--border-color)',
                background: activeRoleTab === 'Administrator' ? 'var(--bg-active)' : 'var(--bg-card)',
              }}
            >
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
                Administrators
              </div>
              <div style={{ fontSize: '1.75rem', fontWeight: 700, fontFamily: 'Outfit', color: 'var(--warning)', marginTop: '4px' }}>
                {roleCounts.Administrator}
              </div>
            </div>
          </div>

          {/* Visual Role & Department Graphs */}
          {users.length > 0 && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
              {/* Role Distribution Bar */}
              <div className="card" style={{ padding: '1.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <h3 style={{ fontSize: '1rem', margin: 0, fontWeight: 600 }}>Workforce Role Composition</h3>
                  <span className="badge badge-secondary" style={{ fontSize: '0.72rem' }}>{users.length} Users</span>
                </div>
                <div style={{ height: '10px', display: 'flex', borderRadius: '5px', overflow: 'hidden', background: 'var(--border-color)', marginBottom: '0.75rem' }}>
                  <div style={{ width: `${(roleCounts.Employee / users.length) * 100}%`, background: 'var(--primary)' }} title={`Employees: ${roleCounts.Employee}`} />
                  <div style={{ width: `${(roleCounts.Reviewer / users.length) * 100}%`, background: 'var(--info)' }} title={`Reviewers: ${roleCounts.Reviewer}`} />
                  <div style={{ width: `${(roleCounts.Manager / users.length) * 100}%`, background: 'var(--purple)' }} title={`Managers: ${roleCounts.Manager}`} />
                  <div style={{ width: `${(roleCounts.Administrator / users.length) * 100}%`, background: 'var(--warning)' }} title={`Admins: ${roleCounts.Administrator}`} />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem', fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--primary)' }} /> Emp: {Math.round((roleCounts.Employee / users.length) * 100)}%</span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--info)' }} /> Rev: {Math.round((roleCounts.Reviewer / users.length) * 100)}%</span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--purple)' }} /> Mgr: {Math.round((roleCounts.Manager / users.length) * 100)}%</span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--warning)' }} /> Adm: {Math.round((roleCounts.Administrator / users.length) * 100)}%</span>
                </div>
              </div>

              {/* Department Distribution Bar Chart */}
              <div className="card" style={{ padding: '1.25rem' }}>
                {(() => {
                  const departmentCounts = users.reduce((acc, u) => {
                    const dept = u.department || 'General';
                    acc[dept] = (acc[dept] || 0) + 1;
                    return acc;
                  }, {});
                  const maxDeptCount = Math.max(...Object.values(departmentCounts), 1);

                  return (
                    <>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                        <h3 style={{ fontSize: '1rem', margin: 0, fontWeight: 600 }}>Department Allocation</h3>
                        <span className="badge badge-secondary" style={{ fontSize: '0.72rem' }}>{Object.keys(departmentCounts).length} Departments</span>
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        {Object.entries(departmentCounts).slice(0, 4).map(([dept, cnt], idx) => {
                          const colors = ['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#EC4899'];
                          const col = colors[idx % colors.length];
                          const pct = Math.round((cnt / maxDeptCount) * 100);
                          return (
                            <div key={dept}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '2px' }}>
                                <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{dept}</span>
                                <span style={{ color: 'var(--text-muted)' }}>{cnt} members</span>
                              </div>
                              <div style={{ height: '6px', background: 'var(--border-color)', borderRadius: '3px', overflow: 'hidden' }}>
                                <div style={{ width: `${pct}%`, height: '100%', background: col, borderRadius: '3px', transition: 'width 0.5s' }} />
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </>
                  );
                })()}
              </div>
            </div>
          )}

          {/* Search & Filters */}
          <div className="card" style={{ padding: '1rem 1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {['ALL', 'Employee', 'Reviewer', 'Manager', 'Administrator'].map((r) => (
                  <button
                    key={r}
                    onClick={() => setActiveRoleTab(r)}
                    className={`btn btn-sm ${activeRoleTab === r ? 'btn-primary' : 'btn-secondary'}`}
                  >
                    {r === 'ALL' ? 'All Roles' : `${r}s`}
                  </button>
                ))}
              </div>

              <div style={{ position: 'relative', minWidth: '240px' }}>
                <Search size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  type="text"
                  className="form-input"
                  style={{ paddingLeft: '2rem', height: '36px', fontSize: '0.85rem' }}
                  placeholder="Search by name, email, department..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
          </div>

          {/* Users Table */}
          {loadingUsers ? (
            <LoadingSpinner message="Loading user directory..." />
          ) : filteredUsers.length === 0 ? (
            <EmptyState
              title={`No ${activeRoleTab === 'ALL' ? '' : activeRoleTab} users found`}
              description="Try clearing search filters or select another role category."
            />
          ) : (
            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
              <div className="table-container" style={{ border: 'none', borderRadius: 0 }}>
                <table className="table">
                  <thead>
                    <tr>
                      <th>User Details</th>
                      <th>Role</th>
                      <th>Department</th>
                      <th>Designation</th>
                      <th>Employee ID</th>
                      <th>Organization</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.map((u) => (
                      <tr key={u.id}>
                        <td>
                          <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{u.full_name}</div>
                          <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>{u.email}</div>
                        </td>
                        <td><RoleBadge role={u.role} /></td>
                        <td>{u.department || '—'}</td>
                        <td>{u.designation || '—'}</td>
                        <td><code style={{ fontSize: '0.8rem' }}>{u.employee_id || '—'}</code></td>
                        <td>
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}>
                            <Building size={14} style={{ color: 'var(--primary)', flexShrink: 0 }} />
                            {orgMap[u.organization_id] || (u.organization_id ? `Org #${u.organization_id}` : '—')}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: TEAMS MANAGEMENT */}
      {activeMainTab === 'teams' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h2 style={{ fontSize: '1.2rem', margin: 0 }}>Organizational Teams</h2>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: '0.2rem 0 0' }}>
                Define engineering, governance, or department teams to group decisions and assign review responsibilities.
              </p>
            </div>
            <button className="btn btn-primary" onClick={() => setShowCreateTeamModal(true)}>
              <Plus size={16} /> Create Team
            </button>
          </div>

          {loadingTeams ? (
            <LoadingSpinner message="Loading teams..." />
          ) : teams.length === 0 ? (
            <EmptyState
              icon={Folder}
              title="No Teams Created"
              description="Create your first team to organize decision owners and reviewers."
              action={
                <button className="btn btn-primary btn-sm" onClick={() => setShowCreateTeamModal(true)}>
                  <Plus size={15} /> Create Team
                </button>
              }
            />
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '1.25rem' }}>
              {teams.map((t) => (
                <div
                  key={t.id}
                  className="card"
                  style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', gap: '1rem' }}
                >
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem' }}>
                      <div>
                        <h3 style={{ fontSize: '1.1rem', margin: 0, fontWeight: 700 }}>{t.name}</h3>
                        {t.description && (
                          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: '0.35rem 0 0', lineHeight: 1.4 }}>
                            {t.description}
                          </p>
                        )}
                      </div>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleDeleteTeam(t.id, t.name)}
                        style={{ color: 'var(--danger)', padding: '4px 8px' }}
                        title="Delete team"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>

                    <div style={{ marginTop: '0.85rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      <strong>Team Lead:</strong> {t.lead?.full_name || 'Unassigned'}
                    </div>

                    {/* Member Roster */}
                    <div style={{ marginTop: '0.85rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                        <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Members ({t.members?.length || 0}):</span>
                        <button
                          className="btn btn-secondary btn-sm"
                          style={{ padding: '2px 8px', fontSize: '0.75rem' }}
                          onClick={() => {
                            setSelectedTeam(t);
                            setShowAddMemberModal(true);
                          }}
                        >
                          <UserPlus size={12} /> Add
                        </button>
                      </div>

                      {(!t.members || t.members.length === 0) ? (
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                          No members in this team yet.
                        </div>
                      ) : (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                          {t.members.map((m) => (
                            <span
                              key={m.id}
                              style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '4px',
                                background: 'var(--bg-hover)',
                                border: '1px solid var(--border-color)',
                                borderRadius: '6px',
                                padding: '2px 6px',
                                fontSize: '0.75rem',
                              }}
                            >
                              {m.full_name}
                              <button
                                onClick={() => handleRemoveMember(t.id, m.id)}
                                style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: 0 }}
                                title="Remove member"
                              >
                                &times;
                              </button>
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', borderTop: '1px solid var(--border-color)', paddingTop: '0.5rem' }}>
                    Created: {new Date(t.created_at).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Create Team Modal */}
      <Modal
        isOpen={showCreateTeamModal}
        onClose={() => setShowCreateTeamModal(false)}
        title="Create New Team"
      >
        <form onSubmit={handleCreateTeam}>
          <div className="form-group">
            <label className="form-label">Team Name *</label>
            <input
              type="text"
              className="form-input"
              required
              placeholder="e.g. Core Infrastructure, Security Arch"
              value={teamForm.name}
              onChange={(e) => setTeamForm({ ...teamForm, name: e.target.value })}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea
              className="form-textarea"
              rows={3}
              placeholder="Brief description of responsibilities..."
              value={teamForm.description}
              onChange={(e) => setTeamForm({ ...teamForm, description: e.target.value })}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Team Lead</label>
            <select
              className="form-select"
              value={teamForm.lead_id}
              onChange={(e) => setTeamForm({ ...teamForm, lead_id: e.target.value })}
            >
              <option value="">-- Select Team Lead (Optional) --</option>
              {users.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.full_name} ({u.role})
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.25rem' }}>
            <button type="button" className="btn btn-secondary" onClick={() => setShowCreateTeamModal(false)}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Create Team
            </button>
          </div>
        </form>
      </Modal>

      {/* Add Member Modal */}
      <Modal
        isOpen={showAddMemberModal}
        onClose={() => setShowAddMemberModal(false)}
        title={`Add Member to ${selectedTeam?.name || 'Team'}`}
      >
        <form onSubmit={handleAddMember}>
          <div className="form-group">
            <label className="form-label">Select Employee / Reviewer</label>
            <select
              className="form-select"
              required
              value={selectedMemberUserId}
              onChange={(e) => setSelectedMemberUserId(e.target.value)}
            >
              <option value="" disabled>-- Select a User --</option>
              {users
                .filter((u) => !selectedTeam?.members?.some((m) => m.id === u.id))
                .map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.full_name} ({u.role} - {u.email})
                  </option>
                ))}
            </select>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.25rem' }}>
            <button type="button" className="btn btn-secondary" onClick={() => setShowAddMemberModal(false)}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={!selectedMemberUserId}>
              Add to Team
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
