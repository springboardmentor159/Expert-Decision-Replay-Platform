// Decision Creation Form View
import { decisionsApi, tagsApi } from '../api.js';
import { showToast, escapeHtml, errorState } from '../components/ui.js';

export async function renderCreateDecisionView() {
  const categories = [
    'Technology', 'Finance', 'Operations', 'Human Resources',
    'Security', 'Product', 'Infrastructure', 'Strategy',
  ];

  let tags = [];
  try {
    tags = await tagsApi.list().catch(() => []);
  } catch {
    tags = [];
  }

  return `
    <div class="page-header">
      <div class="page-header-text">
        <h1>Create Decision Proposal</h1>
        <p>Document the problem context, strategic objectives, stakeholders, and evaluation criteria.</p>
      </div>
      <div class="page-header-actions">
        <a href="#decisions" class="btn btn-outline">Cancel</a>
      </div>
    </div>

    <div class="panel" style="max-width: 900px; margin: 0 auto;">
      <div id="create-decision-alert" style="display: none; padding: 12px; border-radius: 6px; margin-bottom: 18px; font-size: 13.5px;"></div>

      <form id="create-decision-form">
        <!-- Section 1: Core Info -->
        <h3 class="panel-title" style="margin-bottom: 16px;">1. Core Decision Details</h3>
        
        <div class="form-group">
          <label for="dec-title">Decision Title *</label>
          <input type="text" id="dec-title" name="title" class="form-control" placeholder="e.g., Adopt Event-Driven Microservices Architecture for Billing" required minlength="3">
          <span class="form-hint">A clear, concise title summarizing the decision or architectural question.</span>
        </div>

        <div class="form-grid-2">
          <div class="form-group">
            <label for="dec-category">Category *</label>
            <select id="dec-category" name="category" class="form-select" required>
              ${categories.map(c => `<option value="${c}">${c}</option>`).join('')}
            </select>
          </div>

          <div class="form-group">
            <label for="dec-tags">Associated Tags</label>
            <select id="dec-tags" name="tag_ids" class="form-select" multiple style="min-height: 42px;">
              ${tags.map(t => `<option value="${t.id}">${escapeHtml(t.name)}</option>`).join('')}
            </select>
            <span class="form-hint">Hold Ctrl / Cmd to select multiple tags.</span>
          </div>
        </div>

        <div class="form-group">
          <label for="dec-problem">Problem Statement & Context *</label>
          <textarea id="dec-problem" name="problem_statement" class="form-textarea" placeholder="Describe the challenge, operational bottlenecks, architectural constraints, or business driver requiring this decision..." required minlength="10" rows="4"></textarea>
          <span class="form-hint">Provide thorough background so reviewers understand the 'why' behind the call.</span>
        </div>

        <!-- Section 2: Strategic Alignment -->
        <h3 class="panel-title" style="margin-top: 24px; margin-bottom: 16px;">2. Objectives & Governance Context</h3>

        <div class="form-grid-2">
          <div class="form-group">
            <label for="dec-objectives">Objectives & Evaluation Criteria</label>
            <textarea id="dec-objectives" name="objectives" class="form-textarea" placeholder="Key goals, performance latency targets, budget bounds, reliability requirements..." rows="3"></textarea>
          </div>

          <div class="form-group">
            <label for="dec-stakeholders">Key Stakeholders & Impacted Teams</label>
            <textarea id="dec-stakeholders" name="stakeholders" class="form-textarea" placeholder="Platform Engineering, DevOps, Compliance, Finance Operations..." rows="3"></textarea>
          </div>
        </div>

        <div class="form-grid-2">
          <div class="form-group">
            <label for="dec-risks">Identified Risks & Constraints</label>
            <textarea id="dec-risks" name="risks" class="form-textarea" placeholder="Vendor lock-in, data consistency overhead, migration downtime..." rows="3"></textarea>
          </div>

          <div class="form-group">
            <label for="dec-rationale">Initial Rationale / Recommendation</label>
            <textarea id="dec-rationale" name="rationale" class="form-textarea" placeholder="Preliminary findings or working hypothesis (can be updated later)..." rows="3"></textarea>
          </div>
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px; padding-top: 18px; border-top: 1px solid var(--border-subtle);">
          <a href="#decisions" class="btn btn-outline">Cancel</a>
          <button type="submit" id="btn-create-submit" class="btn btn-primary" style="padding: 10px 24px;">
            Save & Continue to Alternatives →
          </button>
        </div>
      </form>
    </div>
  `;
}

export function bindCreateDecisionEvents() {
  const form = document.getElementById('create-decision-form');
  const alertEl = document.getElementById('create-decision-alert');
  const submitBtn = document.getElementById('btn-create-submit');

  if (!form) return;

  form.onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const title = formData.get('title')?.trim();
    const category = formData.get('category');
    const problem_statement = formData.get('problem_statement')?.trim();
    const rationale = formData.get('rationale')?.trim();
    const selectedTagIds = Array.from(form.querySelector('#dec-tags').selectedOptions).map(o => parseInt(o.value, 10));

    if (!title || title.length < 3) {
      alertEl.style.display = 'block';
      alertEl.style.background = 'rgba(248, 81, 73, 0.15)';
      alertEl.style.color = '#f85149';
      alertEl.textContent = 'Decision Title must be at least 3 characters.';
      return;
    }

    if (!problem_statement || problem_statement.length < 10) {
      alertEl.style.display = 'block';
      alertEl.style.background = 'rgba(248, 81, 73, 0.15)';
      alertEl.style.color = '#f85149';
      alertEl.textContent = 'Problem Statement must be at least 10 characters.';
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating Decision...';

    try {
      // 1. Create Decision
      const newDecision = await decisionsApi.create({
        title,
        category,
        problem_statement,
      });

      // 2. If rationale provided, update it
      if (rationale) {
        await decisionsApi.updateRationale(newDecision.id, rationale).catch(() => {});
      }

      // 3. If tags selected, assign them
      if (selectedTagIds.length > 0) {
        await decisionsApi.assignTags(newDecision.id, selectedTagIds).catch(() => {});
      }

      showToast('Decision proposal created successfully!', 'success');
      window.location.hash = `#decisions/${newDecision.id}`;
    } catch (err) {
      alertEl.style.display = 'block';
      alertEl.style.background = 'rgba(248, 81, 73, 0.15)';
      alertEl.style.color = '#f85149';
      alertEl.textContent = err.message || 'Failed to create decision.';
      submitBtn.disabled = false;
      submitBtn.textContent = 'Save & Continue to Alternatives →';
    }
  };
}
