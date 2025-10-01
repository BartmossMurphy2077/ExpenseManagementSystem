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
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "2rem",
    background: "linear-gradient(180deg, #f6fbff 0%, #ffffff 100%)",
  };

  const card = {
    width: "100%",
    maxWidth: 600,
    background: "#fff",
    borderRadius: 12,
    boxShadow: "0 8px 24px rgba(15, 23, 42, 0.08)",
    padding: "2rem",
    boxSizing: "border-box",
  };

  const header = { marginBottom: "1.5rem", textAlign: "center" };
  const title = { fontSize: "1.5rem", marginBottom: "0.25rem", color: "#0f172a" };
  const subtitle = { fontSize: "0.95rem", color: "#64748b" };

  const cancelBtn = {
    marginTop: "0.5rem",
    background: "#f87171",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    padding: "0.3rem 0.6rem",
    cursor: "pointer",
  };

  return (
    <div style={container}>
      <div style={card}>
        <div style={header}>
          <h2 style={title}>Manage Expenses</h2>
          <div style={subtitle}>Add, edit, and remove your expenses</div>
        </div>

        <ExpenseForm expense={editing} onSave={handleSave} />
        {editing && (
          <button style={cancelBtn} onClick={() => setEditing(null)}>
            Cancel Edit
          </button>
        )}

        {/* Use ExpenseList here */}
        <ExpenseList
          expenses={expenses}
          onEdit={setEditing}
          onDelete={handleDelete}
        />
      </div>
    </div>
  );
}
