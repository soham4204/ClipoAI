import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Scissors, AlertCircle } from 'lucide-react';
import { authApi } from '../api';

export const Signup = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    setLoading(true);

    try {
      await authApi.signup({ email, password });
      // After successful signup, log them in
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);
      
      const res = await authApi.login(formData);
      localStorage.setItem('token', res.access_token);
      // Force reload to update auth context
      window.location.href = '/';
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create account.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-950 p-4">
      <div className="glass-card w-full max-w-md p-8 animate-fade-in">
        <div className="flex flex-col items-center mb-8">
          <div className="bg-brand-600 p-3 rounded-2xl mb-4 glow">
            <Scissors className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Create Account</h1>
          <p className="text-surface-400 text-center">Join ClipoAI to automate your content</p>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/50 rounded-xl p-4 flex items-start gap-3 mb-6">
            <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
            <p className="text-red-200 text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-surface-300 mb-1.5">Email Address</label>
            <input 
              type="email" 
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-surface-900 border border-surface-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-colors"
              placeholder="you@example.com"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-surface-300 mb-1.5">Password</label>
            <input 
              type="password" 
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-surface-900 border border-surface-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-colors"
              placeholder="••••••••"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-surface-300 mb-1.5">Confirm Password</label>
            <input 
              type="password" 
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full bg-surface-900 border border-surface-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500 transition-colors"
              placeholder="••••••••"
            />
          </div>

          <button 
            type="submit" 
            disabled={loading}
            className="w-full btn-primary mt-2 flex justify-center items-center gap-2"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        <p className="mt-6 text-center text-surface-400 text-sm">
          Already have an account? <Link to="/login" className="text-brand-400 hover:text-brand-300 font-medium">Log in</Link>
        </p>
      </div>
    </div>
  );
};
