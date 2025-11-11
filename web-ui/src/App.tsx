import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import TaskDetail from './pages/TaskDetail';
import Decisions from './pages/Decisions';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-cube-dark text-white">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tasks/:id" element={<TaskDetail />} />
            <Route path="/tasks/:id/decisions" element={<Decisions />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
