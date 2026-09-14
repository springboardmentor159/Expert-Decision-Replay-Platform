import { useEffect, useState } from "react";
import api from "../services/api";
import { getStoredUser } from "../auth/authService";

function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        setError("");

        const storedUser = getStoredUser();

        if (!storedUser?.id) {
          setError("User information is not available.");
          return;
        }

        const response = await api.get(`/users/${storedUser.id}`);
        setProfile(response.data);
      } catch (error) {
        console.error("Failed to load profile:", error);

        if (error.response?.status === 401) {
          setError("Your session has expired. Please log in again.");
        } else if (error.response?.status === 403) {
          setError("You do not have permission to view this profile.");
        } else if (error.response?.status === 404) {
          setError("Profile not found.");
        } else {
          setError(
            error.response?.data?.detail ||
              "Unable to load profile. Please try again."
          );
        }
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  if (loading) {
    return (
      <div className="profile-page">
        <div className="profile-loading-card">
          <div className="profile-spinner"></div>
          <p>Loading your profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="profile-page">
        <div className="profile-error-card">
          <div className="profile-error-icon">!</div>
          <h2>Unable to load profile</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  const initials = profile?.full_name
    ? profile.full_name
        .split(" ")
        .map((name) => name[0])
        .join("")
        .slice(0, 2)
        .toUpperCase()
    : "U";

  return (
    <div className="profile-page">

      {/* Header */}
      <div className="profile-header">
        <div>
          <span className="profile-eyebrow">ACCOUNT</span>
          <h1>My Profile</h1>
          <p>View your personal and professional information.</p>
        </div>
      </div>

      {/* Profile Hero */}
      <div className="profile-hero-card">
        <div className="profile-avatar">
          {initials}
        </div>

        <div className="profile-hero-info">
          <h2>{profile?.full_name || "User"}</h2>
          <p>{profile?.designation || "Platform User"}</p>
          <span className="profile-role-badge">
            {profile?.role || "User"}
          </span>
        </div>
      </div>

      {/* Information */}
      <div className="profile-section">
        <div className="profile-section-heading">
          <div>
            <span className="profile-section-number">01</span>
            <h2>Personal Information</h2>
          </div>
          <p>Basic account information</p>
        </div>

        <div className="profile-info-grid">

          <div className="profile-info-item">
            <span className="profile-label">Full Name</span>
            <strong>{profile?.full_name || "N/A"}</strong>
          </div>

          <div className="profile-info-item">
            <span className="profile-label">Email Address</span>
            <strong>{profile?.email || "N/A"}</strong>
          </div>

          <div className="profile-info-item">
            <span className="profile-label">Phone Number</span>
            <strong>{profile?.phone_number || "N/A"}</strong>
          </div>

          <div className="profile-info-item">
            <span className="profile-label">Employee ID</span>
            <strong>{profile?.employee_id || "N/A"}</strong>
          </div>

        </div>
      </div>

      {/* Professional Information */}
      <div className="profile-section">
        <div className="profile-section-heading">
          <div>
            <span className="profile-section-number">02</span>
            <h2>Professional Information</h2>
          </div>
          <p>Work-related information</p>
        </div>

        <div className="profile-info-grid">

          <div className="profile-info-item">
            <span className="profile-label">Department</span>
            <strong>{profile?.department || "N/A"}</strong>
          </div>

          <div className="profile-info-item">
            <span className="profile-label">Designation</span>
            <strong>{profile?.designation || "N/A"}</strong>
          </div>

          <div className="profile-info-item">
            <span className="profile-label">Role</span>
            <strong className="profile-role-text">
              {profile?.role || "N/A"}
            </strong>
          </div>

        </div>
      </div>

      {/* Account Status */}
      <div className="profile-account-card">
        <div className="account-status-icon">✓</div>

        <div>
          <h3>Account Active</h3>
          <p>
            Your account is currently active and authenticated.
          </p>
        </div>

        <span className="account-active-badge">Active</span>
      </div>

    </div>
  );
}

export default Profile;