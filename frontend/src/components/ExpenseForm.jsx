// File: frontend/src/components/ExpenseForm.jsx
import { useState, useEffect } from "react";

export default function ExpenseForm({ expense = null, onSave }) {
  const [title, setTitle] = useState("");
  const [amount, setAmount] = useState("");
  const [tags, setTags] = useState("");

  useEffect(() => {
    if (expense) {
      setTitle(expense.title ?? "");
      setAmount(expense.amount ?? "");
      // Normalize various possible tag shapes into a comma-separated string
      const tagStr = (expense.tags || [])
        .map((t) => (typeof t === "string" ? t : t?.name ?? ""))
        .filter(Boolean)
        .join(", ");
      setTags(tagStr);
    } else {
      setTitle("");
      setAmount("");
      setTags("");
    }
  }, [expense]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title || amount === "") return;
    const payload = {
      title,
      amount: parseFloat(amount),
      tags: tags
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean),
    };
    onSave(payload);
    if (!expense) {
      setTitle("");
      setAmount("");
      setTags("");
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: "1rem" }}>
      <input
        placeholder="Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <input
        type="number"
        placeholder="Amount"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
      />
      <input
        placeholder="Tags (comma-separated)"
        value={tags}
        onChange={(e) => setTags(e.target.value)}
      />
      <button type="submit">{expense ? "Update" : "Add"} Expense</button>
    </form>
  );
}
