import { Lightbulb } from 'lucide-react';

export default function AIRecommendationCard({ title, description, icon: Icon = Lightbulb, variant = 'info' }) {
  const styles = {
    warning: {
      container: 'border border-[#FFE0B2] border-l-4 border-l-[#E68A00] bg-[#FFF5E6]',
      title: 'text-[#663C00] font-bold text-sm',
      description: 'text-[#805000] text-xs font-medium',
      icon: 'text-[#E68A00]',
    },
    success: {
      container: 'border border-[#C8E6C9] border-l-4 border-l-[#2E7D32] bg-[#E8F5E9]',
      title: 'text-[#1B5E20] font-bold text-sm',
      description: 'text-[#2E7D32] text-xs font-medium',
      icon: 'text-[#2E7D32]',
    },
    info: {
      container: 'border border-[#B3E5FC] border-l-4 border-l-[#1565C0] bg-[#E3F2FD]',
      title: 'text-[#0D47A1] font-bold text-sm',
      description: 'text-[#1565C0] text-xs font-medium',
      icon: 'text-[#1565C0]',
    },
  };

  const currentStyle = styles[variant] || styles.info;

  return (
    <div className={`rounded-lg p-4 transition-all duration-200 shadow-sm ${currentStyle.container}`}>
      <div className="flex items-start gap-3">
        <Icon size={18} className={`flex-shrink-0 mt-0.5 ${currentStyle.icon}`} />
        <div className="flex-1">
          <h4 className={currentStyle.title}>{title}</h4>
          <p className={`mt-1 leading-relaxed ${currentStyle.description}`}>{description}</p>
        </div>
      </div>
    </div>
  );
}

