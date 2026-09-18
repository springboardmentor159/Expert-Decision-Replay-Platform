import React, { useEffect, useState } from "react";
import authService from "../services/authService";

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    role: "",
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const loadProfile = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await authService.getProfile();

      const data = response.data || response;

      setProfile(data);

      setFormData({
        name: data.name || data.full_name || "",
        email: data.email || "",
        role: data.role || "",
      });
    } catch (err) {
      console.error("Error loading profile:", err);
      setError("Unable to load profile details.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previousData) => ({
      ...previousData,
      [name]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      setSaving(true);
      setError("");

      await authService.updateProfile({
        name: formData.name,
        email: formData.email,
      });

      alert("Profile updated successfully.");
      loadProfile();
    } catch (err) {
      console.error("Error updating profile:", err);
      setError("Unable to update profile.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">My Profile</h1>
        <p className="text-gray-600">Loading profile...</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">
          My Profile
        </h1>

        <p className="text-gray-600 mt-1">
          View and update your account details.
        </p>
      </div>

      {error && (
        <div className="bg-red-100 text-red-700 p-4 rounded-lg mb-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow p-6 text-center">
          <div className="w-24 h-24 mx-auto rounded-full bg-blue-100 flex items-center justify-center">
            <span className="text-3xl font-bold text-blue-700">
              {(formData.name || formData.email || "U")
                .charAt(0)
                .toUpperCase()}
            </span>
          </div>

          <h2 className="text-xl font-semibold text-gray-800 mt-4">
            {formData.name || "User"}
          </h2>

          <p className="text-gray-600 mt-1">
            {formData.email || "No email available"}
          </p>

          <span className="inline-block mt-3 bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-medium">
            {formData.role || "User"}
          </span>
        </div>

        <div className="lg:col-span-2 bg-white rounded-xl shadow p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-5">
            Account Information
          </h2>

          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name
              </label>

              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your full name"
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email
              </label>

              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your email"
              />
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Role
              </label>

              <input
                type="text"
                name="role"
                value={formData.role}
                disabled
                className="w-full border rounded-lg px-3 py-2 bg-gray-100 text-gray-600"
              />
            </div>

            <button
              type="submit"
              disabled={saving}
              className="bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? "Saving..." : "Save Changes"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Profile;