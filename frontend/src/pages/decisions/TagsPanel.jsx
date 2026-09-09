import { useEffect, useState } from "react";
import { getDecisionTags, assignTagsToDecision, removeTagFromDecision } from "../../api/decisions";
import { listTags, createTag } from "../../api/tags";
import Card from "../../components/ui/Card";
import Badge from "../../components/ui/Badge";
import Button from "../../components/ui/Button";
import Select from "../../components/ui/Select";
import Input from "../../components/ui/Input";
import Alert from "../../components/ui/Alert";

export default function TagsPanel({ decisionId, canEdit }) {
  const [tags, setTags] = useState([]);
  const [allTags, setAllTags] = useState([]);
  const [selectedTag, setSelectedTag] = useState("");
  const [newTagName, setNewTagName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    try {
      const [decisionTags, everyTag] = await Promise.all([getDecisionTags(decisionId), listTags()]);
      setTags(decisionTags);
      setAllTags(everyTag);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [decisionId]);

  async function handleAssign() {
    if (!selectedTag) return;
    setBusy(true);
    setError("");
    try {
      await assignTagsToDecision(decisionId, [Number(selectedTag)]);
      setSelectedTag("");
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleCreateAndAssign() {
    if (!newTagName.trim()) return;
    setBusy(true);
    setError("");
    try {
      const tag = await createTag(newTagName.trim());
      await assignTagsToDecision(decisionId, [tag.id]);
      setNewTagName("");
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleRemove(tagId) {
    setBusy(true);
    setError("");
    try {
      await removeTagFromDecision(decisionId, tagId);
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const availableTags = allTags.filter((t) => !tags.some((dt) => dt.id === t.id));

  return (
    <Card title="Tags">
      <Alert type="error">{error}</Alert>
      <div className="tag-chip-row">
        {tags.length === 0 && <span className="empty-desc">No tags assigned.</span>}
        {tags.map((t) => (
          <span key={t.id} className="tag-chip">
            <Badge tone="blue">{t.name}</Badge>
            {canEdit && (
              <button className="tag-remove" onClick={() => handleRemove(t.id)} disabled={busy} aria-label={`Remove ${t.name}`}>
                ×
              </button>
            )}
          </span>
        ))}
      </div>

      {canEdit && (
        <div className="tag-add-row">
          <Select
            placeholder="Select existing tag"
            options={availableTags.map((t) => ({ value: t.id, label: t.name }))}
            value={selectedTag}
            onChange={(e) => setSelectedTag(e.target.value)}
          />
          <Button size="sm" variant="secondary" disabled={!selectedTag} loading={busy} onClick={handleAssign}>
            Add Tag
          </Button>
          <Input placeholder="Or create new tag…" value={newTagName} onChange={(e) => setNewTagName(e.target.value)} />
          <Button size="sm" disabled={!newTagName.trim()} loading={busy} onClick={handleCreateAndAssign}>
            Create & Add
          </Button>
        </div>
      )}
    </Card>
  );
}
