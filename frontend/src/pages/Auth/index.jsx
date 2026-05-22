import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap, Loader2, AlertCircle, CheckCircle } from 'lucide-react';
import { authService } from '../../services/authService';

export default function Auth() {
  const [isRegistering, setIsRegistering] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      if (isRegistering) {
        // Register API flow
        await authService.register(name, email, password);
        setSuccess('Account created successfully! Please sign in.');
        setIsRegistering(false);
        setPassword('');
      } else {
        // Login API flow
        await authService.login(email, password);
        navigate('/');
      }
    } catch (err) {
      console.warn('API connection failed, falling back to simulated local mock login.', err);
      
      if (!isRegistering && email === 'guru@gmail.com' && password === 'password123') {
        // Successful mock fall-through for demo credentials
        localStorage.setItem('token', 'mock-jwt-token-key');
        localStorage.setItem('user', JSON.stringify({
          id: 'mock-123',
          name: 'S. Gurumurthy',
          email: 'guru@gmail.com',
          role: 'ROLE_ADMIN'
        }));
        setSuccess('Backend offline. Logged in via simulated local demo mode.');
        setTimeout(() => navigate('/'), 1200);
      } else {
        setError(err.message || 'Connection failed. Please check credentials or start the backend.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-bg via-dark-card to-dark-bg flex items-center justify-center p-4">
      {/* Logo */}
      <div className="absolute top-8 left-8 flex items-center gap-2">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-primary-light flex items-center justify-center">
          <Zap size={24} className="text-white" />
        </div>
        <span className="text-white font-bold text-lg">InsightFlow AI</span>
      </div>

      {/* Auth Card */}
      <div className="w-full max-w-md mt-12">
        <div className="bg-dark-card border border-dark-border rounded-xl p-8 shadow-xl">
          <h1 className="text-3xl font-bold text-white mb-2">
            {isRegistering ? 'Register / Sign Up' : 'Welcome Back'}
          </h1>
          <p className="text-gray-400 mb-6">
            {isRegistering
              ? 'Get started with your InsightFlow AI analytics workspace'
              : 'Sign in to your InsightFlow AI account'}
          </p>

          {/* Status Banners */}
          {error && (
            <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-lg p-3.5 mb-6">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div className="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs rounded-lg p-3.5 mb-6">
              <CheckCircle size={16} />
              <span>{success}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Name - only for signup */}
            {isRegistering && (
              <div>
                <label className="block text-gray-400 text-xs font-semibold mb-2 uppercase tracking-wider">Full Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Gurumurthy"
                  className="w-full bg-[#141414] border border-[#2A2A2A] focus:border-[#534AB7] text-white rounded-lg px-4 py-3 outline-none transition-colors"
                  required
                />
              </div>
            )}

            {/* Email */}
            <div>
              <label className="block text-gray-400 text-xs font-semibold mb-2 uppercase tracking-wider">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="guru@gmail.com"
                className="w-full bg-[#141414] border border-[#2A2A2A] focus:border-[#534AB7] text-white rounded-lg px-4 py-3 outline-none transition-colors"
                required
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-gray-400 text-xs font-semibold mb-2 uppercase tracking-wider">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-[#141414] border border-[#2A2A2A] focus:border-[#534AB7] text-white rounded-lg px-4 py-3 outline-none transition-colors"
                required
              />
            </div>

            {/* Remember Me / Support Options - only for login */}
            {!isRegistering && (
              <div className="flex items-center justify-between text-xs">
                <label className="flex items-center gap-2 text-gray-400 hover:text-white cursor-pointer select-none">
                  <input type="checkbox" className="accent-primary w-4 h-4 rounded border-dark-border" />
                  Remember me
                </label>
                <a href="#" className="text-[#8C82F2] hover:text-[#A199F5] font-medium underline transition-colors">
                  Forgot password?
                </a>
              </div>
            )}

            {/* Action Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-primary to-primary-light hover:shadow-lg hover:shadow-primary/30 text-white font-semibold py-3.5 rounded-lg disabled:opacity-50 transition-all duration-200"
            >
              {loading ? (
                <Loader2 size={16} className="animate-spin" />
              ) : isRegistering ? (
                'Register'
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Toggle Screen Link */}
          <p className="text-center text-gray-400 text-xs mt-8 select-none">
            {isRegistering ? 'Already have an account? ' : "Don't have an account? "}
            <button
              type="button"
              onClick={() => {
                setIsRegistering(!isRegistering);
                setError('');
                setSuccess('');
              }}
              className="text-[#8C82F2] hover:text-[#A199F5] font-semibold underline transition-colors focus:outline-none"
            >
              {isRegistering ? 'Sign In' : 'Register / Sign Up'}
            </button>
          </p>
        </div>

        {/* Demo Credentials */}
        <p className="text-center text-gray-500 text-[11px] mt-6">
          Demo Credentials: <span className="text-gray-400">guru@gmail.com</span> / <span className="text-gray-400">password123</span>
        </p>
      </div>
    </div>
  );
}
