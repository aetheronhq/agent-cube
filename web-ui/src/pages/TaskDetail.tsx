import { useParams } from 'react-router-dom';

export default function TaskDetail() {
  const { id } = useParams<{ id: string }>();
  
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Task {id}</h1>
      <p className="text-gray-400">Thinking boxes coming soon...</p>
    </div>
  );
}
