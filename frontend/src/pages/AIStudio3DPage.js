import React from 'react';
import Enhanced3DNavigation from '../components/Enhanced3DNavigation';
import AIStudio3D from '../components/AIStudio3D';
import { useAuth } from '../App';

// Page complète pour le Studio IA 3D
const AIStudio3DPage = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-indigo-900">
      <Enhanced3DNavigation user={user} />
      <div className="pt-20">
        <AIStudio3D />
      </div>
    </div>
  );
};

export default AIStudio3DPage;