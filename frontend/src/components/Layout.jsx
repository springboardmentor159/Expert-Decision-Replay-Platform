import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const navigation = {
  employee: [['/dashboard', 'Overview'], ['/decisions', 'My decisions'], ['/decisions/new', 'Create decision'], ['/repository', 'Knowledge repository']],
  reviewer: [['/dashboard', 'Review desk'], ['/decisions', 'Assigned reviews'], ['/repository', 'Knowledge repository']],
  manager: [['/dashboard', 'Manager overview'], ['/decisions', 'Team decisions'], ['/reports', 'Reports'], ['/repository', 'Knowledge repository']],
  administrator: [['/dashboard', 'Admin overview'], ['/decisions', 'All decisions'], ['/reports', 'Reports'], ['/audit', 'Audit activity'], ['/repository', 'Knowledge repository']],
};

export default function Layout() {
  const { user, role, signOut } = useAuth();
  const links = navigation[role] || navigation.employee;
  const initials = user?.full_name?.split(' ').map((part) => part[0]).join('').slice(0, 2) || 'ED';
  return <div className="min-h-screen bg-transparent lg:grid lg:grid-cols-[250px_1fr]">
    <aside className="flex min-h-0 flex-col bg-[#173b36] text-emerald-50 lg:sticky lg:top-0 lg:h-screen">
      <div className="flex items-center gap-3 border-b border-white/10 px-5 py-6"><div className="flex size-9 items-center justify-center rounded-lg bg-[#b6e3d6] font-display font-bold text-[#173b36]">↗</div><div><strong className="block font-display text-base">Decision Replay</strong><small className="text-[11px] text-emerald-100/70">Evidence-led workspace</small></div></div>
      <nav className="flex flex-1 gap-1 overflow-x-auto p-3 lg:flex-col"><span className="px-3 py-3 text-[10px] font-bold uppercase tracking-[.14em] text-emerald-100/55">Workspace</span>{links.map(([to, label]) => <NavLink key={to} to={to} className={({ isActive }) => `whitespace-nowrap rounded-lg border px-3 py-2.5 text-sm transition ${isActive ? 'border-emerald-100/30 bg-emerald-100/15 font-semibold text-white' : 'border-transparent text-emerald-50/70 hover:bg-white/10 hover:text-white'}`}>{label}</NavLink>)}</nav>
      <div className="flex items-center justify-between gap-3 border-t border-white/10 bg-black/10 p-4"><div className="flex min-w-0 items-center gap-2"><div className="flex size-9 shrink-0 items-center justify-center rounded-full bg-emerald-200 font-bold text-emerald-900">{initials}</div><div className="min-w-0"><strong className="block truncate text-sm">{user?.full_name || user?.email}</strong><small className="text-xs text-emerald-100/65">{user?.role || 'User'}</small></div></div><button className="rounded-lg border border-white/20 px-3 py-2 text-xs text-emerald-50 hover:bg-white/10" onClick={() => signOut()}>Sign out</button></div>
    </aside>
    <main className="min-w-0"><header className="sticky top-0 z-10 flex h-[68px] items-center justify-between border-b border-slate-200 bg-white/85 px-5 backdrop-blur lg:px-8"><div><span className="text-[10px] font-bold uppercase tracking-[.14em] text-emerald-700">Decision intelligence</span><strong className="block font-display text-sm text-slate-800">Make the next call easier to explain.</strong></div><span className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">{user?.role || 'Workspace'}</span></header><section className="mx-auto w-full max-w-[1400px] p-5 lg:p-8"><Outlet /></section></main>
  </div>;
}