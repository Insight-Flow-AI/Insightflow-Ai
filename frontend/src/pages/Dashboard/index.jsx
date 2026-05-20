import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MainLayout from '../../components/layout/MainLayout';
import KPICard from '../../components/common/KPICard';
import RevenueChart from '../../components/charts/RevenueChart';
import AIRecommendationCard from '../../components/common/AIRecommendationCard';
import { 
  Lightbulb, 
  TrendingUp, 
  Users, 
  Database, 
  AlertTriangle,
  UploadCloud,
  Send
} from 'lucide-react';

export default function Dashboard() {
  const navigate = useNavigate();
  const [chatInput, setChatInput] = useState('');

  const recommendations = [
    {
      icon: TrendingUp,
      title: 'Revenue dip detected',
      description: 'North zone down 18% — review pricing strategy.',
      variant: 'warning',
    },
    {
      icon: TrendingUp,
      title: 'Increase ad spend',
      description: 'Model predicts 12% lift with ₹50K ad budget.',
      variant: 'success',
    },
    {
      icon: Users,
      title: 'Segment opportunity',
      description: 'Cluster B customers show 3× higher LTV potential.',
      variant: 'info',
    },
  ];

  const handleChatSubmit = (e) => {
    e.preventDefault();
    if (chatInput.trim()) {
      navigate('/chat', { state: { initialQuery: chatInput } });
    }
  };

  return (
    <MainLayout title="Overview dashboard">
      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <KPICard
          title="Total revenue"
          value="₹24.6L"
          changeText="↑ +12.3% vs last month"
          changeColor="text-green-500"
          icon={TrendingUp}
        />
        <KPICard
          title="Active users"
          value="8,412"
          changeText="↑ +5.7% this week"
          changeColor="text-green-500"
          icon={Users}
        />
        <KPICard
          title="Anomalies"
          value="3"
          changeText="⚠ 2 new today"
          changeColor="text-red-500"
          icon={AlertTriangle}
        />
        <KPICard
          title="Datasets"
          value="17"
          changeText="⟳ 4 processing"
          changeColor="text-gray-500"
          icon={Database}
        />
      </div>

      {/* Main Core Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Revenue Trend Chart */}
        <div className="lg:col-span-2">
          <RevenueChart />
        </div>

        {/* AI Recommendations Panel */}
        <div className="bg-[#1C1C1C] border border-[#2A2A2A] rounded-xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-base font-semibold text-white flex items-center gap-2">
                <Lightbulb size={18} className="text-[#534AB7]" />
                AI recommendations
              </h3>
              <span className="px-2 py-0.5 text-[10px] font-bold text-white bg-[#534AB7] rounded-full">
                3 new
              </span>
            </div>
            
            <div className="space-y-3.5">
              {recommendations.map((rec, idx) => (
                <AIRecommendationCard key={idx} {...rec} />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Grid Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Dataset Pipeline Card */}
        <div className="bg-[#1C1C1C] border border-[#2A2A2A] rounded-xl p-6 lg:col-span-2">
          <div className="flex items-center justify-between mb-5">
            <h3 className="text-base font-semibold text-white flex items-center gap-2">
              <Database size={18} className="text-[#534AB7]" />
              Dataset pipeline
            </h3>
            <button 
              onClick={() => navigate('/upload')}
              className="text-xs font-semibold text-[#534AB7] hover:text-[#6B5AC9] transition-colors"
            >
              View all
            </button>
          </div>

          {/* Dotted Drag & Drop box */}
          <div 
            onClick={() => navigate('/upload')}
            className="border border-dashed border-[#444444] hover:border-[#534AB7] bg-[#141414] rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all duration-300 group"
          >
            <UploadCloud size={40} className="text-gray-600 group-hover:text-[#534AB7] mb-3 transition-colors duration-300" />
            <span className="text-sm font-semibold text-gray-300 group-hover:text-white transition-colors">
              Drag CSV / Excel here
            </span>
            <span className="text-xs text-gray-500 mt-1">
              or click to browse local files
            </span>
          </div>
        </div>

        {/* Ask InsightFlow AI Quick Panel */}
        <div className="bg-[#1C1C1C] border border-[#2A2A2A] rounded-xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-base font-semibold text-white">Ask InsightFlow AI</h3>
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                <span className="text-[10px] font-semibold text-gray-400">NLP analytics — online</span>
              </div>
            </div>

            {/* Simulated Chat Feed */}
            <div className="space-y-4 mb-4">
              <div className="bg-[#252525] border border-[#333333] text-gray-300 text-xs rounded-xl rounded-tl-none p-3.5 leading-relaxed shadow-sm">
                Hi Gurumurthy! I've analysed your latest dataset. Revenue is up 12% this month. What would you like to see?
              </div>
            </div>
          </div>

          {/* Quick Chat Input */}
          <form onSubmit={handleChatSubmit} className="relative mt-auto">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Ask AI... (e.g. 'Show me Q2 trend')"
              className="w-full bg-[#141414] border border-[#2A2A2A] hover:border-gray-700 focus:border-[#534AB7] text-white placeholder-gray-500 text-xs rounded-lg pl-3 pr-10 py-3.5 outline-none transition-all duration-200"
            />
            <button
              type="submit"
              disabled={!chatInput.trim()}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white disabled:opacity-30 disabled:hover:text-gray-500 transition-colors"
            >
              <Send size={14} />
            </button>
          </form>
        </div>
      </div>
    </MainLayout>
  );
}

