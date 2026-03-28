import { Routes, Route } from "react-router-dom";
import Home from '@/pages/Home';
import Dashboard from '@/pages/Dashboard';
import DocumentDetail from '@/pages/DocumentDetail';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/documents/:id" element={<DocumentDetail />} />
    </Routes>
  );
}