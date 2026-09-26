import { useEffect, useState } from 'react';
import {
  getIncidents,
  getResponseHistory,
  approveAction,
  type Incident,
  type ResponseAction,
} from '../api/client.ts';
import { AlertTriangle, CheckCircle } from 'lucide-react';

export default function Incidents() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [actions, setActions] = useState<ResponseAction[]>([]);

  const fetchData = () => {
    getIncidents().then((res) => setIncidents(res.data));
    getResponseHistory().then((res) => setActions(res.data));
  };

    useEffect(() => {
    fetchData();
    const timer = setInterval(fetchData, 5000);
    return () => clearInterval(timer);
    }, []);

  const handleApprove = async (actionId: number) => {
    await approveAction(actionId);
    fetchData();
  };

  const getRiskColor = (score: number) => {
    if (score >= 80) return 'text-red-400 bg-red-900/30';
    if (score >= 50) return 'text-yellow-400 bg-yellow-900/30';
    return 'text-green-400 bg-green-900/30';
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Correlated Incidents</h2>
      <div className="space-y-4">
        {incidents.map((inc) => {
          const incActions = actions.filter((a) => a.incident_id === inc.id);
          return (
            <div key={inc.id} className="bg-cyber-panel border border-cyber-border rounded-lg p-6 shadow-lg">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-white flex items-center gap-2">
                    <AlertTriangle className="text-red-500" size={20} /> {inc.title}
                  </h3>
                  <p className="text-sm text-gray-400 mt-1">
                    Entity: <span className="text-cyber-accent">{inc.entity_type}: {inc.entity_value}</span>
                    &nbsp;|&nbsp; Alerts Grouped: <span className="font-bold">{inc.alert_count}</span>
                  </p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-bold ${getRiskColor(inc.risk_score)}`}>
                  Risk: {inc.risk_score}
                </span>
              </div>

              <div className="bg-slate-900/50 p-4 rounded border border-slate-700 mb-4">
                <h4 className="text-sm font-bold text-gray-300 mb-2 uppercase tracking-wider">AI Explanation</h4>
                <pre className="text-sm text-gray-300 whitespace-pre-wrap font-sans">{inc.explanation}</pre>
              </div>

              <div className="border-t border-cyber-border pt-4">
                <h4 className="text-sm font-bold text-gray-300 mb-3 uppercase tracking-wider">Recommended Response Actions</h4>
                <div className="flex flex-wrap gap-3">
                  {incActions.map((action) => (
                    <div key={action.id} className="flex items-center gap-2 bg-slate-800 px-4 py-2 rounded border border-slate-600">
                        {action.status === 'approved' || action.status === 'executed' ? (
                        <span className="flex items-center gap-2 text-green-400">
                            <CheckCircle size={16} /> {action.action_type} ({action.status === 'executed' ? 'Auto-Executed' : 'Executed'})
                        </span>
                        ) : (
                        <>
                            <span className="text-yellow-400 font-mono text-sm">{action.action_type}</span>
                            <button
                            onClick={() => handleApprove(action.id)}
                            className="ml-2 bg-cyber-accent text-slate-900 px-3 py-1 rounded text-xs font-bold hover:bg-sky-300 transition"
                            >
                            Approve & Execute
                            </button>
                        </>
                        )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}