import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Expenses from "./pages/Expenses";
import Analytics from "./pages/Analytics";

export default function App() {
  return (
    <Router>
      <nav style={{ padding: "1rem", borderBottom: "1px solid #ddd" }}>
        <Link to="/expenses" style={{ marginRight: "1rem" }}>Expenses</Link>
        <Link to="/analytics">Analytics</Link>
      </nav>

      <Routes>
        <Route path="/expenses" element={<Expenses />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="*" element={<Expenses />} /> {/* default route */}
      </Routes>
    </Router>
  );
}
