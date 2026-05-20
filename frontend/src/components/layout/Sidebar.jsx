import { Link, useLocation } from 'react-router-dom';
import { 
  BarChart3, 
  Upload, 
  Lightbulb, 
  MessageSquare, 
  FileText, 
  Settings, 
  LogOut,
  Zap,
  TrendingUp,
  AlertTriangle
} from 'lucide-react';

export default function Sidebar() {
  const location = useLocation();
  
  const sections = [
    {
      title: 'MAIN',
      items: [
        { icon: BarChart3, label: 'Overview', path: '/', id: 'dashboard' },
        { icon: Upload, label: 'Upload dataset', path: '/upload', id: 'upload' },
        { icon: Lightbulb, label: 'AI insights', path: '/insights', id: 'insights', badge: 3 },
        { icon: MessageSquare, label: 'Ask AI', path: '/chat', id: 'chat' },
      ]
    },
    {
      title: 'REPORTS',
      items: [
        { icon: FileText, label: 'Reports', path: '/reports', id: 'reports' },
        { icon: TrendingUp, label: 'Predictions', path: '/insights', id: 'predictions' },
      ]
    },
    {
      title: 'SYSTEM',
      items: [
        { icon: AlertTriangle, label: 'Alerts', path: '/insights', id: 'alerts', badge: 2 },
        { icon: Settings, label: 'Settings', path: '/settings', id: 'settings' },
      ]
    }
  ];

  const isActive = (path, id) => {
    if (id === 'predictions' || id === 'alerts') {
      return false; // Sub-elements are usually highlighted when active, but match mockup's simple navigation rules
    }
    return location.pathname === path;
  };

  return (
    <div className="w-64 bg-[#131313] border-r border-[#222222] flex flex-col justify-between py-6 fixed h-screen left-0 top-0 z-40 text-gray-300">
      <div>
        {/* Brand Header */}
        <div className="px-6 mb-8 flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[#534AB7] to-[#6B5AC9] flex items-center justify-center shadow-md shadow-primary/20">
            <Zap size={22} className="text-white" />
          </div>
          <div className="flex flex-col">
            <span className="text-white font-bold text-base tracking-wide">InsightFlow</span>
            <span className="text-gray-500 text-xs font-semibold uppercase tracking-wider">AI Analytics</span>
          </div>
        </div>

        {/* Navigation Sections */}
        <div className="px-4 space-y-7">
          {sections.map((section) => (
            <div key={section.title} className="space-y-1.5">
              <p className="px-3 text-[10px] font-bold tracking-widest text-gray-600 uppercase">
                {section.title}
              </p>
              <nav className="space-y-1">
                {section.items.map((item) => {
                  const Icon = item.icon;
                  const active = isActive(item.path, item.id);
                  return (
                    <Link
                      key={item.id}
                      to={item.path}
                      className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group ${
                        active
                          ? 'bg-[#252525] text-white'
                          : 'hover:text-white hover:bg-[#1C1C1C]'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <Icon 
                          size={18} 
                          className={`transition-colors duration-200 ${
                            active ? 'text-[#534AB7]' : 'text-gray-500 group-hover:text-gray-300'
                          }`} 
                        />
                        <span>{item.label}</span>
                      </div>
                      {item.badge && (
                        <span className="px-1.5 py-0.5 text-[10px] font-semibold text-white bg-[#534AB7] rounded-full min-w-[18px] text-center">
                          {item.badge}
                        </span>
                      )}
                    </Link>
                  );
                })}
              </nav>
            </div>
          ))}
        </div>
      </div>

      {/* Footer Profile Block */}
      <div className="px-4 pt-4 border-t border-[#222222]">
        <div className="flex items-center justify-between px-2">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-[#534AB7] to-[#6B5AC9] flex items-center justify-center font-bold text-white text-sm shadow">
              GS
            </div>
            <div className="flex flex-col">
              <span className="text-white text-sm font-semibold tracking-wide">Gurumurthy</span>
              <span className="text-gray-500 text-xs">Admin</span>
            </div>
          </div>
          <button 
            className="p-1.5 rounded-lg text-gray-500 hover:text-red-500 hover:bg-[#1C1C1C] transition-colors"
            title="Logout"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}

