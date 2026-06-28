import { Outlet, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { LogOut, Scissors, User } from 'lucide-react';

export const Layout = () => {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-surface-950 flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 glass-card mx-4 mt-4 px-6 py-4 flex justify-between items-center rounded-2xl mb-8">
        <Link to="/" className="flex items-center gap-2 group">
          <div className="bg-brand-600 p-2 rounded-xl group-hover:scale-105 transition-transform glow">
            <Scissors className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight text-white">
            Clipo<span className="text-brand-500">AI</span>
          </span>
        </Link>

        {user && (
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 text-surface-300">
              <User className="w-4 h-4" />
              <span className="text-sm font-medium">{user.email}</span>
            </div>
            <button 
              onClick={logout}
              className="flex items-center gap-2 text-surface-400 hover:text-brand-400 transition-colors"
            >
              <LogOut className="w-5 h-5" />
              <span className="text-sm font-medium">Log out</span>
            </button>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 pb-12">
        <Outlet />
      </main>
    </div>
  );
};
