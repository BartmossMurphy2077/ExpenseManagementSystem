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
    return (
      <div style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        color: "white",
        fontSize: "1.2rem",
        fontWeight: "500"
      }}>
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: "1rem"
        }}>
          <div style={{
            width: "24px",
            height: "24px",
            border: "3px solid #ffffff30",
            borderTop: "3px solid #ffffff",
            borderRadius: "50%",
            animation: "spin 1s linear infinite"
          }}></div>
          Loading...
        </div>
      </div>
    );
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
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    padding: "1rem 2rem",
    boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    position: "sticky",
    top: 0,
    zIndex: 1000
  };

  const linkStyle = {
    marginRight: "2rem",
    textDecoration: "none",
    color: "white",
    fontSize: "1rem",
    fontWeight: "500",
    padding: "0.5rem 1rem",
    borderRadius: "8px",
    transition: "all 0.3s ease",
    position: "relative"
  };

  const userButtonStyle = {
    background: "rgba(255, 255, 255, 0.15)",
    backdropFilter: "blur(10px)",
    border: "1px solid rgba(255, 255, 255, 0.2)",
    borderRadius: "12px",
    padding: "0.75rem 1.5rem",
    cursor: "pointer",
    color: "white",
    fontSize: "0.95rem",
    fontWeight: "500",
    transition: "all 0.3s ease",
    boxShadow: "0 2px 10px rgba(0, 0, 0, 0.1)"
  };

  const containerStyle = {
    minHeight: "calc(100vh - 80px)",
    background: "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
    padding: "2rem"
  };

  return (
    <>
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
          
          .nav-link:hover {
            background: rgba(255, 255, 255, 0.15) !important;
            transform: translateY(-2px);
          }
          
          .user-button:hover {
            background: rgba(255, 255, 255, 0.25) !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
          }
          
          body {
            margin: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
              'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
              sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
          }
          
          * {
            box-sizing: border-box;
          }
        `}
      </style>

      <Router>
        <nav style={navStyle}>
          <div style={{ display: "flex", alignItems: "center" }}>
            <div style={{
              fontSize: "1.5rem",
              fontWeight: "bold",
              color: "white",
              marginRight: "3rem",
              letterSpacing: "0.5px"
            }}>
              💰 ExpenseTracker
            </div>
            <div>
              <Link
                to="/expenses"
                style={linkStyle}
                className="nav-link"
                onMouseEnter={(e) => {
                  e.target.style.background = "rgba(255, 255, 255, 0.15)";
                  e.target.style.transform = "translateY(-2px)";
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = "transparent";
                  e.target.style.transform = "translateY(0)";
                }}
              >
                📊 Expenses
              </Link>
              <Link
                to="/analytics"
                style={linkStyle}
                className="nav-link"
                onMouseEnter={(e) => {
                  e.target.style.background = "rgba(255, 255, 255, 0.15)";
                  e.target.style.transform = "translateY(-2px)";
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = "transparent";
                  e.target.style.transform = "translateY(0)";
                }}
              >
                📈 Analytics
              </Link>
            </div>
          </div>
          <button
            style={userButtonStyle}
            className="user-button"
            onClick={() => setShowProfile(true)}
            onMouseEnter={(e) => {
              e.target.style.background = "rgba(255, 255, 255, 0.25)";
              e.target.style.transform = "translateY(-2px)";
              e.target.style.boxShadow = "0 4px 15px rgba(0, 0, 0, 0.2)";
            }}
            onMouseLeave={(e) => {
              e.target.style.background = "rgba(255, 255, 255, 0.15)";
              e.target.style.transform = "translateY(0)";
              e.target.style.boxShadow = "0 2px 10px rgba(0, 0, 0, 0.1)";
            }}
          >
            👤 {user.username}
          </button>
        </nav>

        <div style={containerStyle}>
          <Routes>
            <Route path="/expenses" element={<Expenses />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="*" element={<Expenses />} />
          </Routes>
        </div>

        <ProfileModal isOpen={showProfile} onClose={() => setShowProfile(false)} />
      </Router>
    </>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AuthWrapper />
    </AuthProvider>
  );
}
