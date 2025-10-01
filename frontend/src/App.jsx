// File: frontend/src/App.jsx
import { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Login from "./components/Login";
import Register from "./components/Register";
import ProfileModal from "./components/ProfileModal";
import Expenses from "./pages/Expenses";
import Analytics from "./pages/Analytics";

function AuthWrapper() {
  const [showRegister, setShowRegister] = useState(false);
  const { user, loading } = useAuth();

  if (loading) {
    return <div style={{display: "flex", justifyContent: "center", alignItems: "center", height: "100vh"}}>Loading...</div>;
  }

  if (!user) {
    return showRegister ? (
      <Register onSwitchToLogin={() => setShowRegister(false)} />
    ) : (
      <Login onSwitchToRegister={() => setShowRegister(true)} />
    );
  }

  return <MainApp />;
}

function MainApp() {
  const [showProfile, setShowProfile] = useState(false);
  const { user } = useAuth();

  const navStyle = {
    padding: "1rem",
    borderBottom: "1px solid #ddd",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center"
  };

  const linkStyle = {
    marginRight: "1rem",
    textDecoration: "none",
    color: "#3b82f6"
  };

  const userButtonStyle = {
    background: "#f3f4f6",
    border: "1px solid #d1d5db",
    borderRadius: 6,
    padding: "0.5rem 1rem",
    cursor: "pointer"
  };

  return (
    <Router>
      <nav style={navStyle}>
        <div>
          <Link to="/expenses" style={linkStyle}>Expenses</Link>
          <Link to="/analytics" style={linkStyle}>Analytics</Link>
        </div>
        <button style={userButtonStyle} onClick={() => setShowProfile(true)}>
          {user.username}
        </button>
      </nav>

      <Routes>
        <Route path="/expenses" element={<Expenses />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="*" element={<Expenses />} />
      </Routes>

      <ProfileModal isOpen={showProfile} onClose={() => setShowProfile(false)} />
    </Router>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AuthWrapper />
    </AuthProvider>
  );
}
