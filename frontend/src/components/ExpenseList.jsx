// File: frontend/src/components/ExpenseList.jsx
export default function ExpenseList({ expenses = [], onEdit, onDelete }) {
  return (
    <ul>
      {expenses.map((exp) => {
        const tagNames = (exp.tags || [])
          .map((t) => (typeof t === "string" ? t : t?.name ?? ""))
          .filter(Boolean)
          .join(", ");
        return (
          <li key={exp.id}>
            {exp.title} - ${exp.amount} - Tags: {tagNames}
            <button onClick={() => onEdit(exp)}>Edit</button>
            <button onClick={() => onDelete(exp.id)}>Delete</button>
          </li>
        );
      })}
    </ul>
  );
}
