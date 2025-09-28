import { useEffect, useState } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [expenses, setExpenses] = useState([]);
  const [title, setTitle] = useState("");
  const [amount, setAmount] = useState("");
  const [tags, setTags] = useState("");

  const fetchExpenses = async () => {
    const res = await axios.get(`${API_URL}/expenses`);
    setExpenses(res.data);
  };

  const addExpense = async () => {
    await axios.post(`${API_URL}/expenses`, {
      title,
      amount: parseFloat(amount),
      tags: tags.split(",").map(t => t.trim())
    });
    setTitle(""); setAmount(""); setTags("");
    fetchExpenses();
  };

  const deleteExpense = async (id) => {
    await axios.delete(`${API_URL}/expenses/${id}`);
    fetchExpenses();
  };

  useEffect(() => {
    fetchExpenses();
  }, []);

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Expense Manager</h1>

      <div style={{ marginBottom: "2rem" }}>
        <input placeholder="Title" value={title} onChange={e => setTitle(e.target.value)} />
        <input placeholder="Amount" value={amount} onChange={e => setAmount(e.target.value)} />
        <input placeholder="Tags (comma-separated)" value={tags} onChange={e => setTags(e.target.value)} />
        <button onClick={addExpense}>Add Expense</button>
      </div>

      <ul>
        {expenses.map(exp => (
          <li key={exp.id}>
            {exp.title} - ${exp.amount} - Tags: {exp.tags.map(t => t.name).join(", ")}
            <button onClick={() => deleteExpense(exp.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
