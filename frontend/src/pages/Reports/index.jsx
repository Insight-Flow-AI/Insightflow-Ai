import { useState } from 'react';
import MainLayout from '../../components/layout/MainLayout';
import Card from '../../components/common/Card';
import Badge from '../../components/common/Badge';
import { Download, FileText, Calendar, Filter } from 'lucide-react';

export default function Reports() {
  const [selectedFormat, setSelectedFormat] = useState('pdf');
  const [dateRange, setDateRange] = useState({ from: '2026-05-01', to: '2026-05-20' });

  const reports = [
    {
      id: 1,
      title: 'May Performance Report',
      dataset: 'sales_data.csv',
      generatedAt: '2026-05-20 09:42 AM',
      summary: 'Your May revenue reached ₹24.6L, up 12.3% from last month. Key insights: North zone experienced a 18% dip, but South zone compensated with 25% growth. AI recommends revisiting pricing in North zone.',
      status: 'ready',
    },
    {
      id: 2,
      title: 'Q1 Strategic Review',
      dataset: 'quarterly_metrics.xlsx',
      generatedAt: '2026-05-18 02:15 PM',
      summary: 'Q1 analysis shows strong customer acquisition (+23% YoY) but retention challenges (down 5%). Churn primarily in high-value segment. Recommendation: Implement loyalty program targeting segment B.',
      status: 'ready',
    },
    {
      id: 3,
      title: 'Anomaly Deep Dive',
      dataset: 'customer_behavior.csv',
      generatedAt: '2026-05-15 11:30 AM',
      summary: 'Detected unusual spike in signup rate on May 18th (link to marketing campaign). Transaction latency increased 40% - root cause: unoptimized database query. Also identified churn risk in 234 accounts.',
      status: 'ready',
    },
  ];

  return (
    <MainLayout title="Reports" actionButton="Generate New">
      {/* Filters */}
      <Card className="mb-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Date Range */}
          <div>
            <label className="text-gray-400 text-sm block mb-2">From Date</label>
            <input
              type="date"
              value={dateRange.from}
              onChange={(e) => setDateRange({ ...dateRange, from: e.target.value })}
              className="w-full bg-dark-border text-white rounded px-3 py-2 outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div>
            <label className="text-gray-400 text-sm block mb-2">To Date</label>
            <input
              type="date"
              value={dateRange.to}
              onChange={(e) => setDateRange({ ...dateRange, to: e.target.value })}
              className="w-full bg-dark-border text-white rounded px-3 py-2 outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div>
            <label className="text-gray-400 text-sm block mb-2">Dataset</label>
            <select className="w-full bg-dark-border text-white rounded px-3 py-2 outline-none focus:ring-2 focus:ring-primary">
              <option>All Datasets</option>
              <option>sales_data.csv</option>
              <option>customer_metrics.xlsx</option>
            </select>
          </div>
          <div>
            <label className="text-gray-400 text-sm block mb-2">Export Format</label>
            <select
              value={selectedFormat}
              onChange={(e) => setSelectedFormat(e.target.value)}
              className="w-full bg-dark-border text-white rounded px-3 py-2 outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="pdf">PDF</option>
              <option value="excel">Excel</option>
              <option value="html">HTML</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Reports List */}
      <div className="space-y-4">
        {reports.map((report) => (
          <Card key={report.id} className="hover:border-primary/50 transition-colors">
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <FileText size={20} className="text-primary" />
                  <h3 className="text-lg font-semibold text-white">{report.title}</h3>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-gray-400 text-sm">{report.dataset}</span>
                  <span className="text-gray-500 text-sm">{report.generatedAt}</span>
                  <Badge variant="success">{report.status}</Badge>
                </div>
              </div>
              <button className="flex items-center gap-2 bg-primary hover:bg-primary-light text-white px-4 py-2 rounded-lg font-medium transition-colors">
                <Download size={16} />
                Export
              </button>
            </div>

            {/* AI-Generated Summary */}
            <div className="bg-dark-border/50 border border-primary/20 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-primary mb-2">AI Story Summary</h4>
              <p className="text-gray-300 text-sm leading-relaxed">{report.summary}</p>
            </div>

            {/* Quick Actions */}
            <div className="mt-4 flex gap-3">
              <button className="text-sm text-primary hover:text-primary-light transition-colors">
                View Full Report
              </button>
              <button className="text-sm text-gray-400 hover:text-white transition-colors">
                Share Report
              </button>
              <button className="text-sm text-gray-400 hover:text-white transition-colors">
                Schedule Export
              </button>
            </div>
          </Card>
        ))}
      </div>
    </MainLayout>
  );
}
