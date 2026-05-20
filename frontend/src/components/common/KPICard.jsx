export default function KPICard({ title, value, changeText, changeColor = 'text-green-400', icon: Icon }) {
  return (
    <div className="bg-[#1C1C1C] border border-[#2A2A2A] hover:border-gray-700 rounded-xl p-5 transition-all duration-300 shadow-sm flex flex-col justify-between">
      {/* Title & Icon */}
      <div className="flex items-center gap-2 text-gray-500 mb-4">
        {Icon && <Icon size={16} className="text-gray-500" />}
        <span className="text-xs font-semibold uppercase tracking-wider">{title}</span>
      </div>

      {/* Large Value */}
      <div className="mb-2">
        <span className="text-3xl font-bold text-white tracking-tight">{value}</span>
      </div>

      {/* Change / Subtext */}
      <div className={`text-xs font-semibold flex items-center gap-1 ${changeColor}`}>
        <span>{changeText}</span>
      </div>
    </div>
  );
}

