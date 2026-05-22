import { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import MainLayout from '../../components/layout/MainLayout';
import Card from '../../components/common/Card';
import { Send, Loader, AlertTriangle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { analyticsService } from '../../services/analyticsService';

const SAMPLE_CHART_DATA = [
  { month: 'Q1', revenue: 4500 },
  { month: 'Q2', revenue: 5200 },
  { month: 'Q3', revenue: 4800 },
  { month: 'Q4', revenue: 5900 },
];

export default function Chat() {
  const location = useLocation();
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'ai',
      text: "Hi Gurumurthy! I've analyzed your latest dataset. Revenue is up 12% this month. How can I help?",
      timestamp: new Date(Date.now() - 5 * 60000),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const processAIQuery = async (query) => {
    setLoading(true);
    try {
      const response = await analyticsService.askChatbot(query);
      const isTrend = query.toLowerCase().includes('trend') || 
                      query.toLowerCase().includes('q2') || 
                      query.toLowerCase().includes('revenue') || 
                      query.toLowerCase().includes('sales') ||
                      query.toLowerCase().includes('profit');
      
      let chartData = null;
      if (isTrend) {
        try {
          const chartsData = await analyticsService.getCharts();
          if (chartsData && chartsData.revenueTrend) {
            chartData = chartsData.revenueTrend;
          }
        } catch (err) {
          console.error("Failed to load live charts data for chatbot balloon:", err);
        }
      }

      const aiMessage = {
        id: Date.now() + 1,
        sender: 'ai',
        text: response.answer || "I've processed your analytics inquiry successfully.",
        chartData: chartData,
        timestamp: new Date(response.timestamp || Date.now()),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      console.error("Failed to call chatbot microservice:", err);
      // Graceful offline fallback mode
      const isTrend = query.toLowerCase().includes('trend') || 
                      query.toLowerCase().includes('q2') || 
                      query.toLowerCase().includes('revenue') || 
                      query.toLowerCase().includes('sales');
      
      const fallbackText = isTrend
        ? `[Simulated Offline Answer] Here is the revenue trend analysis for "${query}". The projection shows a positive linear trend entering Q3.`
        : `[Simulated Offline Answer] I've analyzed the dataset for "${query}". The metrics indicate stable customer engagement levels with localized optimization opportunities in segment B.`;
      
      const aiMessage = {
        id: Date.now() + 1,
        sender: 'ai',
        text: fallbackText,
        chartData: isTrend ? SAMPLE_CHART_DATA : null,
        timestamp: new Date(),
        offlineNotice: true
      };

      setMessages((prev) => [...prev, aiMessage]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (location.state?.initialQuery) {
      const query = location.state.initialQuery;
      // Clear state so it doesn't re-trigger
      window.history.replaceState({}, document.title);

      // Add user message
      const userMessage = {
        id: Date.now(),
        sender: 'user',
        text: query,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      processAIQuery(query);
    }
  }, [location.state]);


  const handleSend = () => {
    if (!input.trim() || loading) return;
    const query = input;

    // Add user message
    const userMessage = {
      id: Date.now(),
      sender: 'user',
      text: query,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    processAIQuery(query);
  };

  return (
    <MainLayout title="Chat Analytics">
      <div className="h-screen flex flex-col bg-dark-bg">
        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-md lg:max-w-2xl ${
                  msg.sender === 'user'
                    ? 'bg-primary text-white rounded-lg rounded-tr-none'
                    : 'bg-dark-card border border-dark-border text-gray-300 rounded-lg rounded-tl-none'
                } p-4`}
              >
                {msg.offlineNotice && (
                  <div className="flex items-center gap-1.5 text-amber-500 text-[10px] font-bold mb-2">
                    <AlertTriangle size={12} />
                    <span>Connecting to AI service failed. Showing simulated offline insights.</span>
                  </div>
                )}
                <p className="text-sm mb-2">{msg.text}</p>
                
                {msg.chartData && (
                  <div className="mt-4 bg-[#1E1E1E] border border-[#2D3748] rounded-lg p-4">
                    <ResponsiveContainer width="100%" height={200}>
                      <LineChart data={msg.chartData}>
                        <CartesianGrid strokeDasharray="0" stroke="#252525" vertical={false} />
                        <XAxis 
                          dataKey={msg.chartData[0] && 'name' in msg.chartData[0] ? 'name' : 'month'} 
                          stroke="#555555" 
                          tick={{ fill: '#777777', fontSize: 10 }}
                          axisLine={false}
                          tickLine={false}
                        />
                        <YAxis 
                          stroke="#555555" 
                          tick={{ fill: '#777777', fontSize: 10 }}
                          axisLine={false}
                          tickLine={false}
                        />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#1A1F2E',
                            border: '1px solid #2D3748',
                            borderRadius: '8px',
                          }}
                          labelStyle={{ color: '#FFF' }}
                        />
                        <Line
                          type="monotone"
                          dataKey={msg.chartData[0] && 'Revenue' in msg.chartData[0] ? 'Revenue' : 'revenue'}
                          stroke="#534AB7"
                          strokeWidth={3}
                          dot={{ r: 3, stroke: '#534AB7', strokeWidth: 1, fill: '#534AB7' }}
                          activeDot={{ r: 5 }}
                        />
                        {msg.chartData[0] && 'Profit' in msg.chartData[0] && (
                          <Line
                            type="monotone"
                            dataKey="Profit"
                            stroke="#10B981"
                            strokeWidth={3}
                            strokeDasharray="5 5"
                            dot={{ r: 3, stroke: '#10B981', strokeWidth: 1, fill: '#10B981' }}
                            activeDot={{ r: 5 }}
                          />
                        )}
                      </LineChart>
                    </ResponsiveContainer>
                    <div className="flex items-center gap-4 mt-3 px-1 justify-start">
                      <div className="flex items-center gap-1.5">
                        <span className="w-2.5 h-2.5 rounded bg-[#534AB7] block"></span>
                        <span className="text-[10px] font-semibold text-gray-400">
                          {msg.chartData[0] && 'Revenue' in msg.chartData[0] ? 'Revenue' : 'Actual'}
                        </span>
                      </div>
                      {msg.chartData[0] && 'Profit' in msg.chartData[0] && (
                        <div className="flex items-center gap-1.5">
                          <span className="w-2.5 h-2.5 rounded bg-[#10B981] block"></span>
                          <span className="text-[10px] font-semibold text-gray-400">Profit</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
                
                <p className="text-xs mt-2 opacity-70">
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-dark-card border border-dark-border text-gray-300 rounded-lg rounded-tl-none p-4">
                <div className="flex items-center gap-2">
                  <Loader size={16} className="animate-spin" />
                  <span className="text-sm">Analyzing...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <Card className="m-6 mt-0 border-primary/50">
          <div className="flex items-center gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask InsightFlow AI... (e.g., 'Show me Q2 revenue trend')"
              className="flex-1 bg-transparent text-white placeholder-gray-400 outline-none"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              className="p-2 bg-primary hover:bg-primary-light disabled:opacity-50 text-white rounded-lg transition-colors"
            >
              <Send size={18} />
            </button>
          </div>
        </Card>
      </div>
    </MainLayout>
  );
}
