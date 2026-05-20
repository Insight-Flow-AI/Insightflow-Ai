export default function Card({ children, className = '' }) {
  return (
    <div className={`bg-dark-card border border-dark-border rounded-lg p-6 ${className}`}>
      {children}
    </div>
  );
}
