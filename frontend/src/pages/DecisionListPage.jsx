import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { decisionsApi, tagsApi } from '../services/api';
import { EmptyState, ErrorState, LoadingState, StatusBadge } from '../components/ui';

const statuses = ['', 'Draft', 'Under Review', 'Approved', 'Rejected', 'Archived'];
const categories = ['', 'Technology', 'Finance', 'Operations', 'Human Resources', 'Security', 'Product', 'Infrastructure', 'Strategy'];

export default function DecisionListPage() {
  const [params, setParams] = useSearchParams();
  const [items, setItems] = useState(null);
  const [meta, setMeta] = useState({ page: 1, total: 0, pageSize: 20 });
  const [tags, setTags] = useState([]);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const query = params.get('q') || '';
  const status = params.get('status') || '';
  const category = params.get('category') || '';
  const tag = params.get('tag') || '';
  const page = Number(params.get('page') || 1);

  async function load() {
    setError('');
    try {
      const filters = { status, category, tag, page, page_size: 20 };
      const result = query ? await decisionsApi.search(query, filters) : await decisionsApi.list(filters);
      const list = Array.isArray(result) ? result : result.items || result.results || [];
      setItems(list);
      setMeta({ page: result.page || page, total: result.total || list.length, pageSize: result.page_size || 20 });
    } catch (err) { setError(err.message); }
  }

  useEffect(() => { load(); tagsApi.list().then(setTags).catch(() => setTags([])); }, [query, status, category, tag, page]);

  function filter(event) {
    event.preventDefault();
    const values = Object.fromEntries(new FormData(event.currentTarget));
    setParams({ q: values.q, status: values.status, category: values.category, tag: values.tag, page: '1' });
  }

  async function archive(item) {
    if (!window.confirm(`Archive "${item.title}"?`)) return;
    try { await decisionsApi.delete(item.id); setNotice('Decision archived.'); load(); } catch (err) { setError(err.message); }
  }

  async function submit(item) {
    try { await decisionsApi.updateStatus(item.id, 'Under Review'); setNotice('Decision submitted for review.'); load(); } catch (err) { setError(err.message); }
  }

  if (error && !items) return <ErrorState message={error} />;
  if (!items) return <LoadingState label="Loading decisions..." />;
  return <div>
    <div className="mb-7 flex flex-wrap items-start justify-between gap-5"><div><p className="text-[11px] font-bold uppercase tracking-[.14em] text-emerald-700">Decision management</p><h1 className="mt-2 font-display text-3xl font-bold tracking-tight text-slate-900">Decisions</h1><p className="mt-2 text-sm text-slate-500">Find, update, and move important choices through review.</p></div><Link className="rounded-lg bg-emerald-700 px-4 py-2.5 text-sm font-semibold text-white hover:bg-emerald-800" to="/decisions/new">+ Create decision</Link></div>
    {notice && <div className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2.5 text-sm text-emerald-700">{notice}</div>}
    {error && <div className="mb-4 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2.5 text-sm text-rose-700">{error}</div>}
    <form className="mb-5 grid gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm md:grid-cols-[1fr_170px_170px_150px_auto]" onSubmit={filter}><input className="rounded-lg border border-slate-200 px-3 py-2 text-sm" name="q" defaultValue={query} placeholder="Search title, problem, rationale..." /><select className="rounded-lg border border-slate-200 px-3 py-2 text-sm" name="status" defaultValue={status}>{statuses.map((value) => <option key={value} value={value}>{value || 'All statuses'}</option>)}</select><select className="rounded-lg border border-slate-200 px-3 py-2 text-sm" name="category" defaultValue={category}>{categories.map((value) => <option key={value} value={value}>{value || 'All categories'}</option>)}</select><select className="rounded-lg border border-slate-200 px-3 py-2 text-sm" name="tag" defaultValue={tag}><option value="">All tags</option>{tags.map((item) => <option key={item.id} value={item.name}>{item.name}</option>)}</select><button className="rounded-lg bg-slate-800 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700">Filter</button></form>
    <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">{items.length ? <div className="overflow-x-auto"><table className="w-full min-w-[900px] text-left"><thead><tr className="border-b border-slate-100 text-[11px] uppercase tracking-wider text-slate-400"><th className="px-4 py-3">Decision title</th><th className="px-4 py-3">Category</th><th className="px-4 py-3">Created by</th><th className="px-4 py-3">Status</th><th className="px-4 py-3">Created</th><th className="px-4 py-3">Updated</th><th className="px-4 py-3">Actions</th></tr></thead><tbody>{items.map((item) => <tr className="border-b border-slate-100 last:border-0" key={item.id}><td className="px-4 py-4"><Link className="font-semibold text-slate-800 hover:text-emerald-700" to={`/decisions/${item.id}`}>{item.title}</Link><small className="mt-1 block max-w-xs truncate text-xs text-slate-500">{item.problem_statement || 'No problem statement'}</small></td><td className="px-4 py-4 text-sm text-slate-600">{item.category}</td><td className="px-4 py-4 text-sm text-slate-600">{item.created_by_name || item.creator?.full_name || `User #${item.created_by}`}</td><td className="px-4 py-4"><StatusBadge status={item.status} /></td><td className="px-4 py-4 text-sm text-slate-500">{item.created_at ? new Date(item.created_at).toLocaleDateString() : '—'}</td><td className="px-4 py-4 text-sm text-slate-500">{item.updated_at ? new Date(item.updated_at).toLocaleDateString() : '—'}</td><td className="px-4 py-4"><div className="flex flex-wrap gap-2 text-xs font-semibold"><Link className="text-emerald-700" to={`/decisions/${item.id}`}>View</Link>{item.status !== 'Archived' && <Link className="text-slate-600" to={`/decisions/${item.id}/edit`}>Edit</Link>}{item.status === 'Draft' && <button className="text-amber-700" onClick={() => submit(item)}>Submit</button>}{item.status !== 'Archived' && <button className="text-rose-700" onClick={() => archive(item)}>Delete</button>}</div></td></tr>)}</tbody></table></div> : <EmptyState title="No decisions found" message="Try changing your filters or create a new decision." />}<div className="flex items-center justify-between border-t border-slate-100 px-4 py-3 text-sm text-slate-500"><span>{meta.total} result{meta.total === 1 ? '' : 's'}</span><div className="flex gap-2"><button className="rounded border border-slate-200 px-3 py-1.5 disabled:opacity-40" disabled={page <= 1} onClick={() => setParams({ q: query, status, category, tag, page: String(page - 1) })}>Previous</button><span className="px-2 py-1.5">Page {page}</span><button className="rounded border border-slate-200 px-3 py-1.5 disabled:opacity-40" disabled={page * meta.pageSize >= meta.total} onClick={() => setParams({ q: query, status, category, tag, page: String(page + 1) })}>Next</button></div></div></section>
  </div>;
}
