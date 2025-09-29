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

  useEffect(() => { loadExpenses(); }, []);

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

  return (
    <div style={{ padding: "1rem" }}>
      <h2>Manage Expenses</h2>
      <ExpenseForm expense={editing} onSave={handleSave} />

      <ul>
        {expenses.map((exp) => (
          <li key={exp.id}>
            {exp.title} – ${exp.amount}
            <button onClick={() => setEditing(exp)}>Edit</button>
            <button onClick={() => handleDelete(exp.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
