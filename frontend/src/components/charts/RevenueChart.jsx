import { useNavigate } from 'react-router-dom';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

const data = [
  { month: 'Nov', Actual: 4500, Predicted: 4200 },
  { month: 'Dec', Actual: 5200, Predicted: 5100 },
  { month: 'Jan', Actual: 4800, Predicted: 5300 },
  { month: 'Feb', Actual: 5900, Predicted: 5800 },
  { month: 'Mar', Actual: 6200, Predicted: 6400 },
  { month: 'Apr', Actual: 7100, Predicted: 7200 },
  { month: 'May', Actual: 8200, Predicted: 8100 },
];

export default function RevenueChart() {
  const navigate = useNavigate();

  return (
    <div className="bg-[#1C1C1C] border border-[#2A2A2A] rounded-xl p-6 shadow-sm">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <h3 className="text-base font-semibold text-white">Revenue trend — last 7 months</h3>
        <button 
          onClick={() => navigate('/insights')}
          className="text-xs font-semibold text-[#534AB7] hover:text-[#6B5AC9] transition-colors flex items-center"
        >
          View full ↗
        </button>
      </div>

      {/* Chart */}
      <div className="h-[260px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="0" stroke="#252525" vertical={false} />
            <XAxis 
              dataKey="month" 
              stroke="#555555" 
              tick={{ fill: '#777777', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              dy={10}
            />
            <YAxis 
              stroke="#555555" 
              tick={{ fill: '#777777', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              dx={-5}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1E1E1E',
                border: '1px solid #333333',
                borderRadius: '8px',
                color: '#E5E7EB',
              }}
              labelStyle={{ color: '#FFF', fontWeight: 'bold' }}
            />
            <Line
              type="monotone"
              dataKey="Actual"
              stroke="#534AB7"
              strokeWidth={3}
              dot={{ r: 4, stroke: '#534AB7', strokeWidth: 1, fill: '#534AB7' }}
              activeDot={{ r: 6 }}
            />
            <Line
              type="monotone"
              dataKey="Predicted"
              stroke="#10B981"
              strokeWidth={3}
              strokeDasharray="5 5"
              dot={{ r: 4, stroke: '#10B981', strokeWidth: 1, fill: '#10B981' }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Custom Legend */}
      <div className="flex items-center gap-6 mt-6 px-2 justify-start">
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded bg-[#534AB7] block"></span>
          <span className="text-xs font-semibold text-gray-400">Actual</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded bg-[#10B981] block"></span>
          <span className="text-xs font-semibold text-gray-400">Predicted</span>
        </div>
      </div>
    </div>
  );
}

