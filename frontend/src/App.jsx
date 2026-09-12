import { useEffect, useMemo, useState } from "react";
import { BrowserRouter, Link, Navigate, Route, Routes, useNavigate, useParams } from "react-router-dom";
import {
  authApi, usersApi, decisionsApi, alternativesApi, commentsApi, meetingNotesApi,
  rationaleApi, tagsApi, approvalsApi, dashboardApi, activitiesApi, auditApi, reportsApi
} from "./services/api";

const ROLES = ["Employee", "Reviewer", "Manager", "Administrator"];
const STATUSES = ["Draft", "Under Review", "Approved", "Rejected", "Archived"];

function tokenPayload() {
  const token = localStorage.getItem("access_token");
  if (!token) return null;
  try {
    const part = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(atob(part));
  } catch {
    return null;
  }
}
function role() { return tokenPayload()?.role || ""; }
function userId() { return tokenPayload()?.sub || ""; }
function loggedIn() { return !!localStorage.getItem("access_token"); }
function roleLower() { return role().trim().toLowerCase(); }

function errorMessage(error, fallback = "Something went wrong.") {
  const status = error?.response?.status;
  const detail = error?.response?.data?.detail;
  if (status === 401) return "Your session is invalid or expired. Please log in again.";
  if (status === 403) return detail || "You are not authorized to perform this action.";
  if (status === 404) return detail || "The requested resource was not found.";
  if (status === 422) {
    if (Array.isArray(error?.response?.data?.detail)) {
      return error.response.data.detail.map(x => x.msg).join(", ");
    }
    return detail || "Please correct the entered information.";
  }
  if (status === 400) return detail || "The request was not accepted.";
  if (status >= 500) return "Server error. Please try again later.";
  return detail || fallback;
}

function fmt(value) {
  if (!value) return "—";
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? String(value) : d.toLocaleString();
}

function getArray(value) {
  if (Array.isArray(value)) return value;
  if (Array.isArray(value?.items)) return value.items;
  if (Array.isArray(value?.results)) return value.results;
  if (Array.isArray(value?.alternatives)) return value.alternatives;
  return [];
}

function StatusBadge({ value }) {
  return <span className={`badge ${String(value || "").toLowerCase().replaceAll(" ", "-")}`}>{value || "Unknown"}</span>;
}

function Alert({ type = "error", children }) {
  if (!children) return null;
  return <div className={`alert ${type}`}>{children}</div>;
}

function Loading({ text = "Loading..." }) { return <div className="loading">{text}</div>; }

function Empty({ text }) { return <div className="empty">{text}</div>; }

function Protected({ children, allowed }) {
  if (!loggedIn()) return <Navigate to="/login" replace />;
  if (allowed && !allowed.map(x => x.toLowerCase()).includes(roleLower())) {
    return <Navigate to="/dashboard" replace />;
  }
  return children;
}

function Nav() {
  const navigate = useNavigate();
  const r = roleLower();
  const logout = () => {
    localStorage.removeItem("access_token");
    navigate("/login", { replace: true });
  };
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">ED</div>
        <div>
          <strong>Expert Decision</strong>
          <span>Replay Platform</span>
        </div>
      </div>
      <div className="role-chip">{role() || "Guest"}</div>
      <nav className="nav">
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/decisions">Decisions</Link>
        {(r === "employee" || r === "reviewer" || r === "manager" || r === "administrator" || r === "admin") && <Link to="/repository">Knowledge Repository</Link>}
        {(r === "reviewer" || r === "manager" || r === "administrator" || r === "admin") && <Link to="/approvals">Approvals</Link>}
        {(r === "manager" || r === "administrator" || r === "admin") && <Link to="/reports">Reports</Link>}
        <Link to="/activities">Activities</Link>
        {(r === "administrator" || r === "admin") && <>
          <Link to="/users">User Management</Link>
          <Link to="/analytics">Admin Analytics</Link>
          <Link to="/audit">Audit Logs</Link>
        </>}
      </nav>
      <button className="logout" onClick={logout}>Logout</button>
    </aside>
  );
}

function Shell({ children }) {
  return (
    <div className="app-shell">
      <Nav />
      <main className="main">{children}</main>
    </div>
  );
}

function Page({ title, subtitle, actions, children }) {
  return (
    <section className="page">
      <div className="page-head">
        <div>
          <h1>{title}</h1>
          {subtitle && <p>{subtitle}</p>}
        </div>
        {actions && <div className="actions">{actions}</div>}
      </div>
      {children}
    </section>
  );
}

function Card({ title, value, children }) {
  return <div className="card stat-card"><span>{title}</span>{value !== undefined && <strong>{value}</strong>}{children}</div>;
}

function Home() {
  return (
    <div className="landing">
      <div className="landing-card">
        <div className="brand-mark large">ED</div>
        <h1>Expert Decision Replay Platform</h1>
        <p>Capture decisions, compare alternatives, collaborate, approve, audit and preserve organizational knowledge.</p>
        <div className="landing-actions">
          <Link className="button primary" to="/login">Login</Link>
          <Link className="button secondary" to="/register">Register</Link>
        </div>
      </div>
    </div>
  );
}

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();
    setError("");
    if (!email || !password) return setError("Email and password are required.");
    setLoading(true);
    try {
      const result = await authApi.login(email, password);
      localStorage.setItem("access_token", result.access_token);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(errorMessage(err, "Invalid email or password."));
    } finally { setLoading(false); }
  }

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={submit}>
        <div className="brand-mark">ED</div>
        <h1>Welcome back</h1>
        <p>Sign in to your decision workspace.</p>
        <Alert>{error}</Alert>
        <label>Email<input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" /></label>
        <label>Password<input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" /></label>
        <button className="button primary full" disabled={loading}>{loading ? "Signing in..." : "Login"}</button>
        <p className="auth-link">New user? <Link to="/register">Create an account</Link></p>
      </form>
    </div>
  );
}

function Register() {
  const navigate = useNavigate();
  const initial = { full_name:"", email:"", password:"", confirm_password:"", employee_id:"", department:"", designation:"", phone_number:"" };
  const [form, setForm] = useState(initial);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  function change(e) { setForm({...form, [e.target.name]: e.target.value}); }

  async function submit(e) {
    e.preventDefault(); setError(""); setSuccess("");
    const required = ["full_name","email","password","confirm_password","employee_id","department","designation","phone_number"];
    if (required.some(k => !form[k].trim())) return setError("Please fill in all fields.");
    if (form.password.length < 6) return setError("Password must be at least 6 characters.");
    if (form.password !== form.confirm_password) return setError("Passwords do not match.");
    setLoading(true);
    try {
      const payload = {...form};
      delete payload.confirm_password;
      await authApi.register(payload);
      setSuccess("Registration successful. Redirecting to login...");
      setTimeout(() => navigate("/login"), 1000);
    } catch (err) { setError(errorMessage(err, "Registration failed.")); }
    finally { setLoading(false); }
  }

  return (
    <div className="auth-page">
      <form className="auth-card wide" onSubmit={submit}>
        <div className="brand-mark">ED</div><h1>Create account</h1>
        <p>New registrations receive the Employee role through the public registration API.</p>
        <Alert>{error}</Alert><Alert type="success">{success}</Alert>
        <div className="form-grid">
          {[
            ["full_name","Full Name","text"],["email","Email","email"],["employee_id","Employee ID","text"],
            ["department","Department","text"],["designation","Designation","text"],["phone_number","Phone Number","tel"],
            ["password","Password","password"],["confirm_password","Confirm Password","password"]
          ].map(([name,label,type]) =>
            <label key={name}>{label}<input type={type} name={name} value={form[name]} onChange={change} /></label>
          )}
        </div>
        <button className="button primary full" disabled={loading}>{loading ? "Registering..." : "Register"}</button>
        <p className="auth-link">Already registered? <Link to="/login">Login</Link></p>
      </form>
    </div>
  );
}

function Dashboard() {
  const r = roleLower();
  if (r === "administrator" || r === "admin") return <AdminDashboard />;
  if (r === "manager") return <ManagerDashboard />;
  if (r === "reviewer") return <ReviewerDashboard />;
  return <EmployeeDashboard />;
}

function DashboardLayout({ title, subtitle, children }) {
  return <Shell><Page title={title} subtitle={subtitle}>{children}</Page></Shell>;
}

function EmployeeDashboard() {
  const [data, setData] = useState(null), [activities, setActivities] = useState([]), [error, setError] = useState(""), [loading, setLoading] = useState(true);
  useEffect(() => {
    Promise.all([dashboardApi.employee(), dashboardApi.employeeActivities()])
      .then(([a,b]) => {setData(a); setActivities(getArray(b));})
      .catch(e => setError(errorMessage(e)))
      .finally(() => setLoading(false));
  }, []);
  if (loading) return <Shell><Loading text="Loading employee dashboard..." /></Shell>;
  return <DashboardLayout title="Employee Dashboard" subtitle="Your decisions, status and recent activity.">
    <Alert>{error}</Alert>
    {data && <div className="stats">
      <Card title="My Decisions" value={data.total_decisions}/>
      <Card title="Draft" value={data.draft_decisions}/>
      <Card title="Under Review" value={data.under_review_decisions}/>
      <Card title="Approved" value={data.approved_decisions}/>
      <Card title="Rejected" value={data.rejected_decisions}/>
      <Card title="Archived" value={data.archived_decisions}/>
      <Card title="Pending Approvals" value={data.pending_approvals}/>
    </div>}
    <Panel title="Recent Activities">
      {activities.length ? <ActivityTable rows={activities}/> : <Empty text="No recent activities."/>}
    </Panel>
  </DashboardLayout>;
}

function ReviewerDashboard() {
  const [pending,setPending] = useState([]), [decisions,setDecisions] = useState([]), [error,setError] = useState(""), [loading,setLoading] = useState(true);
  useEffect(() => {
    Promise.all([approvalsApi.pending(), decisionsApi.list({page:1,limit:10,sort_by:"created_at",sort_order:"desc"})])
      .then(([a,d]) => {setPending(getArray(a)); setDecisions(getArray(d));})
      .catch(e => setError(errorMessage(e)))
      .finally(() => setLoading(false));
  }, []);
  if (loading) return <Shell><Loading text="Loading reviewer dashboard..." /></Shell>;
  return <DashboardLayout title="Reviewer Dashboard" subtitle="Review assigned approvals and inspect decisions.">
    <Alert>{error}</Alert>
    <div className="stats">
      <Card title="Pending Reviews" value={pending.length}/>
      <Card title="Recent Decisions" value={decisions.length}/>
    </div>
    <Panel title="Pending Reviews">
      {pending.length ? <ApprovalTable rows={pending} onRefresh={async()=>{const a=await approvalsApi.pending();setPending(getArray(a));}} /> : <Empty text="No pending reviews."/>}
    </Panel>
  </DashboardLayout>;
}

function ManagerDashboard() {
  const [data,setData]=useState(null), [pending,setPending]=useState([]), [stats,setStats]=useState(null), [activities,setActivities]=useState([]), [error,setError]=useState(""), [loading,setLoading]=useState(true);
  useEffect(() => {
    Promise.all([dashboardApi.manager(),dashboardApi.managerPending(),dashboardApi.managerStats(),dashboardApi.managerActivities()])
      .then(([a,b,c,d])=>{setData(a);setPending(getArray(b));setStats(c);setActivities(getArray(d));})
      .catch(e=>setError(errorMessage(e))).finally(()=>setLoading(false));
  },[]);
  if(loading)return <Shell><Loading text="Loading manager dashboard..." /></Shell>;
  return <DashboardLayout title="Manager Dashboard" subtitle={`Team overview${data?.department ? ` • ${data.department}` : ""}.`}>
    <Alert>{error}</Alert>
    <div className="stats">
      <Card title="Team Decisions" value={data?.total_decisions ?? stats?.total_decisions ?? 0}/>
      <Card title="Draft" value={data?.draft_decisions ?? stats?.draft_decisions ?? 0}/>
      <Card title="Under Review" value={data?.under_review_decisions ?? stats?.under_review_decisions ?? 0}/>
      <Card title="Approved" value={data?.approved_decisions ?? stats?.approved_decisions ?? 0}/>
      <Card title="Rejected" value={data?.rejected_decisions ?? stats?.rejected_decisions ?? 0}/>
      <Card title="Pending Approvals" value={pending.length}/>
    </div>
    <Panel title="Pending Approvals">{pending.length ? <ApprovalTable rows={pending}/> : <Empty text="No pending team approvals."/>}</Panel>
    <Panel title="Recent Team Activities">{activities.length ? <ActivityTable rows={activities}/> : <Empty text="No recent team activities."/>}</Panel>
  </DashboardLayout>;
}

function AdminDashboard() {
  const [data,setData]=useState(null), [activities,setActivities]=useState([]), [error,setError]=useState(""), [loading,setLoading]=useState(true);
  useEffect(() => {
    Promise.all([dashboardApi.admin(),dashboardApi.adminActivities()])
      .then(([a,b])=>{setData(a);setActivities(getArray(b));})
      .catch(e=>setError(errorMessage(e)))
      .finally(()=>setLoading(false));
  },[]);
  if(loading)return <Shell><Loading text="Loading administrator dashboard..." /></Shell>;
  return <DashboardLayout title="Administrator Dashboard" subtitle="Organization-wide analytics and system activity.">
    <Alert>{error}</Alert>
    {error && <div className="warning-box">If this is the old Administrator account, check that the database/JWT role is <strong>Administrator</strong> or <strong>Admin</strong>. The backend explicitly accepts both roles for the admin dashboard.</div>}
    {data && <div className="stats">
      <Card title="Total Users" value={data.system_analytics?.total_users ?? 0}/>
      <Card title="Total Decisions" value={data.system_analytics?.total_decisions ?? 0}/>
      <Card title="Total Approvals" value={data.approval_statistics?.total_approvals ?? 0}/>
      <Card title="Pending Approvals" value={data.approval_statistics?.pending_approvals ?? 0}/>
      <Card title="Approved Approvals" value={data.approval_statistics?.approved_approvals ?? 0}/>
      <Card title="Rejected Approvals" value={data.approval_statistics?.rejected_approvals ?? 0}/>
      <Card title="Approved Decisions" value={data.decision_status_statistics?.approved ?? 0}/>
      <Card title="Rejected Decisions" value={data.decision_status_statistics?.rejected ?? 0}/>
    </div>}
    <Panel title="Recent Administrator Activity">{activities.length ? <ActivityTable rows={activities}/> : <Empty text="No recent activities."/>}</Panel>
  </DashboardLayout>;
}

function Panel({title,children,actions}) { return <div className="panel"><div className="panel-head"><h2>{title}</h2>{actions}</div>{children}</div>; }

function ActivityTable({rows}) {
  return <div className="table-wrap"><table><thead><tr><th>Action</th><th>Entity</th><th>Description</th><th>Date</th></tr></thead><tbody>
    {rows.map((x,i)=><tr key={x.id ?? i}><td>{x.action}</td><td>{x.entity_type}{x.entity_id ? ` #${x.entity_id}` : ""}</td><td>{x.description || "—"}</td><td>{fmt(x.created_at)}</td></tr>)}
  </tbody></table></div>;
}

function ApprovalTable({rows,onRefresh}) {
  const [busy,setBusy]=useState(null), [error,setError]=useState("");
  async function act(id,status) {
    setBusy(id);setError("");
    try { await approvalsApi.action(id,status); await onRefresh?.(); }
    catch(e){setError(errorMessage(e));}
    finally { setBusy(null); }
  }
  return <><Alert>{error}</Alert><div className="table-wrap"><table><thead><tr><th>ID</th><th>Decision</th><th>Level</th><th>Status</th><th>Reviewer</th><th>Action</th></tr></thead><tbody>
    {rows.map(x=><tr key={x.id ?? x.approval_id}>
      <td>{x.id ?? x.approval_id}</td><td>{x.decision || x.decision_id}</td><td>{x.approval_level}</td><td><StatusBadge value={x.status || x.current_status}/></td><td>{x.reviewer_id ?? x.assigned_reviewer ?? "—"}</td>
      <td>{(x.status || x.current_status)==="Pending" ? <><button className="small success" disabled={busy===(x.id ?? x.approval_id)} onClick={()=>act(x.id ?? x.approval_id,"Approved")}>Approve</button>{" "}<button className="small danger" disabled={busy===(x.id ?? x.approval_id)} onClick={()=>act(x.id ?? x.approval_id,"Rejected")}>Reject</button></> : "Completed"}</td>
    </tr>)}
  </tbody></table></div></>;
}

function Decisions() {
  const [items,setItems]=useState([]),[search,setSearch]=useState(""),[status,setStatus]=useState(""),[category,setCategory]=useState(""),[tag,setTag]=useState(""),[page,setPage]=useState(1),[loading,setLoading]=useState(true),[error,setError]=useState("");
  async function load(p=page) {
    setLoading(true);setError("");
    try { const result=await decisionsApi.list({search:search||undefined,status:status||undefined,category:category||undefined,tag:tag||undefined,page:p,limit:10,sort_by:"created_at",sort_order:"desc"}); setItems(getArray(result)); }
    catch(e){setError(errorMessage(e));}
    finally{setLoading(false);}
  }
  useEffect(()=>{load(1);},[]);
  return <Shell><Page title="Decisions" subtitle="Create, search, filter and manage organizational decisions." actions={<Link className="button primary" to="/decisions/create">+ Create Decision</Link>}>
    <Panel title="Search & Filters">
      <form className="filter-grid" onSubmit={e=>{e.preventDefault();setPage(1);load(1);}}>
        <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search title or problem..." />
        <select value={status} onChange={e=>setStatus(e.target.value)}><option value="">All statuses</option>{STATUSES.map(s=><option key={s}>{s}</option>)}</select>
        <input value={category} onChange={e=>setCategory(e.target.value)} placeholder="Category" />
        <input value={tag} onChange={e=>setTag(e.target.value)} placeholder="Tag" />
        <button className="button primary">Apply</button>
        <button type="button" className="button secondary" onClick={()=>{setSearch("");setStatus("");setCategory("");setTag("");setPage(1);setTimeout(()=>load(1),0);}}>Clear</button>
      </form>
    </Panel>
    {loading ? <Loading text="Loading decisions..." /> : error ? <><Alert>{error}</Alert><button className="button secondary" onClick={()=>load(page)}>Try Again</button></> :
      items.length ? <div className="decision-grid">{items.map(d=><div className="decision-card" key={d.id}>
        <div className="card-top"><StatusBadge value={d.status}/><span>#{d.id}</span></div>
        <h3>{d.title}</h3><p>{d.problem_statement}</p>
        <div className="meta"><span>{d.category}</span><span>Created {fmt(d.created_at)}</span></div>
        <Link className="button secondary" to={`/decisions/${d.id}`}>View Details</Link>
      </div>)}</div> : <Empty text="No decisions found."/>}
    <div className="pagination"><button disabled={page<=1} onClick={()=>{setPage(page-1);load(page-1)}}>Previous</button><span>Page {page}</span><button disabled={items.length<10} onClick={()=>{setPage(page+1);load(page+1)}}>Next</button></div>
  </Page></Shell>;
}

function CreateDecision() {
  const navigate=useNavigate(); const [form,setForm]=useState({title:"",problem_statement:"",category:""}); const [error,setError]=useState(""); const [loading,setLoading]=useState(false);
  async function submit(e){e.preventDefault();setError("");if(Object.values(form).some(v=>!v.trim()))return setError("All decision fields are required.");setLoading(true);try{const d=await decisionsApi.create(form);navigate(`/decisions/${d.id}`)}catch(e){setError(errorMessage(e))}finally{setLoading(false)}}
  return <Shell><Page title="Create Decision" subtitle="Create a decision. The backend assigns the authenticated user and Draft status."><Panel title="Decision Information">
    <form onSubmit={submit} className="form-stack"><label>Title<input value={form.title} onChange={e=>setForm({...form,title:e.target.value})}/></label><label>Problem Statement<textarea rows="6" value={form.problem_statement} onChange={e=>setForm({...form,problem_statement:e.target.value})}/></label><label>Category<input value={form.category} onChange={e=>setForm({...form,category:e.target.value})}/></label><Alert>{error}</Alert><div><button className="button primary" disabled={loading}>{loading?"Creating...":"Create Decision"}</button>{" "}<Link className="button secondary" to="/decisions">Cancel</Link></div></form>
  </Panel></Page></Shell>;
}

function DecisionDetails() {
  const {decisionId}=useParams();
  const [decision,setDecision]=useState(null),[alternatives,setAlternatives]=useState([]),[comparison,setComparison]=useState(null),[comments,setComments]=useState([]),[notes,setNotes]=useState([]),[rationale,setRationale]=useState(null),[decisionTags,setDecisionTags]=useState([]),[allTags,setAllTags]=useState([]),[approvals,setApprovals]=useState([]),[versions,setVersions]=useState([]),[history,setHistory]=useState([]),[users,setUsers]=useState([]),[error,setError]=useState(""),[loading,setLoading]=useState(true);
  const [edit,setEdit]=useState(false),[editForm,setEditForm]=useState({title:"",problem_statement:"",category:""}),[status,setStatus]=useState(""),[rationaleText,setRationaleText]=useState("");
  const [alt,setAlt]=useState({name:"",description:"",pros:"",cons:"",estimated_cost:"",feasibility_score:5,risk_level:"Low"}),[editingAlt,setEditingAlt]=useState(null);
  const [comment,setComment]=useState(""),[editingComment,setEditingComment]=useState(null),[commentEdit,setCommentEdit]=useState("");
  const [note,setNote]=useState({title:"",content:"",meeting_date:""}),[editingNote,setEditingNote]=useState(null);
  const [tagId,setTagId]=useState(""),[newTag,setNewTag]=useState(""),[approval,setApproval]=useState({reviewer_id:"",approval_level:1});

  async function loadAll(){
    setLoading(true);setError("");
    const jobs=[
      decisionsApi.get(decisionId),alternativesApi.list(decisionId),alternativesApi.compare(decisionId),
      commentsApi.list(decisionId),meetingNotesApi.list(decisionId),rationaleApi.get(decisionId),
      tagsApi.getDecisionTags(decisionId),tagsApi.list(),approvalsApi.list(),decisionsApi.versions(decisionId),
      decisionsApi.history(decisionId),usersApi.list()
    ];
    const r=await Promise.allSettled(jobs);
    if(r[0].status==="rejected"){setError(errorMessage(r[0].reason,"Unable to load decision."));setLoading(false);return;}
    const val=i=>r[i].status==="fulfilled"?r[i].value:null;
    const d=val(0);setDecision(d);setEditForm({title:d.title||"",problem_statement:d.problem_statement||"",category:d.category||""});setStatus(d.status||"");
    setAlternatives(getArray(val(1)));setComparison(val(2));setComments(getArray(val(3)));setNotes(getArray(val(4)));setRationale(val(5));
    setRationaleText(val(5)?.rationale||"");setDecisionTags(getArray(val(6)));setAllTags(getArray(val(7)));setApprovals(getArray(val(8)).filter(a=>Number(a.decision_id)===Number(decisionId)));
    setVersions(getArray(val(9)));setHistory(getArray(val(10)));setUsers(getArray(val(11)));
    setLoading(false);
  }
  useEffect(()=>{loadAll()},[decisionId]);

  async function run(fn, successRefresh=true){try{await fn();if(successRefresh)await loadAll();}catch(e){setError(errorMessage(e));}}
  async function saveDecision(e){e.preventDefault();await run(()=>decisionsApi.update(decisionId,editForm));setEdit(false)}
  async function changeStatus(){await run(()=>decisionsApi.updateStatus(decisionId,status))}
  async function saveRationale(){await run(()=>rationaleApi.update(decisionId,rationaleText))}
  async function saveAlt(e){
    e.preventDefault();
    if([alt.name,alt.description,alt.pros,alt.cons,alt.estimated_cost].some(v=>String(v ?? "").trim()==="")) {
      setError("Please complete all alternative fields.");
      return;
    }
    const cost=Number(alt.estimated_cost), score=Number(alt.feasibility_score);
    if(!Number.isFinite(cost) || cost<0 || !Number.isInteger(cost)) { setError("Estimated cost must be a non-negative whole number."); return; }
    if(!Number.isFinite(score) || score<1 || score>5 || !Number.isInteger(score)) { setError("Feasibility score must be a whole number from 1 to 5."); return; }
    const payload={...alt,estimated_cost:cost,feasibility_score:score};
    await run(()=>editingAlt?alternativesApi.update(editingAlt,payload):alternativesApi.create(decisionId,payload));
    setEditingAlt(null);
    setAlt({name:"",description:"",pros:"",cons:"",estimated_cost:"",feasibility_score:5,risk_level:"Low"});
  }
  async function saveComment(e){e.preventDefault();if(!comment.trim())return;await run(()=>commentsApi.create(decisionId,{content:comment}));setComment("")}
  async function saveCommentEdit(id){await run(()=>commentsApi.update(id,{content:commentEdit}));setEditingComment(null)}
  async function saveNote(e){
    e.preventDefault();
    if(!note.title.trim() || !note.content.trim() || !note.meeting_date) {
      setError("Meeting note title, content and meeting date are required.");
      return;
    }
    const meetingDate=new Date(note.meeting_date);
    if(Number.isNaN(meetingDate.getTime())) { setError("Please enter a valid meeting date."); return; }
    const payload={...note,meeting_date:meetingDate.toISOString()};
    await run(()=>editingNote?meetingNotesApi.update(editingNote,payload):meetingNotesApi.create(decisionId,payload));
    setEditingNote(null);
    setNote({title:"",content:"",meeting_date:""});
  }
  async function addTag(){if(tagId)await run(()=>tagsApi.addToDecision(decisionId,Number(tagId)))}
  async function createAndAddTag(){if(!newTag.trim())return;try{const t=await tagsApi.create(newTag.trim());await tagsApi.addToDecision(decisionId,t.id);setNewTag("");await loadAll()}catch(e){setError(errorMessage(e))}}
  async function createApproval(e){e.preventDefault();await run(()=>approvalsApi.create({decision_id:Number(decisionId),reviewer_id:Number(approval.reviewer_id),approval_level:Number(approval.approval_level)}));setApproval({reviewer_id:"",approval_level:1})}

  if(loading)return <Shell><Loading text="Loading decision information, alternatives, discussion, meeting notes and history..." /></Shell>;
  if(!decision)return <Shell><Page title="Decision"><Alert>{error||"Decision not found."}</Alert><Link className="button secondary" to="/decisions">Back</Link></Page></Shell>;

  return <Shell><Page title={decision.title} subtitle={`Decision #${decision.id} • ${decision.category}`} actions={<Link className="button secondary" to="/decisions">← Back to Decisions</Link>}>
    <Alert>{error}</Alert>

    <Panel title="Decision Information" actions={<button className="button secondary" onClick={()=>setEdit(!edit)}>{edit?"Cancel Edit":"Edit Decision"}</button>}>
      {!edit ? <div className="info-grid">
        <div><b>Status</b><StatusBadge value={decision.status}/></div><div><b>Decision ID</b><span>#{decision.id}</span></div>
        <div><b>Created By</b><span>{decision.created_by ?? "—"}</span></div><div><b>Created</b><span>{fmt(decision.created_at)}</span></div>
        <div><b>Updated</b><span>{fmt(decision.updated_at)}</span></div><div><b>Category</b><span>{decision.category}</span></div>
        <div className="full"><b>Problem Statement</b><p>{decision.problem_statement}</p></div>
      </div> :
      <form onSubmit={saveDecision} className="form-stack"><label>Title<input required value={editForm.title} onChange={e=>setEditForm({...editForm,title:e.target.value})}/></label><label>Problem Statement<textarea required rows="5" value={editForm.problem_statement} onChange={e=>setEditForm({...editForm,problem_statement:e.target.value})}/></label><label>Category<input required value={editForm.category} onChange={e=>setEditForm({...editForm,category:e.target.value})}/></label><button className="button primary">Save Changes</button></form>}
      <div className="inline-form"><select value={status} onChange={e=>setStatus(e.target.value)}>{STATUSES.map(s=><option key={s}>{s}</option>)}</select><button className="button secondary" onClick={changeStatus}>Update Status</button></div>
    </Panel>

    <Panel title="Decision Rationale"><textarea rows="4" value={rationaleText} onChange={e=>setRationaleText(e.target.value)} placeholder="Why was this decision made?"/><button className="button primary" onClick={saveRationale}>Save Rationale</button>{rationale?.updated_at&&<small>Updated {fmt(rationale.updated_at)}</small>}</Panel>

    <Panel title="Tags">
      <div className="tag-list">{decisionTags.map(t=><span className="tag" key={t.id}>{t.name}<button onClick={()=>run(()=>tagsApi.removeFromDecision(decisionId,t.id))}>×</button></span>)}</div>
      <div className="inline-form"><select value={tagId} onChange={e=>setTagId(e.target.value)}><option value="">Select existing tag</option>{allTags.filter(t=>!decisionTags.some(x=>x.id===t.id)).map(t=><option key={t.id} value={t.id}>{t.name}</option>)}</select><button className="button secondary" onClick={addTag}>Add Tag</button><input value={newTag} onChange={e=>setNewTag(e.target.value)} placeholder="New tag"/><button className="button secondary" onClick={createAndAddTag}>Create & Add</button></div>
    </Panel>

    <Panel title="Alternatives" actions={<span>{alternatives.length} option(s)</span>}>
      <form onSubmit={saveAlt} className="form-grid">
        {["name","description","pros","cons"].map(k=><label key={k}>{k.replace("_"," ").replace(/\b\w/g,m=>m.toUpperCase())}<input required value={alt[k]} onChange={e=>setAlt({...alt,[k]:e.target.value})}/></label>)}
        <label>Estimated Cost<input required type="number" min="0" step="1" value={alt.estimated_cost} onChange={e=>setAlt({...alt,estimated_cost:e.target.value})}/></label>
        <label>Feasibility (1–5)<input type="number" min="1" max="5" value={alt.feasibility_score} onChange={e=>setAlt({...alt,feasibility_score:e.target.value})}/></label>
        <label>Risk Level<select value={alt.risk_level} onChange={e=>setAlt({...alt,risk_level:e.target.value})}>{["Low","Medium","High","Critical"].map(x=><option key={x}>{x}</option>)}</select></label>
        <div className="form-actions"><button className="button primary">{editingAlt?"Update Alternative":"Add Alternative"}</button>{editingAlt&&<button type="button" className="button secondary" onClick={()=>setEditingAlt(null)}>Cancel</button>}</div>
      </form>
      {alternatives.length ? <div className="table-wrap"><table><thead><tr><th>Name</th><th>Cost</th><th>Feasibility</th><th>Risk</th><th>Pros/Cons</th><th>Action</th></tr></thead><tbody>{alternatives.map(a=><tr key={a.id}><td><b>{a.name}</b><br/>{a.description}</td><td>{a.estimated_cost}</td><td>{a.feasibility_score}/5</td><td>{a.risk_level}</td><td><div><b>Pros:</b> {a.pros}</div><div><b>Cons:</b> {a.cons}</div></td><td><button className="small" onClick={()=>{setEditingAlt(a.id);setAlt({name:a.name||"",description:a.description||"",pros:a.pros||"",cons:a.cons||"",estimated_cost:a.estimated_cost||"",feasibility_score:a.feasibility_score||5,risk_level:a.risk_level||"Low"})}}>Edit</button></td></tr>)}</tbody></table></div> : <Empty text="No alternatives yet. Add the first option above."/>}
    </Panel>

    <Panel title="Alternative Comparison">
      {getArray(comparison).length ? <div className="table-wrap"><table><thead><tr><th>Alternative</th><th>Cost</th><th>Feasibility</th><th>Risk</th></tr></thead><tbody>{getArray(comparison).map((a,i)=><tr key={a.id||i}><td>{a.name}</td><td>{a.estimated_cost}</td><td>{a.feasibility_score}/5</td><td>{a.risk_level}</td></tr>)}</tbody></table></div> : <Empty text="Add alternatives to compare them."/>}
    </Panel>

    <Panel title="Discussion / Comments">
      <form onSubmit={saveComment} className="inline-form"><input className="grow" value={comment} onChange={e=>setComment(e.target.value)} placeholder="Write a comment..."/><button className="button primary">Add Comment</button></form>
      {comments.length ? <div className="comment-list">{comments.map(c=><div className="comment" key={c.id}><div className="comment-head"><b>User #{c.user_id}</b><span>{fmt(c.created_at)}</span></div>{editingComment===c.id?<><textarea value={commentEdit} onChange={e=>setCommentEdit(e.target.value)}/><button className="small success" onClick={()=>saveCommentEdit(c.id)}>Save</button></>:<p>{c.content}</p>}<div className="comment-actions">{Number(c.user_id)===Number(userId())&&<><button className="small" onClick={()=>{setEditingComment(c.id);setCommentEdit(c.content)}}>Edit</button>{" "}<button className="small danger" onClick={()=>run(()=>commentsApi.remove(c.id))}>Delete</button></>}</div></div>)}</div> : <Empty text="No comments yet. Start the discussion above."/>}
    </Panel>

    <Panel title="Meeting Notes">
      <form onSubmit={saveNote} className="form-grid"><label>Title<input value={note.title} onChange={e=>setNote({...note,title:e.target.value})}/></label><label>Meeting Date<input required type="datetime-local" value={note.meeting_date} onChange={e=>setNote({...note,meeting_date:e.target.value})}/></label><label className="full">Content<textarea required rows="4" value={note.content} onChange={e=>setNote({...note,content:e.target.value})}/></label><div className="form-actions"><button className="button primary">{editingNote?"Update Note":"Add Meeting Note"}</button>{editingNote&&<button type="button" className="button secondary" onClick={()=>setEditingNote(null)}>Cancel</button>}</div></form>
      {notes.length ? <div className="note-list">{notes.map(n=><div className="note" key={n.id}><div className="comment-head"><b>{n.title}</b><span>{fmt(n.meeting_date)}</span></div><p>{n.content}</p><small>Created by #{n.created_by}</small>{Number(n.created_by)===Number(userId())&&<div><button className="small" onClick={()=>{setEditingNote(n.id);setNote({title:n.title,content:n.content,meeting_date:new Date(n.meeting_date).toISOString().slice(0,16)})}}>Edit</button>{" "}<button className="small danger" onClick={()=>run(()=>meetingNotesApi.remove(n.id))}>Delete</button></div>}</div>)}</div> : <Empty text="No meeting notes yet."/>}
    </Panel>

    <Panel title="Approvals">
      {approvals.length ? <ApprovalTable rows={approvals} onRefresh={loadAll}/> : <Empty text="No approvals assigned to this decision."/>}
      {(roleLower()==="manager"||roleLower()==="administrator"||roleLower()==="admin")&&<form onSubmit={createApproval} className="inline-form"><select required value={approval.reviewer_id} onChange={e=>setApproval({...approval,reviewer_id:e.target.value})}><option value="">Assign reviewer</option>{users.filter(u=>u.role==="Reviewer").map(u=><option key={u.id} value={u.id}>{u.full_name} (#{u.id})</option>)}</select><input type="number" min="1" value={approval.approval_level} onChange={e=>setApproval({...approval,approval_level:e.target.value})}/><button className="button secondary">Assign Approval</button></form>}
    </Panel>

    <Panel title="Version History / Timeline">
      {versions.length ? <div className="timeline">{versions.map(v=><div className="timeline-item" key={`${v.decision_id}-${v.version_number}`}><div className="timeline-dot"/><div><b>Version {v.version_number}</b><StatusBadge value={v.status}/><p>{v.title}</p><small>{fmt(v.created_at)} • User #{v.created_by}</small></div></div>)}</div> : <Empty text="No versions found."/>}
    </Panel>

    <Panel title="Decision History / Audit Timeline">
      {history.length ? <div className="timeline">{history.map(h=><div className="timeline-item" key={h.id}><div className="timeline-dot"/><div><b>{h.action}</b><p>{h.description}</p><small>{fmt(h.created_at)} • User #{h.user_id}</small>{(h.old_value||h.new_value)&&<details><summary>Values</summary><pre>{JSON.stringify({old:h.old_value,new:h.new_value},null,2)}</pre></details>}</div></div>)}</div> : <Empty text="No history recorded yet."/>}
    </Panel>
  </Page></Shell>;
}

function Repository() {
  return <Decisions />;
}

function Approvals() {
  const [items,setItems]=useState([]),[pending,setPending]=useState([]),[error,setError]=useState(""),[loading,setLoading]=useState(true);
  async function load(){setLoading(true);try{const [a,p]=await Promise.all([approvalsApi.list(),approvalsApi.pending()]);setItems(getArray(a));setPending(getArray(p))}catch(e){setError(errorMessage(e))}finally{setLoading(false)}}
  useEffect(()=>{load()},[]);
  if(loading)return <Shell><Loading text="Loading approvals..." /></Shell>;
  return <Shell><Page title="Approval Workflow" subtitle="Review assigned approvals and track approval history."><Alert>{error}</Alert><Panel title="My Pending Approvals">{pending.length?<ApprovalTable rows={pending} onRefresh={load}/>:<Empty text="No pending approvals."/>}</Panel><Panel title="All Approvals">{items.length?<ApprovalTable rows={items} onRefresh={load}/>:<Empty text="No approvals found."/>}</Panel></Page></Shell>;
}

function Activities() {
  const [rows,setRows]=useState([]),[filters,setFilters]=useState({action:"",entity_type:"",start_date:"",end_date:""}),[error,setError]=useState(""),[loading,setLoading]=useState(true);
  async function load(){setLoading(true);try{const r=await activitiesApi.list(Object.fromEntries(Object.entries(filters).filter(([,v])=>v)));setRows(getArray(r))}catch(e){setError(errorMessage(e))}finally{setLoading(false)}}
  useEffect(()=>{load()},[]);
  return <Shell><Page title="Activities" subtitle="Track recent system and user activity."><Panel title="Filters"><div className="filter-grid"><input placeholder="Action" value={filters.action} onChange={e=>setFilters({...filters,action:e.target.value})}/><input placeholder="Entity Type" value={filters.entity_type} onChange={e=>setFilters({...filters,entity_type:e.target.value})}/><input type="date" value={filters.start_date} onChange={e=>setFilters({...filters,start_date:e.target.value})}/><input type="date" value={filters.end_date} onChange={e=>setFilters({...filters,end_date:e.target.value})}/><button className="button primary" onClick={load}>Apply</button></div></Panel><Alert>{error}</Alert>{loading?<Loading/>:rows.length?<ActivityTable rows={rows}/>:<Empty text="No activities found."/>}</Page></Shell>;
}

function Audit() {
  const [result,setResult]=useState({items:[],total:0}),[filters,setFilters]=useState({action:"",entity_type:"",entity_id:"",start_date:"",end_date:"",page:1,page_size:20}),[error,setError]=useState(""),[loading,setLoading]=useState(true);
  async function load(){setLoading(true);try{const r=await auditApi.list(Object.fromEntries(Object.entries(filters).filter(([,v])=>v!==""&&v!==null)));setResult({items:getArray(r),total:r.total||0})}catch(e){setError(errorMessage(e))}finally{setLoading(false)}}
  useEffect(()=>{load()},[]);
  return <Shell><Page title="Audit Logs" subtitle="Administrator-only audit and compliance information."><Panel title="Audit Filters"><div className="filter-grid"><select value={filters.action} onChange={e=>setFilters({...filters,action:e.target.value})}><option value="">All actions</option>{["CREATE","UPDATE","DELETE","APPROVE","REJECT","SUBMIT","LOGIN","LOGOUT","ACCESS","STATUS_CHANGE"].map(x=><option key={x}>{x}</option>)}</select><select value={filters.entity_type} onChange={e=>setFilters({...filters,entity_type:e.target.value})}><option value="">All entities</option>{["Decision","Alternative","Comment","DiscussionThread","MeetingNote","Approval","User"].map(x=><option key={x}>{x}</option>)}</select><input type="number" placeholder="Entity ID" value={filters.entity_id} onChange={e=>setFilters({...filters,entity_id:e.target.value})}/><input type="date" value={filters.start_date} onChange={e=>setFilters({...filters,start_date:e.target.value})}/><input type="date" value={filters.end_date} onChange={e=>setFilters({...filters,end_date:e.target.value})}/><button className="button primary" onClick={()=>{setFilters({...filters,page:1});setTimeout(load,0)}}>Apply</button></div></Panel><Alert>{error}</Alert>{loading?<Loading/>:result.items.length?<div className="table-wrap"><table><thead><tr><th>User</th><th>Action</th><th>Entity</th><th>Description</th><th>Endpoint</th><th>Time</th></tr></thead><tbody>{result.items.map(x=><tr key={x.id}><td>{x.user_id}</td><td>{x.action}</td><td>{x.entity_type} #{x.entity_id}</td><td>{x.description}</td><td>{x.endpoint||"—"}</td><td>{fmt(x.created_at)}</td></tr>)}</tbody></table></div>:<Empty text="No audit records found."/>}</Page></Shell>;
}

function Users() {
  const blank={full_name:"",email:"",role:"Employee",password:"",employee_id:"",department:"",designation:"",phone_number:""};
  const [items,setItems]=useState([]),[form,setForm]=useState(blank),[editing,setEditing]=useState(null),[error,setError]=useState(""),[loading,setLoading]=useState(true);
  async function load(){setLoading(true);try{setItems(getArray(await usersApi.list()))}catch(e){setError(errorMessage(e))}finally{setLoading(false)}}
  useEffect(()=>{load()},[]);
  async function save(e){e.preventDefault();setError("");try{if(editing){const payload={...form};delete payload.password;await usersApi.update(editing,payload)}else await usersApi.create(form);setForm(blank);setEditing(null);await load()}catch(e){setError(errorMessage(e))}}
  async function remove(id){if(!confirm("Delete this user?"))return;try{await usersApi.remove(id);await load()}catch(e){setError(errorMessage(e))}}
  return <Shell><Page title="User Management" subtitle="Create, update and manage organizational users and roles."><Alert>{error}</Alert><Panel title={editing?`Edit User #${editing}`:"Create User"}><form onSubmit={save} className="form-grid">{[["full_name","Full Name"],["email","Email"],["employee_id","Employee ID"],["department","Department"],["designation","Designation"],["phone_number","Phone Number"]].map(([k,l])=><label key={k}>{l}<input required value={form[k]} onChange={e=>setForm({...form,[k]:e.target.value})}/></label>)}{!editing&&<label>Password<input type="password" required value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/></label>}<label>Role<select value={form.role} onChange={e=>setForm({...form,role:e.target.value})}>{ROLES.map(x=><option key={x}>{x}</option>)}</select></label><div className="form-actions"><button className="button primary">{editing?"Update User":"Create User"}</button>{editing&&<button type="button" className="button secondary" onClick={()=>{setEditing(null);setForm(blank)}}>Cancel</button>}</div></form></Panel>{loading?<Loading/>:<div className="table-wrap"><table><thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Role</th><th>Employee ID</th><th>Department</th><th>Actions</th></tr></thead><tbody>{items.map(u=><tr key={u.id}><td>{u.id}</td><td>{u.full_name}</td><td>{u.email}</td><td><StatusBadge value={u.role}/></td><td>{u.employee_id}</td><td>{u.department}</td><td><button className="small" onClick={()=>{setEditing(u.id);setForm({...u,password:""})}}>Edit</button>{" "}<button className="small danger" onClick={()=>remove(u.id)}>Delete</button></td></tr>)}</tbody></table></div>}</Page></Shell>;
}

function Analytics() {
  const [analytics,setAnalytics]=useState(null),[activity,setActivity]=useState([]),[approval,setApproval]=useState(null),[error,setError]=useState(""),[loading,setLoading]=useState(true),[dates,setDates]=useState({start_date:"",end_date:""});
  async function load(){setLoading(true);try{const [a,b,c]=await Promise.all([dashboardApi.adminAnalytics(Object.fromEntries(Object.entries(dates).filter(([,v])=>v))),dashboardApi.adminDecisionActivity(),dashboardApi.adminApprovalStats()]);setAnalytics(a);setActivity(getArray(b));setApproval(c)}catch(e){setError(errorMessage(e))}finally{setLoading(false)}}
  useEffect(()=>{load()},[]);
  if(loading)return <Shell><Loading text="Loading admin analytics..." /></Shell>;
  return <Shell><Page title="Admin Analytics" subtitle="Organization-level decision, approval and activity analytics."><Alert>{error}</Alert><Panel title="Date Range"><div className="inline-form"><input type="date" value={dates.start_date} onChange={e=>setDates({...dates,start_date:e.target.value})}/><input type="date" value={dates.end_date} onChange={e=>setDates({...dates,end_date:e.target.value})}/><button className="button primary" onClick={load}>Apply</button></div></Panel><div className="stats"><Card title="Users" value={analytics?.total_users ?? analytics?.system_analytics?.total_users ?? 0}/><Card title="Decisions" value={analytics?.total_decisions ?? analytics?.system_analytics?.total_decisions ?? 0}/><Card title="Active Users" value={analytics?.active_users ?? 0}/><Card title="Approvals" value={approval?.total_approvals ?? analytics?.total_approvals ?? 0}/></div><Panel title="Decision Activity">{activity.length?<ActivityTable rows={activity}/>:<Empty text="No decision activity."/>}</Panel></Page></Shell>;
}

function Reports() {
  const [type,setType]=useState("decisions"),[rows,setRows]=useState([]),[raw,setRaw]=useState(null),[error,setError]=useState(""),[loading,setLoading]=useState(false),[filters,setFilters]=useState({status:"",category:"",start_date:"",end_date:""});
  async function load(){setLoading(true);setError("");try{const r=await reportsApi.list(type,Object.fromEntries(Object.entries(filters).filter(([,v])=>v)));setRaw(r);setRows(getArray(r))}catch(e){setError(errorMessage(e))}finally{setLoading(false)}}
  async function download(format){try{const r=await reportsApi.download(type,format,Object.fromEntries(Object.entries(filters).filter(([,v])=>v)));const blob=new Blob([r.data]);const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download=`${type}-report.${format==="pdf"?"pdf":"xlsx"}`;a.click();URL.revokeObjectURL(url)}catch(e){setError(errorMessage(e,"Unable to download report."))}}
  return <Shell><Page title="Reports & Export" subtitle="Generate decision, approval, team and audit reports, then export PDF or Excel."><Panel title="Report Controls"><div className="filter-grid"><select value={type} onChange={e=>setType(e.target.value)}><option value="decisions">Decision Report</option><option value="approvals">Approval Report</option><option value="teams">Team Report</option><option value="audit">Audit Report</option></select><input placeholder="Status" value={filters.status} onChange={e=>setFilters({...filters,status:e.target.value})}/><input placeholder="Category" value={filters.category} onChange={e=>setFilters({...filters,category:e.target.value})}/><input type="date" value={filters.start_date} onChange={e=>setFilters({...filters,start_date:e.target.value})}/><input type="date" value={filters.end_date} onChange={e=>setFilters({...filters,end_date:e.target.value})}/><button className="button primary" onClick={load}>Generate</button><button className="button secondary" onClick={()=>download("pdf")}>Export PDF</button><button className="button secondary" onClick={()=>download("excel")}>Export Excel</button></div></Panel><Alert>{error}</Alert>{loading?<Loading/>:rows.length?<div className="table-wrap"><table><thead><tr>{Object.keys(rows[0]).slice(0,8).map(k=><th key={k}>{k.replaceAll("_"," ")}</th>)}</tr></thead><tbody>{rows.map((r,i)=><tr key={i}>{Object.keys(rows[0]).slice(0,8).map(k=><td key={k}>{typeof r[k]==="object"?JSON.stringify(r[k]):String(r[k]??"—")}</td>)}</tr>)}</tbody></table></div>:raw?<Empty text="Report generated but contains no rows for the selected filters."/>:<Empty text="Choose filters and click Generate."/>}</Page></Shell>;
}

function NotFound(){return <div className="landing"><div className="landing-card"><h1>404</h1><p>Page not found.</p><Link className="button primary" to="/dashboard">Go to Dashboard</Link></div></div>}

function App(){
  return <BrowserRouter><Routes>
    <Route path="/" element={<Home/>}/><Route path="/login" element={<Login/>}/><Route path="/register" element={<Register/>}/>
    <Route path="/dashboard" element={<Protected><Dashboard/></Protected>}/>
    <Route path="/decisions" element={<Protected><Decisions/></Protected>}/>
    <Route path="/decisions/create" element={<Protected allowed={["Employee","Reviewer","Manager","Administrator","Admin"]}><CreateDecision/></Protected>}/>
    <Route path="/decisions/:decisionId" element={<Protected><DecisionDetails/></Protected>}/>
    <Route path="/repository" element={<Protected><Repository/></Protected>}/>
    <Route path="/approvals" element={<Protected allowed={["Reviewer","Manager","Administrator","Admin"]}><Approvals/></Protected>}/>
    <Route path="/reports" element={<Protected allowed={["Manager","Administrator","Admin"]}><Reports/></Protected>}/>
    <Route path="/activities" element={<Protected><Activities/></Protected>}/>
    <Route path="/users" element={<Protected allowed={["Administrator","Admin"]}><Users/></Protected>}/>
    <Route path="/analytics" element={<Protected allowed={["Administrator","Admin"]}><Analytics/></Protected>}/>
    <Route path="/audit" element={<Protected allowed={["Administrator","Admin"]}><Audit/></Protected>}/>
    <Route path="*" element={<NotFound/>}/>
  </Routes></BrowserRouter>
}

export default App;
