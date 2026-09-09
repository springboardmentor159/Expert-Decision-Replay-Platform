// Authentication Views: Login & Registration
import { auth } from '../auth.js';
import { showToast, escapeHtml } from '../components/ui.js';

export function renderAuthView(isRegister = false) {
  const roles = ['Employee', 'Reviewer', 'Manager', 'Administrator'];

  return `
    <div class="auth-page-container">
      <!-- Left Hero Panel -->
      <section class="auth-hero-panel">
        <div class="auth-hero-brand">
          <div class="brand-icon">⚡</div>
          <div class="brand-info">
            <span class="brand-title" style="font-size: 20px; color: #fff;">Decision Replay</span>
            <span class="brand-tagline" style="color: #6ee7b7;">Intelligence & Governance</span>
          </div>
        </div>

        <div class="auth-hero-content">
          <h1 class="auth-hero-title">Make high-stakes calls.<br>Preserve the context.</h1>
          <p class="auth-hero-lead">
            The unified platform for capturing organizational decisions, comparing alternatives with empirical criteria, collaborating across roles, and establishing rigorous audit trails.
          </p>

          <div class="auth-features-list">
            <div class="auth-feature-item">
              <span class="auth-feature-check">✓</span>
              <span>Role-governed approval workflows (Employee, Reviewer, Manager, Admin)</span>
            </div>
            <div class="auth-feature-item">
              <span class="auth-feature-check">✓</span>
              <span>Side-by-side alternative tradeoff analysis & feasibility scoring</span>
            </div>
            <div class="auth-feature-item">
              <span class="auth-feature-check">✓</span>
              <span>Complete immutable version history & compliance audit logs</span>
            </div>
            <div class="auth-feature-item">
              <span class="auth-feature-check">✓</span>
              <span>Instant PDF and Excel reporting export engine</span>
            </div>
          </div>
        </div>

        <div style="font-size: 12px; color: #94a3b8;">
          Enterprise Decision Intelligence Platform • Sprint 14
        </div>
      </section>

      <!-- Right Form Panel -->
      <section class="auth-form-panel">
        <div class="auth-form-card">
          <div class="auth-form-header">
            <h2 class="auth-form-title">${isRegister ? 'Create your account' : 'Welcome back'}</h2>
            <p class="auth-form-subtitle">
              ${isRegister ? 'Join your organization workspace to contribute to decisions' : 'Sign in to access your role-based workspace'}
            </p>
          </div>

          <div id="auth-alert" style="display: none; padding: 12px; border-radius: 6px; margin-bottom: 18px; font-size: 13.5px;"></div>

          ${isRegister ? renderRegisterForm(roles) : renderLoginForm()}

          <div class="auth-switch">
            ${isRegister
              ? `Already have an account? <a href="#login">Sign in</a>`
              : `Don't have an account? <a href="#register">Register now</a>`
            }
          </div>
        </div>
      </section>
    </div>
  `;
}

function renderLoginForm() {
  return `
    <form id="login-form">
      <div class="form-group">
        <label for="login-email">Work Email</label>
        <input type="email" id="login-email" name="email" class="form-control" placeholder="name@company.com" required autocomplete="username">
      </div>

      <div class="form-group">
        <label for="login-password">Password</label>
        <input type="password" id="login-password" name="password" class="form-control" placeholder="••••••••" required autocomplete="current-password">
      </div>

      <button type="submit" class="btn btn-primary" id="btn-login-submit" style="width: 100%; margin-top: 8px; padding: 11px;">
        Sign In to Platform
      </button>
    </form>
  `;
}

function renderRegisterForm(roles) {
  return `
    <form id="register-form">
      <div class="form-group">
        <label for="reg-fullname">Full Name</label>
        <input type="text" id="reg-fullname" name="full_name" class="form-control" placeholder="Alex Morgan" required>
      </div>

      <div class="form-group">
        <label for="reg-email">Work Email</label>
        <input type="email" id="reg-email" name="email" class="form-control" placeholder="alex@company.com" required>
      </div>

      <div class="form-grid-2">
        <div class="form-group">
          <label for="reg-role">Role</label>
          <select id="reg-role" name="role" class="form-select" required>
            ${roles.map(r => `<option value="${r}">${r}</option>`).join('')}
          </select>
        </div>
        <div class="form-group">
          <label for="reg-empid">Employee ID</label>
          <input type="text" id="reg-empid" name="employee_id" class="form-control" placeholder="EMP-1042" required>
        </div>
      </div>

      <div class="form-grid-2">
        <div class="form-group">
          <label for="reg-department">Department</label>
          <input type="text" id="reg-department" name="department" class="form-control" placeholder="Engineering" required>
        </div>
        <div class="form-group">
          <label for="reg-designation">Designation</label>
          <input type="text" id="reg-designation" name="designation" class="form-control" placeholder="Staff Architect" required>
        </div>
      </div>

      <div class="form-group">
        <label for="reg-phone">Phone Number</label>
        <input type="tel" id="reg-phone" name="phone_number" class="form-control" placeholder="+1-555-0199" required>
      </div>

      <div class="form-grid-2">
        <div class="form-group">
          <label for="reg-password">Password</label>
          <input type="password" id="reg-password" name="password" class="form-control" placeholder="Min 8 characters" minlength="8" required>
        </div>
        <div class="form-group">
          <label for="reg-confirm">Confirm Password</label>
          <input type="password" id="reg-confirm" name="confirm_password" class="form-control" placeholder="Re-enter password" minlength="8" required>
        </div>
      </div>

      <button type="submit" class="btn btn-primary" id="btn-register-submit" style="width: 100%; margin-top: 8px; padding: 11px;">
        Complete Registration
      </button>
    </form>
  `;
}

export function bindAuthEvents(isRegister = false) {
  const alertEl = document.getElementById('auth-alert');
  const showAlert = (msg, isError = true) => {
    if (!alertEl) return;
    alertEl.style.display = 'block';
    alertEl.style.background = isError ? 'rgba(248, 81, 73, 0.15)' : 'rgba(46, 160, 67, 0.15)';
    alertEl.style.border = `1px solid ${isError ? '#f85149' : '#2ea043'}`;
    alertEl.style.color = isError ? '#f85149' : '#3fb950';
    alertEl.textContent = msg;
  };

  if (isRegister) {
    const regForm = document.getElementById('register-form');
    if (!regForm) return;

    regForm.onsubmit = async (e) => {
      e.preventDefault();
      const submitBtn = document.getElementById('btn-register-submit');
      const data = Object.fromEntries(new FormData(regForm));

      // Validation
      if (!data.full_name || !data.email || !data.password || !data.confirm_password) {
        return showAlert('All required fields must be filled.');
      }

      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
        return showAlert('Please enter a valid email address.');
      }

      if (data.password.length < 8) {
        return showAlert('Password must be at least 8 characters long.');
      }

      if (data.password !== data.confirm_password) {
        return showAlert('Passwords do not match.');
      }

      delete data.confirm_password;
      submitBtn.disabled = true;
      submitBtn.textContent = 'Creating account...';

      try {
        await auth.register(data);
        showToast('Registration successful! Please sign in.', 'success');
        window.location.hash = '#login';
      } catch (err) {
        showAlert(err.message || 'Registration failed.');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Complete Registration';
      }
    };
  } else {
    const loginForm = document.getElementById('login-form');
    if (!loginForm) return;

    loginForm.onsubmit = async (e) => {
      e.preventDefault();
      const submitBtn = document.getElementById('btn-login-submit');
      const email = document.getElementById('login-email').value.trim();
      const password = document.getElementById('login-password').value;

      if (!email || !password) {
        return showAlert('Please enter your email and password.');
      }

      submitBtn.disabled = true;
      submitBtn.textContent = 'Authenticating...';

      try {
        await auth.login(email, password);
        showToast('Welcome back! Signed in successfully.', 'success');
        window.location.hash = '#dashboard';
      } catch (err) {
        showAlert(err.message || 'Invalid credentials or server error.');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Sign In to Platform';
      }
    };
  }
}
