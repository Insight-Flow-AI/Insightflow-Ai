import { useNavigate } from 'react-router-dom';
import { Upload, ArrowUpRight } from 'lucide-react';

export default function TopBar({ title }) {
  const navigate = useNavigate();

  return (
    <div className="bg-[#181818] border-b border-[#222222] px-8 py-5 flex items-center justify-between z-30">
      {/* Title & Status */}
      <div className="flex flex-col">
        <h1 className="text-xl font-bold text-white tracking-wide">{title}</h1>
        <p className="text-gray-500 text-xs mt-1">Last updated: today at 09:42 AM</p>
      </div>

      {/* Right Action Buttons */}
      <div className="flex items-center gap-3">
        <button 
          onClick={() => navigate('/upload')}
          className="px-4 py-2 border border-[#333333] hover:border-gray-500 bg-[#252525] hover:bg-[#2e2e2e] text-white rounded-lg flex items-center gap-2 text-sm font-semibold transition-all duration-200 shadow-sm"
        >
          <Upload size={16} />
          <span>Upload</span>
        </button>

        <button 
          onClick={() => navigate('/chat')}
          className="px-4 py-2 border border-[#333333] hover:border-gray-500 bg-[#252525] hover:bg-[#2e2e2e] text-white rounded-lg flex items-center gap-2 text-sm font-semibold transition-all duration-200 shadow-sm"
        >
          <span>Ask AI</span>
          <ArrowUpRight size={16} className="text-gray-400" />
        </button>
      </div>
    </div>
  );
}

