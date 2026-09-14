import { useAuth } from "../context/AuthContext";


const Profile = () => {
  const { user, role } = useAuth();


  if (!user) {
    return (
      <div className="page-container">
        <div className="card">
          <h2>Profile</h2>
          <p>User information is not available.</p>
        </div>
      </div>
    );
  }


  return (
    <div className="page-container">

      {/* =====================================================
          PAGE HEADER
      ===================================================== */}

      <div className="page-header">

        <div>
          <h1>My Profile</h1>

          <p>
            View your account and profile information.
          </p>
        </div>

      </div>


      {/* =====================================================
          PROFILE CARD
      ===================================================== */}

      <div className="card profile-card">

        {/* Profile Header */}

        <div className="profile-header">

          <div className="profile-avatar">
            {user.full_name
              ? user.full_name.charAt(0).toUpperCase()
              : "U"}
          </div>

          <div>

            <h2>
              {user.full_name || "User"}
            </h2>

            <p>
              {role || "User"}
            </p>

          </div>

        </div>


        {/* Profile Information */}

        <div className="profile-details">

          <div className="profile-field">
            <span className="profile-label">
              Full Name
            </span>

            <span className="profile-value">
              {user.full_name || "-"}
            </span>
          </div>


          <div className="profile-field">
            <span className="profile-label">
              Email
            </span>

            <span className="profile-value">
              {user.email || "-"}
            </span>
          </div>


          <div className="profile-field">
            <span className="profile-label">
              Role
            </span>

            <span className="profile-value">
              {role || "-"}
            </span>
          </div>


          <div className="profile-field">
            <span className="profile-label">
              Employee ID
            </span>

            <span className="profile-value">
              {user.employee_id || "-"}
            </span>
          </div>


          <div className="profile-field">
            <span className="profile-label">
              Department
            </span>

            <span className="profile-value">
              {user.department || "-"}
            </span>
          </div>


          <div className="profile-field">
            <span className="profile-label">
              Designation
            </span>

            <span className="profile-value">
              {user.designation || "-"}
            </span>
          </div>


          <div className="profile-field">
            <span className="profile-label">
              Phone Number
            </span>

            <span className="profile-value">
              {user.phone_number || "-"}
            </span>
          </div>

        </div>

      </div>

    </div>
  );
};


export default Profile;