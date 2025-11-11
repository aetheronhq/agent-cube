import { Link } from 'react-router-dom';

export default function Navigation(): React.ReactElement {
  return (
    <nav className="bg-cube-gray border-b border-cube-light">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center space-x-6">
          <h1 className="text-xl font-bold">AgentCube</h1>
          <div className="flex space-x-4">
            <Link 
              to="/" 
              className="text-gray-300 hover:text-white transition-colors"
            >
              Dashboard
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
