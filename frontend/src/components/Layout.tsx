import { Link, Outlet } from 'react-router-dom';
import { Shield, LayoutDashboard, AlertTriangle, ClipboardList } from 'lucide-react';

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-cyber-panel border-r border-cyber-border flex flex-col">
        <div className="p-6 border-b border-cyber-border flex items-center gap-2">
          <Shield className="text-cyber-accent" size={28} />
          <h1 className="text-xl font-bold text-white">SME CyberShield</h1>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <Link to="/" className="flex items-center gap-3 px-4 py-2 rounded hover:bg-slate-700 transition">
            <LayoutDashboard size={18} /> Dashboard
          </Link>
          <Link to="/incidents" className="flex items-center gap-3 px-4 py-2 rounded hover:bg-slate-700 transition">
            <AlertTriangle size={18} /> Incidents
          </Link>
          <Link to="/onboarding" className="flex items-center gap-3 px-4 py-2 rounded hover:bg-slate-700 transition">
            <ClipboardList size={18} /> SME Setup
          </Link>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-8">
        <Outlet />
      </main>
    </div>
  );
}