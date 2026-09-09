import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createDecision } from "../../api/decisions";
import Card from "../../components/ui/Card";
import Input from "../../components/ui/Input";
import Textarea from "../../components/ui/Textarea";
import Button from "../../components/ui/Button";
import Alert from "../../components/ui/Alert";

// The backend's DecisionCreate schema only accepts title, problem_statement,
// and category on creation. Objectives, stakeholders, evaluation criteria,
// risks, and tags are added afterward on the Decision Details page, via
// their own endpoints (alternatives, tags, discussions, etc).
export default function DecisionCreate() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ title: "", problem_statement: "", category: "" });
  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState("");
  const [loading, setLoading] = useState(false);

  function validate() {
    const next = {};
    if (!form.title.trim()) next.title = "Title is required.";
    if (form.title.length > 200) next.title = "Title must be under 200 characters.";
    if (!form.problem_statement.trim()) next.problem_statement = "Problem statement is required.";
    if (!form.category.trim()) next.category = "Category is required.";
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setServerError("");
    if (!validate()) return;

    setLoading(true);
    try {
      const decision = await createDecision(form);
      navigate(`/decisions/${decision.id}`);
    } catch (err) {
      setServerError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Create Decision</h1>
      </div>

      <Card>
        <form onSubmit={handleSubmit} noValidate className="stacked-form">
          <Alert type="error">{serverError}</Alert>

          <Input
            label="Decision Title"
            required
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            error={errors.title}
            maxLength={200}
          />
          <Textarea
            label="Problem Statement"
            required
            rows={4}
            value={form.problem_statement}
            onChange={(e) => setForm({ ...form, problem_statement: e.target.value })}
            error={errors.problem_statement}
          />
          <Input
            label="Category"
            required
            placeholder="e.g. Finance, Operations, HR"
            value={form.category}
            onChange={(e) => setForm({ ...form, category: e.target.value })}
            error={errors.category}
          />

          <p className="form-note">
            After creating the decision you'll be able to add alternatives, stakeholders, evaluation
            criteria, risks, tags, and start discussions from the Decision Details page.
          </p>

          <div className="form-actions">
            <Button type="submit" loading={loading}>
              Create Decision
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
