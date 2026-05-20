import { useState } from 'react';
import MainLayout from '../../components/layout/MainLayout';
import Card from '../../components/common/Card';
import Badge from '../../components/common/Badge';
import { TrendingUp, AlertTriangle, Zap, PieChart } from 'lucide-react';
import { PieChart as RechartsPie, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const CLUSTER_DATA = [
  { name: 'High Value', value: 35 },
  { name: 'Medium Value', value: 45 },
  { name: 'Low Engagement', value: 20 },
];

const COLORS = ['#534AB7', '#10B981', '#F59E0B'];

export default function Insights() {
  const predictions = [
    {
      id: 1,
      title: 'Revenue Growth',
      prediction: '+₹2.4L',
      confidence: 92,
      timeframe: 'Next Quarter',
      icon: TrendingUp,
      color: 'from-green-600 to-green-400',
    },
    {
      id: 2,
      title: 'Customer Churn',
      prediction: '8.5%',
      confidence: 78,
      timeframe: 'Next 30 Days',
      icon: AlertTriangle,
      color: 'from-red-600 to-red-400',
    },
    {
      id: 3,
      title: 'Market Demand',
      prediction: '↑ 23%',
      confidence: 85,
      timeframe: 'Next Month',
      icon: Zap,
      color: 'from-yellow-600 to-yellow-400',
    },
  ];

  const anomalies = [
    {
      date: 'May 18',
      description: 'Unusual spike in signup rate',
      impact: 'Critical',
      rootCause: 'Marketing campaign launch',
    },
    {
      date: 'May 15',
      description: 'Transaction latency increased',
      impact: 'Medium',
      rootCause: 'Database query optimization needed',
    },
    {
      date: 'May 12',
      description: 'Customer retention dropped',
      impact: 'High',
      rootCause: 'Pricing change feedback',
    },
  ];

  return (
    <MainLayout title="AI Insights">
      {/* Predictions */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-white mb-4">AI Predictions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {predictions.map((pred) => {
            const Icon = pred.icon;
            return (
              <Card key={pred.id}>
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-3 rounded-lg bg-gradient-to-br ${pred.color} bg-opacity-20`}>
                    <Icon size={24} className="text-white" />
                  </div>
                  <Badge variant="primary">{pred.confidence}% confidence</Badge>
                </div>
                <h3 className="text-gray-400 text-sm font-medium mb-2">{pred.title}</h3>
                <p className="text-3xl font-bold text-white mb-3">{pred.prediction}</p>
                <p className="text-gray-500 text-xs">{pred.timeframe}</p>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Root Cause Analysis & K-Means Clustering */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Root Cause Analysis */}
        <Card>
          <h3 className="text-lg font-semibold text-white mb-6">Root Cause Analysis</h3>
          <div className="space-y-4">
            {anomalies.map((anomaly, idx) => (
              <div key={idx} className="border border-dark-border rounded-lg p-4 hover:bg-dark-border/30 transition-colors">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="text-white font-semibold text-sm">{anomaly.description}</p>
                    <p className="text-gray-400 text-xs mt-1">{anomaly.date}</p>
                  </div>
                  <Badge
                    variant={
                      anomaly.impact === 'Critical'
                        ? 'error'
                        : anomaly.impact === 'High'
                        ? 'warning'
                        : 'secondary'
                    }
                  >
                    {anomaly.impact}
                  </Badge>
                </div>
                <div className="bg-primary/10 border border-primary/30 rounded px-3 py-2 mt-3">
                  <p className="text-primary text-xs font-semibold">Root Cause</p>
                  <p className="text-gray-300 text-sm">{anomaly.rootCause}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* K-Means Clustering */}
        <Card>
          <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
            <PieChart size={20} />
            Customer Segmentation
          </h3>
          <ResponsiveContainer width="100%" height={280}>
            <RechartsPie>
              <Pie
                data={CLUSTER_DATA}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={4}
                dataKey="value"
              >
                {CLUSTER_DATA.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index]} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1A1F2E',
                  border: '1px solid #2D3748',
                  borderRadius: '8px',
                }}
                labelStyle={{ color: '#FFF' }}
              />
            </RechartsPie>
          </ResponsiveContainer>
          <div className="mt-6 space-y-2">
            {CLUSTER_DATA.map((cluster, idx) => (
              <div key={idx} className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[idx] }}></div>
                <span className="text-gray-300 text-sm">{cluster.name}: {cluster.value}%</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Anomaly Timeline */}
      <Card>
        <h3 className="text-lg font-semibold text-white mb-6">Anomaly Detection Timeline</h3>
        <div className="space-y-4">
          {anomalies.map((anomaly, idx) => (
            <div key={idx} className="flex gap-4 pb-4 border-b border-dark-border last:border-b-0">
              <div className="flex flex-col items-center pt-1">
                <div className="w-3 h-3 rounded-full bg-primary mb-2"></div>
                {idx < anomalies.length - 1 && <div className="w-0.5 h-12 bg-dark-border"></div>}
              </div>
              <div className="flex-1">
                <p className="text-white font-semibold">{anomaly.date}</p>
                <p className="text-gray-400 text-sm mt-1">{anomaly.description}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </MainLayout>
  );
}
