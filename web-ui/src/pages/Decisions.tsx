import { useParams } from 'react-router-dom';

export default function Decisions() {
  const { id } = useParams<{ id: string }>();
  
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Decisions - Task {id}</h1>
      <p className="text-gray-400">Judge panel coming soon...</p>
    </div>
  );
}
