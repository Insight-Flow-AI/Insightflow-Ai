import { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import MainLayout from '../../components/layout/MainLayout';
import Card from '../../components/common/Card';
import { Send, Loader } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

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
      setLoading(true);

      // Simulate AI processing
      setTimeout(() => {
        const isTrend = query.toLowerCase().includes('trend') || query.toLowerCase().includes('q2') || query.toLowerCase().includes('revenue');
        const aiMessage = {
          id: Date.now() + 1,
          sender: 'ai',
          text: isTrend 
            ? 'Here is the revenue trend analysis for your query. The projection shows a positive linear trend entering Q3.'
            : `I've analyzed the dataset for "${query}". The metrics indicate stable customer engagement levels with localized optimization opportunities in segment B.`,
          chart: isTrend,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, aiMessage]);
        setLoading(false);
      }, 1000);
    }
  }, [location.state]);


  const handleSend = () => {
    if (!input.trim()) return;

    // Add user message
    const userMessage = {
      id: messages.length + 1,
      sender: 'user',
      text: input,
      timestamp: new Date(),
    };
    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const aiMessage = {
        id: messages.length + 2,
        sender: 'ai',
        text: `I found insights about "${input}". Let me analyze that for you...`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
      setLoading(false);
    }, 1000);
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
                <p className="text-sm mb-2">{msg.text}</p>
                {msg.chart && (
                  <div className="mt-4 bg-dark-border rounded-lg p-4">
                    <ResponsiveContainer width="100%" height={200}>
                      <LineChart data={SAMPLE_CHART_DATA}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#2D3748" />
                        <XAxis dataKey="month" stroke="#9CA3AF" />
                        <YAxis stroke="#9CA3AF" />
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
                          dataKey="revenue"
                          stroke="#534AB7"
                          strokeWidth={2}
                        />
                      </LineChart>
                    </ResponsiveContainer>
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
