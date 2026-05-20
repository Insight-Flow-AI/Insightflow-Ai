export default function Badge({ children, variant = 'primary', className = '' }) {
  const variants = {
    primary: 'bg-primary/20 text-primary border border-primary/50',
    success: 'bg-green-900/20 text-green-400 border border-green-500/50',
    warning: 'bg-yellow-900/20 text-yellow-400 border border-yellow-500/50',
    error: 'bg-red-900/20 text-red-400 border border-red-500/50',
    secondary: 'bg-dark-border text-gray-300',
  };

  return (
    <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
}
