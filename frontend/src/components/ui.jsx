export function StatusBadge({ status }) {
  const value = String(status || 'draft').toLowerCase().replaceAll('_', '-');
  const colors = { approved: 'bg-emerald-100 text-emerald-700', 'under-review': 'bg-amber-100 text-amber-700', rejected: 'bg-rose-100 text-rose-700', draft: 'bg-slate-100 text-slate-600' };
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold capitalize ${colors[value] || colors.draft}`}>{value.replaceAll('-', ' ')}</span>;
}

export function LoadingState({ label = 'Loading workspace...' }) {
  return <div className="flex min-h-40 flex-col items-center justify-center gap-3 text-center text-sm text-slate-500"><span className="size-6 animate-spin rounded-full border-3 border-emerald-100 border-t-emerald-700" />{label}</div>;
}

export function EmptyState({ title = 'Nothing here yet', message = 'Your workspace has no matching records.' }) {
  return <div className="flex min-h-40 flex-col items-center justify-center gap-2 text-center text-sm text-slate-500"><strong className="text-base text-slate-800">{title}</strong><span>{message}</span></div>;
}

export function ErrorState({ message = 'Unable to load this view.' }) {
  return <div className="flex min-h-40 flex-col items-center justify-center gap-2 rounded-xl border border-rose-200 bg-rose-50 p-6 text-center text-sm text-rose-700"><strong className="text-base">Something went wrong</strong><span>{message}</span></div>;
}

export function StatCard({ label, value, note, accent = false }) {
  return <article className={`rounded-xl border p-5 shadow-sm ${accent ? 'border-emerald-200 bg-emerald-50' : 'border-slate-200 bg-white'}`}><span className="text-sm text-slate-500">{label}</span><strong className="mt-2 block font-display text-3xl font-bold text-slate-900">{value ?? 0}</strong><small className="mt-1 block text-xs text-slate-500">{note}</small></article>;
}