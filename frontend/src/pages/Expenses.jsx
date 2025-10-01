// File: frontend/src/pages/Expenses.jsx
import { useEffect, useState } from "react";
import { api } from "../api";
import ExpenseForm from "../components/ExpenseForm";
import ExpenseList from "../components/ExpenseList";

export default function Expenses() {
  const [expenses, setExpenses] = useState([]);
  const [editing, setEditing] = useState(null);

  const loadExpenses = async () => {
    const res = await api.get("/expenses");
    setExpenses(res.data);
  };

  useEffect(() => {
    loadExpenses();
  }, []);

  const handleSave = async (data) => {
    if (editing) {
      await api.put(`/expenses/${editing.id}`, data);
      setEditing(null);
    } else {
      await api.post("/expenses", data);
    }
    loadExpenses();
  };

  const handleDelete = async (id) => {
    await api.delete(`/expenses/${id}`);
    loadExpenses();
  };

  // Styles
  const container = {
    minHeight: "100vh",
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    padding: "2rem",
    display: "flex",
    justifyContent: "center",
    alignItems: "flex-start",
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
  };

  const card = {
    width: "100%",
    maxWidth: "800px",
    background: "#ffffff",
    borderRadius: "16px",
    boxShadow: "0 20px 40px rgba(0, 0, 0, 0.1)",
    overflow: "hidden",
    marginTop: "2rem",
  };

  const header = {
    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    color: "white",
    padding: "2rem",
    textAlign: "center",
  };

  const title = {
    fontSize: "2rem",
    fontWeight: "700",
    margin: "0 0 0.5rem 0",
    letterSpacing: "-0.025em",
  };

  const subtitle = {
    fontSize: "1rem",
    opacity: "0.9",
    margin: "0",
    fontWeight: "400",
  };

  const content = {
    padding: "2rem",
  };

  const formSection = {
    background: "#f8fafc",
    borderRadius: "12px",
    padding: "1.5rem",
    marginBottom: "2rem",
    border: "1px solid #e2e8f0",
  };

  const formTitle = {
    fontSize: "1.25rem",
    fontWeight: "600",
    color: "#1e293b",
    margin: "0 0 1rem 0",
  };

  const cancelBtn = {
    marginTop: "1rem",
    background: "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    padding: "0.75rem 1.5rem",
    cursor: "pointer",
    fontSize: "0.875rem",
    fontWeight: "500",
    transition: "all 0.2s",
    boxShadow: "0 2px 4px rgba(239, 68, 68, 0.2)",
  };

  const listSection = {
    background: "#ffffff",
    borderRadius: "12px",
    border: "1px solid #e2e8f0",
    overflow: "hidden",
  };

  const listTitle = {
    fontSize: "1.25rem",
    fontWeight: "600",
    color: "#1e293b",
    margin: "0",
    padding: "1.5rem 1.5rem 1rem 1.5rem",
    borderBottom: "1px solid #e2e8f0",
  };

  return (
    <div style={container}>
      <div style={card}>
        <div style={header}>
          <h1 style={title}>Expense Manager</h1>
          <p style={subtitle}>Track and manage your expenses efficiently</p>
        </div>

        <div style={content}>
          <div style={formSection}>
            <h3 style={formTitle}>
              {editing ? "Edit Expense" : "Add New Expense"}
            </h3>
            <ExpenseForm expense={editing} onSave={handleSave} />
            {editing && (
              <button
                style={cancelBtn}
                onClick={() => setEditing(null)}
                onMouseEnter={(e) => e.target.style.transform = "translateY(-1px)"}
                onMouseLeave={(e) => e.target.style.transform = "translateY(0)"}
              >
                Cancel Edit
              </button>
            )}
          </div>

          <div style={listSection}>
            <h3 style={listTitle}>Your Expenses</h3>
            <div style={{ padding: "0 1.5rem 1.5rem 1.5rem" }}>
              <ExpenseList
                expenses={expenses}
                onEdit={setEditing}
                onDelete={handleDelete}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
