import React, { useState } from 'react';
import {
  Sparkles,
  Plus,
  Trash2,
  Send,
  Eye,
  CheckCircle,
  AlertTriangle,
  FileText,
  Search,
  Lock,
} from 'lucide-react';
import { useAuth, UserRole } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import Alert from '../components/common/Alert';
import FormField from '../components/common/FormField';
import Input from '../components/common/Input';
import Select from '../components/common/Select';
import Textarea from '../components/common/Textarea';
import SearchInput from '../components/common/SearchInput';
import Modal from '../components/common/Modal';
import Table from '../components/common/Table';
import Pagination from '../components/common/Pagination';
import FilterBar from '../components/common/FilterBar';
import Skeleton from '../components/common/Skeleton';
import LoadingSpinner from '../components/common/LoadingSpinner';
import EmptyState from '../components/common/EmptyState';
import RoleGate from '../components/auth/RoleGate';

export const ComponentShowcasePage = () => {
  const toast = useToast();
  const { user } = useAuth();

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form Validation Demo State
  const [formData, setFormData] = useState({
    title: '',
    category: '',
    description: '',
  });
  const [formErrors, setFormErrors] = useState({});

  // Table & Filter State
  const [tableLoading, setTableLoading] = useState(false);
  const [showEmptyTable, setShowEmptyTable] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [sortColumn, setSortColumn] = useState('title');
  const [sortDirection, setSortDirection] = useState('asc');

  const demoData = [
    { id: 1, title: 'Adopt Event-Driven Architecture', category: 'Technology', status: 'Approved', risk: 'Medium', author: 'Bhargav' },
    { id: 2, title: 'Migrate to Cloud Database Cluster', category: 'Infrastructure', status: 'Under Review', risk: 'High', author: 'Reviewer Alex' },
    { id: 3, title: 'Implement Automated Audit Reporting', category: 'Compliance', status: 'Draft', risk: 'Low', author: 'Employee Dev' },
    { id: 4, title: 'Deprecate Legacy Monolith Services', category: 'Architecture', status: 'Rejected', risk: 'Critical', author: 'Manager Sarah' },
    { id: 5, title: 'Upgrade Core Encryption Modules', category: 'Security', status: 'Archived', risk: 'Low', author: 'Admin System' },
  ];

  const filteredData = demoData.filter((item) => {
    if (showEmptyTable) return false;
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) || item.category.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = !statusFilter || item.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handleFormSubmit = (e) => {
    e.preventDefault();
    const errors = {};
    if (!formData.title.trim()) errors.title = 'Decision title is required';
    if (!formData.category) errors.category = 'Please select a category';
    if (!formData.description.trim()) errors.description = 'Problem statement description is required';

    setFormErrors(errors);
    if (Object.keys(errors).length === 0) {
      toast.success('Form validated successfully!');
      setIsModalOpen(false);
      setFormData({ title: '', category: '', description: '' });
    } else {
      toast.error('Please fix validation errors in the form.');
    }
  };

  const handleSort = (columnKey) => {
    if (sortColumn === columnKey) {
      setSortDirection((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortColumn(columnKey);
      setSortDirection('asc');
    }
  };

  const tableColumns = [
    { key: 'id', header: 'ID', width: '60px' },
    {
      key: 'title',
      header: 'Title',
      sortable: true,
      render: (val, row) => (
        <div>
          <div style={{ fontWeight: 600, color: 'var(--color-ink)' }}>{val}</div>
          <div style={{ fontSize: '12px', color: 'var(--color-ink-muted-48)' }}>Created by {row.author}</div>
        </div>
      ),
    },
    {
      key: 'category',
      header: 'Category',
      sortable: true,
      render: (val) => <span style={{ color: 'var(--color-ink-muted-80)' }}>{val}</span>,
    },
    {
      key: 'status',
      header: 'Status',
      sortable: true,
      render: (val) => <Badge variant={val}>{val}</Badge>,
    },
    {
      key: 'risk',
      header: 'Risk Level',
      render: (val) => <Badge variant={val}>{val}</Badge>,
    },
    {
      key: 'actions',
      header: 'Actions',
      width: '100px',
      render: (_, row) => (
        <Button
          variant="pearl"
          size="small"
          onClick={(e) => {
            e.stopPropagation();
            toast.info(`Inspecting "${row.title}"`);
          }}
          icon={Eye}
        >
          View
        </Button>
      ),
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: '28px', fontWeight: 600, marginBottom: '6px' }}>
          Apple Design System Component Library
        </h1>
        <p style={{ fontSize: '15px', color: 'var(--color-ink-muted-48)' }}>
          Shared UI building blocks adhering to <code>DESIGN.md</code> specification, supporting reactive validation, role gates, and interactive feedback.
        </p>
      </div>

      {/* 1. BUTTONS */}
      <section className="apple-card">
        <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>
          1. Button Variants & Micro-Interactions (Click to test active scale-down)
        </h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '14px', alignItems: 'center' }}>
          <Button variant="primary" onClick={() => toast.success('Primary Action Blue button pressed!')}>
            Primary Pill
          </Button>
          <Button variant="secondary" onClick={() => toast.info('Secondary Ghost Pill pressed')}>
            Secondary Pill
          </Button>
          <Button variant="dark" icon={Sparkles} onClick={() => toast.info('Dark Utility button pressed')}>
            Dark Utility
          </Button>
          <Button variant="pearl" onClick={() => toast.info('Pearl Capsule pressed')}>
            Pearl Capsule
          </Button>
          <Button variant="danger" icon={Trash2} onClick={() => toast.warning('Danger action triggered')}>
            Danger Action
          </Button>
          <Button variant="primary" loading={true}>
            Loading State
          </Button>
          <Button variant="primary" disabled={true}>
            Disabled
          </Button>
        </div>
      </section>

      {/* 2. BADGES */}
      <section className="apple-card">
        <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>
          2. Badges & Tags (Status, Risk, and Role Variants)
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div>
            <span style={{ fontSize: '13px', fontWeight: 600, marginRight: '12px' }}>Decision Statuses:</span>
            <div style={{ display: 'inline-flex', flexWrap: 'wrap', gap: '8px' }}>
              <Badge variant="draft">Draft</Badge>
              <Badge variant="under-review">Under Review</Badge>
              <Badge variant="approved">Approved</Badge>
              <Badge variant="rejected">Rejected</Badge>
              <Badge variant="archived">Archived</Badge>
            </div>
          </div>
          <div>
            <span style={{ fontSize: '13px', fontWeight: 600, marginRight: '12px' }}>Risk Levels:</span>
            <div style={{ display: 'inline-flex', flexWrap: 'wrap', gap: '8px' }}>
              <Badge variant="low">Low Risk</Badge>
              <Badge variant="medium">Medium Risk</Badge>
              <Badge variant="high">High Risk</Badge>
              <Badge variant="critical">Critical Risk</Badge>
            </div>
          </div>
          <div>
            <span style={{ fontSize: '13px', fontWeight: 600, marginRight: '12px' }}>User Roles:</span>
            <div style={{ display: 'inline-flex', flexWrap: 'wrap', gap: '8px' }}>
              <Badge variant="employee">Employee</Badge>
              <Badge variant="reviewer">Reviewer</Badge>
              <Badge variant="manager">Manager</Badge>
              <Badge variant="administrator">Administrator</Badge>
            </div>
          </div>
        </div>
      </section>

      {/* 3. ALERTS & TOASTS */}
      <section className="apple-card">
        <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '16px' }}>
          3. Alerts & Toast Notification Triggers
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '20px' }}>
          <Alert type="success" title="Operation Succeeded">
            Decision v3 snapshot successfully committed and audited to immutable ledger.
          </Alert>
          <Alert type="warning" title="Feasibility Threshold Warning">
            Alternative feasibility score is below recommended threshold of 3.
          </Alert>
          <Alert type="error" title="403 Authorization Denied">
            Your current role does not have permission to modify this discussion thread.
          </Alert>
          <Alert type="info" title="System Notice">
            Scheduled maintenance audit exports will run at 00:00 UTC.
          </Alert>
        </div>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
          <Button variant="pearl" size="small" onClick={() => toast.success('Success notification trigger')}>
            Trigger Success Toast
          </Button>
          <Button variant="pearl" size="small" onClick={() => toast.error('API Error: 422 Invalid Status')}>
            Trigger Error Toast
          </Button>
          <Button variant="pearl" size="small" onClick={() => toast.warning('Warning: Token expires in 5m')}>
            Trigger Warning Toast
          </Button>
          <Button variant="pearl" size="small" onClick={() => toast.info('Info: Decision status updated')}>
            Trigger Info Toast
          </Button>
        </div>
      </section>

      {/* 4. MODALS & FORMS */}
      <section className="apple-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: 600 }}>4. Modal Dialogs & Form Validation</h2>
            <p style={{ fontSize: '13px', color: 'var(--color-ink-muted-48)' }}>
              Backdrop frosted glass, ESC key dismiss, field-level error mapping.
            </p>
          </div>
          <Button variant="primary" icon={Plus} onClick={() => setIsModalOpen(true)}>
            Open Sample Modal
          </Button>
        </div>

        {/* Modal Instance */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Create New Decision Proposal"
          subtitle="Define decision parameters, problem statements, and category."
          footer={
            <>
              <Button variant="pearl" onClick={() => setIsModalOpen(false)}>
                Cancel
              </Button>
              <Button variant="primary" onClick={handleFormSubmit}>
                Submit Proposal
              </Button>
            </>
          }
        >
          <form onSubmit={handleFormSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <FormField label="Decision Title" required error={formErrors.title} hint="Clear, actionable decision title">
              <Input
                placeholder="e.g. Migrate to Event-Driven Architecture"
                value={formData.title}
                onChange={(e) => {
                  setFormData((prev) => ({ ...prev, title: e.target.value }));
                  if (formErrors.title) setFormErrors((prev) => ({ ...prev, title: null }));
                }}
                error={!!formErrors.title}
              />
            </FormField>

            <FormField label="Category" required error={formErrors.category}>
              <Select
                options={['Technology', 'Infrastructure', 'Architecture', 'Security', 'Compliance', 'Operations']}
                value={formData.category}
                onChange={(e) => {
                  setFormData((prev) => ({ ...prev, category: e.target.value }));
                  if (formErrors.category) setFormErrors((prev) => ({ ...prev, category: null }));
                }}
                error={!!formErrors.category}
              />
            </FormField>

            <FormField label="Problem Statement" required error={formErrors.description}>
              <Textarea
                placeholder="Describe the context, problem statement, and objectives..."
                rows={3}
                value={formData.description}
                onChange={(e) => {
                  setFormData((prev) => ({ ...prev, description: e.target.value }));
                  if (formErrors.description) setFormErrors((prev) => ({ ...prev, description: null }));
                }}
                error={!!formErrors.description}
              />
            </FormField>
          </form>
        </Modal>
      </section>

      {/* 5. DATA TABLES, SKELETONS & EMPTY STATES */}
      <section className="apple-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
          <div>
            <h2 style={{ fontSize: '18px', fontWeight: 600 }}>5. Data Tables, Skeletons & Filter Bar</h2>
            <p style={{ fontSize: '13px', color: 'var(--color-ink-muted-48)' }}>
              Responsive table with sortable headers, filter controls, and dynamic states.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <Button
              variant="pearl"
              size="small"
              onClick={() => setTableLoading((prev) => !prev)}
            >
              {tableLoading ? 'Stop Loading' : 'Toggle Skeleton Loading'}
            </Button>
            <Button
              variant="pearl"
              size="small"
              onClick={() => setShowEmptyTable((prev) => !prev)}
            >
              {showEmptyTable ? 'Show Data' : 'Toggle Empty State'}
            </Button>
          </div>
        </div>

        <FilterBar
          searchValue={searchQuery}
          onSearchChange={setSearchQuery}
          searchPlaceholder="Search decisions by title or category..."
          filters={[
            {
              key: 'status',
              label: 'All Statuses',
              value: statusFilter,
              options: [
                { value: '', label: 'All Statuses' },
                { value: 'Draft', label: 'Draft' },
                { value: 'Under Review', label: 'Under Review' },
                { value: 'Approved', label: 'Approved' },
                { value: 'Rejected', label: 'Rejected' },
                { value: 'Archived', label: 'Archived' },
              ],
              onChange: setStatusFilter,
            },
          ]}
          onReset={() => {
            setSearchQuery('');
            setStatusFilter('');
            setShowEmptyTable(false);
          }}
        />

        <Table
          columns={tableColumns}
          data={filteredData}
          loading={tableLoading}
          sortColumn={sortColumn}
          sortDirection={sortDirection}
          onSort={handleSort}
          onRowClick={(row) => toast.info(`Clicked row #${row.id}: ${row.title}`)}
        />

        <Pagination
          currentPage={currentPage}
          totalPages={3}
          totalItems={filteredData.length}
          pageSize={5}
          onPageChange={setCurrentPage}
          onPageSizeChange={() => {}}
        />
      </section>

      {/* 6. ROLE GATE DEMONSTRATION */}
      <section className="apple-card">
        <h2 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>
          6. Role Gate Access Demonstration
        </h2>
        <p style={{ fontSize: '13px', color: 'var(--color-ink-muted-48)', marginBottom: '16px' }}>
          Currently logged in as <Badge variant="role">{user?.role || 'Guest'}</Badge>. Components below will show or hide based on role privileges.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
          <div style={{ padding: '16px', borderRadius: 'var(--radius-md)', backgroundColor: 'var(--color-surface-pearl)', border: '1px solid var(--color-hairline)' }}>
            <div style={{ fontWeight: 600, marginBottom: '6px' }}>Employee Action Zone</div>
            <p style={{ fontSize: '12px', color: 'var(--color-ink-muted-48)', marginBottom: '12px' }}>Visible to all roles</p>
            <RoleGate allowedRoles={[UserRole.EMPLOYEE, UserRole.REVIEWER, UserRole.MANAGER, UserRole.ADMINISTRATOR]}>
              <Button variant="primary" size="small">Create Proposal</Button>
            </RoleGate>
          </div>

          <div style={{ padding: '16px', borderRadius: 'var(--radius-md)', backgroundColor: 'var(--color-surface-pearl)', border: '1px solid var(--color-hairline)' }}>
            <div style={{ fontWeight: 600, marginBottom: '6px' }}>Reviewer / Manager Zone</div>
            <p style={{ fontSize: '12px', color: 'var(--color-ink-muted-48)', marginBottom: '12px' }}>Requires Reviewer, Manager, or Admin</p>
            <RoleGate
              allowedRoles={[UserRole.REVIEWER, UserRole.MANAGER, UserRole.ADMINISTRATOR]}
              fallback={<span style={{ fontSize: '12px', color: '#dc2626', display: 'flex', alignItems: 'center', gap: '4px' }}><Lock size={12}/> Role Restricted</span>}
            >
              <Button variant="secondary" size="small">Endorse / Approve Decision</Button>
            </RoleGate>
          </div>

          <div style={{ padding: '16px', borderRadius: 'var(--radius-md)', backgroundColor: 'var(--color-surface-pearl)', border: '1px solid var(--color-hairline)' }}>
            <div style={{ fontWeight: 600, marginBottom: '6px' }}>Administrator Zone</div>
            <p style={{ fontSize: '12px', color: 'var(--color-ink-muted-48)', marginBottom: '12px' }}>Requires Administrator Role</p>
            <RoleGate
              allowedRoles={[UserRole.ADMINISTRATOR]}
              fallback={<span style={{ fontSize: '12px', color: '#dc2626', display: 'flex', alignItems: 'center', gap: '4px' }}><Lock size={12}/> Role Restricted</span>}
            >
              <Button variant="dark" size="small">System Configuration</Button>
            </RoleGate>
          </div>
        </div>
      </section>
    </div>
  );
};

export default ComponentShowcasePage;
