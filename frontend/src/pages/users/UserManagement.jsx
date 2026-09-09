import { useEffect, useState } from "react";
import { listUsers, updateUser, deleteUser } from "../../api/users";
import Card from "../../components/ui/Card";
import Table from "../../components/ui/Table";
import Badge from "../../components/ui/Badge";
import Button from "../../components/ui/Button";
import Modal from "../../components/ui/Modal";
import Select from "../../components/ui/Select";
import Alert from "../../components/ui/Alert";
import LoadingState from "../../components/ui/LoadingState";
import ErrorState from "../../components/ui/ErrorState";
import EmptyState from "../../components/ui/EmptyState";
import { ROLES } from "../../utils/roles";
import { useAuth } from "../../context/AuthContext";

export default function UserManagement() {
  const { user: me } = useAuth();
  const [users, setUsers] = useState([]);
  const [state, setState] = useState("loading");
  const [errorMsg, setErrorMsg] = useState("");

  const [editingUser, setEditingUser] = useState(null);
  const [roleDraft, setRoleDraft] = useState("");
  const [saving, setSaving] = useState(false);
  const [actionError, setActionError] = useState("");

  const [deletingUser, setDeletingUser] = useState(null);
  const [deleting, setDeleting] = useState(false);

  async function load() {
    setState("loading");
    try {
      const res = await listUsers();
      setUsers(res);
      setState("ready");
    } catch (err) {
      setErrorMsg(err.message);
      setState("error");
    }
  }

  useEffect(() => {
    load();
  }, []);

  function openRoleEdit(u) {
    setEditingUser(u);
    setRoleDraft(u.role);
    setActionError("");
  }

  async function saveRole() {
    setSaving(true);
    setActionError("");
    try {
      await updateUser(editingUser.id, { role: roleDraft });
      setEditingUser(null);
      load();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function confirmDelete() {
    setDeleting(true);
    try {
      await deleteUser(deletingUser.id);
      setDeletingUser(null);
      load();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setDeleting(false);
    }
  }

  if (state === "loading") return <LoadingState label="Loading users…" />;
  if (state === "error") return <ErrorState message={errorMsg} onRetry={load} />;

  return (
    <div>
      <div className="page-header">
        <h1>User Management</h1>
      </div>

      <Alert type="error">{actionError}</Alert>

      <Card>
        {users.length === 0 ? (
          <EmptyState title="No users found" />
        ) : (
          <Table columns={["Name", "Email", "Role", "Department", "Designation", "Actions"]}>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.full_name}</td>
                <td>{u.email}</td>
                <td>
                  <Badge tone="blue">{u.role}</Badge>
                </td>
                <td>{u.department}</td>
                <td>{u.designation}</td>
                <td className="row-actions">
                  <Button size="sm" variant="secondary" onClick={() => openRoleEdit(u)}>
                    Change Role
                  </Button>
                  {u.id !== me?.id && (
                    <Button size="sm" variant="danger" onClick={() => setDeletingUser(u)}>
                      Delete
                    </Button>
                  )}
                </td>
              </tr>
            ))}
          </Table>
        )}
      </Card>

      {editingUser && (
        <Modal
          title={`Change role for ${editingUser.full_name}`}
          onClose={() => setEditingUser(null)}
          footer={
            <>
              <Button variant="secondary" onClick={() => setEditingUser(null)}>
                Cancel
              </Button>
              <Button loading={saving} onClick={saveRole}>
                Save
              </Button>
            </>
          }
        >
          <Alert type="error">{actionError}</Alert>
          <Select label="Role" options={Object.values(ROLES)} value={roleDraft} onChange={(e) => setRoleDraft(e.target.value)} />
        </Modal>
      )}

      {deletingUser && (
        <Modal
          title="Delete user"
          onClose={() => setDeletingUser(null)}
          footer={
            <>
              <Button variant="secondary" onClick={() => setDeletingUser(null)}>
                Cancel
              </Button>
              <Button variant="danger" loading={deleting} onClick={confirmDelete}>
                Delete
              </Button>
            </>
          }
        >
          <p>
            Are you sure you want to delete <strong>{deletingUser.full_name}</strong>? This cannot be undone.
          </p>
        </Modal>
      )}
    </div>
  );
}
