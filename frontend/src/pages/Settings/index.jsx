import MainLayout from '../../components/layout/MainLayout';
import Card from '../../components/common/Card';
import { Settings as SettingsIcon, Bell, Shield, Database } from 'lucide-react';

export default function Settings() {
  const settings = [
    {
      icon: Bell,
      title: 'Notifications',
      description: 'Manage alert preferences and email settings',
      action: 'Configure',
    },
    {
      icon: Shield,
      title: 'Security',
      description: 'Change password and manage authentication',
      action: 'Update',
    },
    {
      icon: Database,
      title: 'Data & Privacy',
      description: 'Manage data retention and privacy settings',
      action: 'Manage',
    },
  ];

  return (
    <MainLayout title="Settings">
      <div className="space-y-4">
        {settings.map((setting, idx) => {
          const Icon = setting.icon;
          return (
            <Card key={idx} className="flex items-center justify-between hover:border-primary/50 transition-colors">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-lg bg-primary/20">
                  <Icon size={24} className="text-primary" />
                </div>
                <div>
                  <h3 className="text-white font-semibold">{setting.title}</h3>
                  <p className="text-gray-400 text-sm">{setting.description}</p>
                </div>
              </div>
              <button className="px-4 py-2 border border-primary text-primary hover:bg-primary/10 rounded-lg transition-colors">
                {setting.action}
              </button>
            </Card>
          );
        })}
      </div>
    </MainLayout>
  );
}
