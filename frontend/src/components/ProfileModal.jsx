// File: frontend/src/components/ProfileModal.jsx
import { useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function ProfileModal({ isOpen, onClose }) {
  const { user, updateProfile, logout } = useAuth();
  const [username, setUsername] = useState(user?.username || "");
  const [email, setEmail] = useState(user?.email || "");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password && password !== confirmPassword) {
      setError("Passwords don't match");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const updateData = { username, email };
      if (password) updateData.password = password;
      await updateProfile(updateData);
      setPassword("");
      setConfirmPassword("");
      alert("Profile updated successfully!");
    } catch (err) {
      setError(err.response?.data?.detail || "Update failed");
    }

    setLoading(false);
  };

  const overlayStyle = {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000
  };

  const modalStyle = {
    background: "#fff",
    borderRadius: 12,
    padding: "2rem",
    width: "90%",
    maxWidth: 400,
    boxShadow: "0 8px 24px rgba(15, 23, 42, 0.08)"
  };

  const inputStyle = {
    width: "100%",
    padding: "0.75rem",
    border: "1px solid #e2e8f0",
    borderRadius: 6,
    marginBottom: "1rem",
    fontSize: "1rem",
    boxSizing: "border-box"
  };

  const buttonStyle = {
    padding: "0.75rem 1rem",
    border: "none",
    borderRadius: 6,
    fontSize: "1rem",
    cursor: "pointer",
    marginRight: "0.5rem"
  };

  return (
    <div style={overlayStyle} onClick={onClose}>
      <div style={modalStyle} onClick={(e) => e.stopPropagation()}>
        <h2 style={{marginTop: 0}}>Profile Settings</h2>
        {error && <div style={{color: "red", marginBottom: "1rem"}}>{error}</div>}
        <form onSubmit={handleSubmit}>
          <input
            style={inputStyle}
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            style={inputStyle}
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            style={inputStyle}
            type="password"
            placeholder="New Password (leave empty to keep current)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {password && (
            <input
              style={inputStyle}
              type="password"
              placeholder="Confirm New Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
          )}
          <div style={{display: "flex", justifyContent: "space-between", alignItems: "center"}}>
            <div>
              <button
                style={{...buttonStyle, background: "#3b82f6", color: "#fff"}}
                type="submit"
                disabled={loading}
              >
                {loading ? "Updating..." : "Update"}
              </button>
              <button
                style={{...buttonStyle, background: "#6b7280", color: "#fff"}}
                type="button"
                onClick={onClose}
              >
                Cancel
              </button>
            </div>
            <button
              style={{...buttonStyle, background: "#ef4444", color: "#fff"}}
              type="button"
              onClick={() => {
                logout();
                onClose();
              }}
            >
              Logout
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
