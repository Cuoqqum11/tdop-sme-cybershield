import { useEffect, useState } from 'react';
import { getSummary, type Summary } from '../api/client';
import { ShieldCheck, AlertOctagon, Activity } from 'lucide-react';

export default function Dashboard() {
  const [data, setData] = useState<Summary | null>(null);

    useEffect(() => {
    const load = () =>
        getSummary()
        .then((res) => setData(res.data))
        .catch(() => setData(null));

    load();
    const timer = setInterval(load, 5000);
    return () => clearInterval(timer);
    }, []);

  if (!data) return <div className="text-center mt-20">Loading system status...</div>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Security Overview</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-cyber-panel p-6 rounded-lg border border-cyber-border">
          <div className="flex items-center gap-3 text-gray-400 mb-2">
            <Activity size={20} /> System Status
          </div>
          <p className="text-3xl font-bold text-cyber-success capitalize">{data.system_status}</p>
        </div>

        <div className="bg-cyber-panel p-6 rounded-lg border border-cyber-border">
          <div className="flex items-center gap-3 text-gray-400 mb-2">
            <AlertOctagon size={20} /> Total Alerts
          </div>
          <p className="text-3xl font-bold text-white">{data.total_alerts}</p>
        </div>

        <div className="bg-cyber-panel p-6 rounded-lg border border-cyber-border">
          <div className="flex items-center gap-3 text-gray-400 mb-2">
            <ShieldCheck size={20} /> Active Incidents
          </div>
          <p className="text-3xl font-bold text-cyber-accent">{data.total_incidents}</p>
          <p className="text-sm text-gray-500 mt-1">all-time: {data.total_incidents_all_time}</p>
        </div>
      </div>
    </div>
  );
}