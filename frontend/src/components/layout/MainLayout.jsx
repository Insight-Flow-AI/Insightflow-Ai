import Sidebar from './Sidebar';
import TopBar from './TopBar';

export default function MainLayout({ children, title, actionButton }) {
  return (
    <div className="flex min-h-screen bg-dark-bg">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="ml-64 flex-1 flex flex-col">
        {/* Top Bar */}
        <TopBar title={title} actionButton={actionButton} />

        {/* Page Content */}
        <div className="flex-1 overflow-auto">
          <div className="p-8">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
