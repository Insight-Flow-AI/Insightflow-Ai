import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap } from 'lucide-react';

export default function Auth() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    // Mock authentication
    navigate('/');
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

      {/* Login Card */}
      <div className="w-full max-w-md">
        <div className="bg-dark-card border border-dark-border rounded-lg p-8">
          <h1 className="text-3xl font-bold text-white mb-2">Welcome Back</h1>
          <p className="text-gray-400 mb-8">Sign in to your InsightFlow AI account</p>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email */}
            <div>
              <label className="block text-gray-400 text-sm font-medium mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="guru@gmail.com"
                className="w-full bg-dark-border text-white rounded-lg px-4 py-3 outline-none focus:ring-2 focus:ring-primary placeholder-gray-500"
                required
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-gray-400 text-sm font-medium mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-dark-border text-white rounded-lg px-4 py-3 outline-none focus:ring-2 focus:ring-primary placeholder-gray-500"
                required
              />
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 text-gray-400 hover:text-white cursor-pointer">
                <input type="checkbox" className="w-4 h-4 rounded" />
                Remember me
              </label>
              <a href="#" className="text-primary hover:text-primary-light transition-colors">
                Forgot password?
              </a>
            </div>

            {/* Sign In Button */}
            <button
              type="submit"
              className="w-full bg-gradient-to-r from-primary to-primary-light hover:shadow-lg hover:shadow-primary/50 text-white font-bold py-3 rounded-lg transition-all duration-200"
            >
              Sign in
            </button>
          </form>

          {/* Sign Up Link */}
          <p className="text-center text-gray-400 text-sm mt-8">
            Don't have an account?{' '}
            <a href="#" className="text-primary hover:text-primary-light transition-colors font-semibold">
              Sign up
            </a>
          </p>
        </div>

        {/* Demo Credentials */}
        <p className="text-center text-gray-500 text-xs mt-6">
          Demo: guru@gmail.com / password123
        </p>
      </div>
    </div>
  );
}
