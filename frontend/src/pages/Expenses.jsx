import { useEffect, useState } from "react";
import { api } from "../api";
import ExpenseForm from "../components/ExpenseForm";

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

  const header = {
    marginBottom: "1.5rem",
    textAlign: "center",
  };

  const title = {
    fontSize: "1.5rem",
    marginBottom: "0.25rem",
    color: "#0f172a",
  };

  const subtitle = {
    fontSize: "0.95rem",
    color: "#64748b",
  };

  const list = {
    listStyle: "none",
    padding: 0,
    marginTop: "1rem",
  };

  const listItem = {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "0.5rem 0",
    borderBottom: "1px solid #e2e8f0",
  };

  const buttons = {
    display: "flex",
    gap: "0.5rem",
  };

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

        <ul style={list}>
          {expenses.map((exp) => (
            <li key={exp.id} style={listItem}>
              <span>{exp.title} – ${exp.amount}</span>
              <div style={buttons}>
                <button
                  style={{
                    background: "#3b82f6",
                    color: "#fff",
                    border: "none",
                    borderRadius: 6,
                    padding: "0.3rem 0.6rem",
                    cursor: "pointer",
                  }}
                  onClick={() => setEditing(exp)}
                >
                  Edit
                </button>
                <button
                  style={{
                    background: "#ef4444",
                    color: "#fff",
                    border: "none",
                    borderRadius: 6,
                    padding: "0.3rem 0.6rem",
                    cursor: "pointer",
                  }}
                  onClick={() => handleDelete(exp.id)}
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
