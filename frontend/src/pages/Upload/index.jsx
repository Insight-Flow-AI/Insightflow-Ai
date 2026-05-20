import { useState } from 'react';
import MainLayout from '../../components/layout/MainLayout';
import Card from '../../components/common/Card';
import Badge from '../../components/common/Badge';
import { Upload as UploadIcon, CheckCircle, Clock, AlertCircle } from 'lucide-react';

const PIPELINE_STEPS = [
  { id: 1, name: 'Receive', description: 'File upload & validation' },
  { id: 2, name: 'Schema', description: 'Data structure analysis' },
  { id: 3, name: 'AI Analysis', description: 'ML preprocessing' },
  { id: 4, name: 'Dashboard', description: 'Chart generation' },
  { id: 5, name: 'Report', description: 'Summary creation' },
];

export default function Upload() {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([
    {
      id: 1,
      name: 'sales_data.csv',
      size: '2.4 MB',
      uploadedAt: '2 hours ago',
      currentStep: 3,
      status: 'processing',
    },
    {
      id: 2,
      name: 'customer_metrics.xlsx',
      size: '1.8 MB',
      uploadedAt: '5 hours ago',
      currentStep: 5,
      status: 'complete',
    },
  ]);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    // Handle file drop logic
  };

  return (
    <MainLayout title="Upload dataset" actionButton="Browse Files">
      {/* Drag & Drop Zone */}
      <div
        className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors mb-8 ${
          dragActive
            ? 'border-primary bg-primary/10'
            : 'border-dark-border hover:border-primary/50 bg-dark-card/50'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <UploadIcon size={48} className="mx-auto mb-4 text-primary" />
        <h3 className="text-xl font-semibold text-white mb-2">Drop your files here</h3>
        <p className="text-gray-400 mb-4">or click to browse. Supported: CSV, Excel, Parquet</p>
        <button className="bg-primary hover:bg-primary-light text-white px-6 py-2 rounded-lg font-medium transition-colors">
          Select Files
        </button>
      </div>

      {/* Pipeline Legend */}
      <Card className="mb-8">
        <h3 className="text-lg font-semibold text-white mb-6">Processing Pipeline</h3>
        <div className="flex items-center justify-between">
          {PIPELINE_STEPS.map((step, idx) => (
            <div key={step.id} className="flex flex-col items-center">
              <div className="w-10 h-10 rounded-full bg-primary/20 text-primary font-bold flex items-center justify-center mb-2">
                {step.id}
              </div>
              <p className="text-white text-sm font-medium text-center">{step.name}</p>
              <p className="text-gray-400 text-xs text-center">{step.description}</p>
              {idx < PIPELINE_STEPS.length - 1 && (
                <div className="absolute w-16 h-0.5 bg-dark-border -right-8 top-5 hidden lg:block"></div>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* Uploaded Files */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">Upload History</h3>
        <div className="space-y-4">
          {uploadedFiles.map((file) => (
            <Card key={file.id} className="hover:border-primary/50 transition-colors">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h4 className="text-white font-semibold mb-1">{file.name}</h4>
                  <p className="text-gray-400 text-sm">{file.size} • Uploaded {file.uploadedAt}</p>
                </div>
                <Badge variant={file.status === 'complete' ? 'success' : 'warning'}>
                  {file.status}
                </Badge>
              </div>

              {/* Pipeline Progress */}
              <div className="space-y-3">
                {/* Step Progress Bar */}
                <div className="flex items-center gap-2 mb-3">
                  {PIPELINE_STEPS.map((step) => (
                    <div
                      key={step.id}
                      className={`flex-1 h-1 rounded-full transition-colors ${
                        step.id <= file.currentStep
                          ? 'bg-primary'
                          : 'bg-dark-border'
                      }`}
                    ></div>
                  ))}
                </div>

                {/* Step Details */}
                <div className="grid grid-cols-5 gap-2">
                  {PIPELINE_STEPS.map((step) => {
                    let icon = null;
                    let color = 'text-gray-400';

                    if (step.id < file.currentStep) {
                      icon = <CheckCircle size={16} className="text-green-400" />;
                      color = 'text-green-400';
                    } else if (step.id === file.currentStep) {
                      icon = <Clock size={16} className="text-primary animate-spin" />;
                      color = 'text-primary';
                    }

                    return (
                      <div key={step.id} className={`text-xs text-center ${color}`}>
                        {icon && <div className="flex justify-center mb-1">{icon}</div>}
                        <span>{step.name}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </MainLayout>
  );
}
