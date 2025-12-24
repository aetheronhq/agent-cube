import type { JSX } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navigation from "./components/Navigation";
import Dashboard from "./pages/Dashboard";
import TaskDetail from "./pages/TaskDetail";
import { Decisions } from "./pages/Decisions";

function App(): JSX.Element {
  return (
    <BrowserRouter>
      <div className="h-screen flex flex-col bg-cube-dark text-white overflow-hidden">
        <Navigation />
        <main className="flex-1 overflow-auto">
          <div className="container mx-auto px-4 py-6 h-full">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/tasks/:id" element={<TaskDetail />} />
              <Route path="/tasks/:id/decisions" element={<Decisions />} />
            </Routes>
          </div>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
