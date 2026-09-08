import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Eye, FileText, CheckCircle2, RotateCcw } from 'lucide-react';
import { useAuth, UserRole } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import apiClient from '../api/client';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import Modal from '../components/common/Modal';
import FormField from '../components/common/FormField';
import Input from '../components/common/Input';
import Select from '../components/common/Select';
import Textarea from '../components/common/Textarea';
import Table from '../components/common/Table';
import FilterBar from '../components/common/FilterBar';
import RoleGate from '../components/auth/RoleGate';

export const DecisionsPage = () => {
  const { user } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  // Modal create state
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [createLoading, setCreateLoading] = useState(false);
  const [createForm, setCreateForm] = useState({
    title: '',
    problem_statement: '',
    category: 'Technology',
  });
  const [createErrors, setCreateErrors] = useState({});

  const fetchDecisions = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (statusFilter) params.status = statusFilter;
      if (categoryFilter) params.category = categoryFilter;

      const res = await apiClient.get('/decisions', { params });
      setDecisions(res.data || []);
    } catch (err) {
      toast.error(err.formattedMessage || 'Failed to fetch decisions');
    } finally {
      setLoading(false);
    }
  }, [statusFilter, categoryFilter, toast]);

  useEffect(() => {
    fetchDecisions();
  }, [fetchDecisions]);

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    const errs = {};
    if (!createForm.title.trim()) errs.title = 'Title is required';
    if (!createForm.problem_statement.trim()) errs.problem_statement = 'Problem statement is required';
    if (!createForm.category) errs.category = 'Category is required';

    setCreateErrors(errs);
    if (Object.keys(errs).length > 0) return;

    setCreateLoading(true);
    try {
      await apiClient.post('/decisions', createForm);
      toast.success('Decision created successfully!');
      setIsCreateOpen(false);
      setCreateForm({ title: '', problem_statement: '', category: 'Technology' });
      fetchDecisions();
    } catch (err) {
      toast.error(err.formattedMessage || 'Failed to create decision');
    } finally {
      setCreateLoading(false);
    }
  };

  const filteredDecisions = decisions.filter((d) => {
    if (!searchQuery) return true;
    return (
      d.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.problem_statement.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.category.toLowerCase().includes(searchQuery.toLowerCase())
    );
  });

  const columns = [
    { key: 'id', header: 'ID', width: '70px' },
    {
      key: 'title',
      header: 'Title & Summary',
      render: (val, row) => (
        <div>
          <div style={{ fontWeight: 600, color: 'var(--color-ink)' }}>{val}</div>
          <div
            style={{
              fontSize: '13px',
              color: 'var(--color-ink-muted-48)',
              marginTop: '2px',
              maxWidth: '500px',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {row.problem_statement}
          </div>
        </div>
      ),
    },
    {
      key: 'category',
      header: 'Category',
      render: (val) => <span style={{ color: 'var(--color-ink-muted-80)' }}>{val}</span>,
    },
    {
      key: 'status',
      header: 'Status',
      render: (val) => <Badge variant={val}>{val}</Badge>,
    },
    {
      key: 'created_at',
      header: 'Created',
      render: (val) => (
        <span style={{ fontSize: '13px', color: 'var(--color-ink-muted-48)' }}>
          {val ? new Date(val).toLocaleDateString() : '—'}
        </span>
      ),
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 600 }}>Decisions Governance</h1>
          <p style={{ fontSize: '14px', color: 'var(--color-ink-muted-48)' }}>
            Track, evaluate, and audit enterprise architectural and product decisions.
          </p>
        </div>

        <Button variant="primary" icon={Plus} onClick={() => setIsCreateOpen(true)}>
          New Decision
        </Button>
      </div>

      <div className="apple-card">
        <FilterBar
          searchValue={searchQuery}
          onSearchChange={setSearchQuery}
          searchPlaceholder="Search decisions..."
          filters={[
            {
              key: 'status',
              label: 'Status',
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
            {
              key: 'category',
              label: 'Category',
              value: categoryFilter,
              options: [
                { value: '', label: 'All Categories' },
                { value: 'Technology', label: 'Technology' },
                { value: 'Infrastructure', label: 'Infrastructure' },
                { value: 'Architecture', label: 'Architecture' },
                { value: 'Security', label: 'Security' },
                { value: 'Finance', label: 'Finance' },
                { value: 'Operations', label: 'Operations' },
              ],
              onChange: setCategoryFilter,
            },
          ]}
          onReset={() => {
            setSearchQuery('');
            setStatusFilter('');
            setCategoryFilter('');
          }}
        />

        <Table
          columns={columns}
          data={filteredDecisions}
          loading={loading}
          onRowClick={(decision) => navigate(`/decisions/${decision.id}`)}
          emptyTitle="No decisions found"
          emptyDescription="Create your first decision proposal to start collaborating with reviewers."
        />
      </div>

      {/* Create Modal */}
      <Modal
        isOpen={isCreateOpen}
        onClose={() => setIsCreateOpen(false)}
        title="Propose New Decision"
        subtitle="Submit a structured decision proposal for peer review and architectural audit."
        footer={
          <>
            <Button variant="pearl" onClick={() => setIsCreateOpen(false)} disabled={createLoading}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleCreateSubmit} loading={createLoading}>
              Create Decision
            </Button>
          </>
        }
      >
        <form onSubmit={handleCreateSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <FormField label="Decision Title" required error={createErrors.title}>
            <Input
              placeholder="e.g. Implement Kafka Event Bus for Order Processing"
              value={createForm.title}
              onChange={(e) => {
                setCreateForm((prev) => ({ ...prev, title: e.target.value }));
                if (createErrors.title) setCreateErrors((prev) => ({ ...prev, title: null }));
              }}
              error={!!createErrors.title}
            />
          </FormField>

          <FormField label="Category" required error={createErrors.category}>
            <Select
              options={['Technology', 'Infrastructure', 'Architecture', 'Security', 'Finance', 'Operations']}
              value={createForm.category}
              onChange={(e) => {
                setCreateForm((prev) => ({ ...prev, category: e.target.value }));
                if (createErrors.category) setCreateErrors((prev) => ({ ...prev, category: null }));
              }}
              error={!!createErrors.category}
            />
          </FormField>

          <FormField label="Problem Statement" required error={createErrors.problem_statement}>
            <Textarea
              placeholder="Describe why this decision is necessary and the problem it resolves..."
              rows={4}
              value={createForm.problem_statement}
              onChange={(e) => {
                setCreateForm((prev) => ({ ...prev, problem_statement: e.target.value }));
                if (createErrors.problem_statement) setCreateErrors((prev) => ({ ...prev, problem_statement: null }));
              }}
              error={!!createErrors.problem_statement}
            />
          </FormField>
        </form>
      </Modal>
    </div>
  );
};

export default DecisionsPage;
