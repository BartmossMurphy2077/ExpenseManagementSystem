// File: frontend/src/components/Login.jsx
import { useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function Login({ onSwitchToRegister }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username || !password) return;

    setLoading(true);
    setError("");

    try {
      await login(username, password);
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed");
    }

    setLoading(false);
  };

  const containerStyle = {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "linear-gradient(180deg, #f6fbff 0%, #ffffff 100%)",
    padding: "2rem"
  };

  const cardStyle = {
    width: "100%",
    maxWidth: 400,
    background: "#fff",
    borderRadius: 12,
    boxShadow: "0 8px 24px rgba(15, 23, 42, 0.08)",
    padding: "2rem",
    boxSizing: "border-box"
  };

  const titleStyle = {
    fontSize: "1.5rem",
    marginBottom: "0.5rem",
    color: "#0f172a",
    textAlign: "center"
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
    width: "100%",
    padding: "0.75rem",
    background: "#3b82f6",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    fontSize: "1rem",
    cursor: "pointer",
    marginBottom: "1rem"
  };

  const linkStyle = {
    color: "#3b82f6",
    textDecoration: "none",
    fontSize: "0.9rem"
  };

  return (
    <div style={containerStyle}>
      <div style={cardStyle}>
        <h2 style={titleStyle}>Login</h2>
        {error && <div style={{color: "red", marginBottom: "1rem", textAlign: "center"}}>{error}</div>}
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
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button style={buttonStyle} type="submit" disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
        <div style={{textAlign: "center"}}>
          <span>Don't have an account? </span>
          <a href="#" style={linkStyle} onClick={onSwitchToRegister}>
            Register here
          </a>
        </div>
      </div>
    </div>
  );
}
