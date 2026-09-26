import { useState } from 'react';
import { saveProfile, type SMEProfile } from '../api/client';
import { CheckCircle } from 'lucide-react';

const COMPANY_TYPES = ['Accounting', 'Retail', 'Education', 'Clinic', 'Manufacturing', 'Professional Services'];
const SIZES = ['1-10 computers', '11-50 computers', '51-100 computers'];
const SERVICES = ['Windows PCs', 'Linux server', 'Web server', 'Database', 'Accounting software', 'File sharing', 'Microsoft 365', 'Email server'];
const MODES = [
  { id: 'monitoring', label: 'Monitoring only', desc: 'Detect and explain. No response actions.' },
  { id: 'recommended', label: 'Recommended response', desc: 'System drafts actions, admin approves.' },
  { id: 'automated', label: 'Automated response', desc: 'Safe actions run automatically (dry-run for now).' },
];

export default function Onboarding() {
  const [step, setStep] = useState(0);
  const [saved, setSaved] = useState(false);
  const [form, setForm] = useState<SMEProfile>({
    company_type: '',
    company_size: '',
    services: '',
    security_mode: 'monitoring',
    language: 'vi',
  });

  const selectedServices = form.services ? form.services.split(', ') : [];

  const toggleService = (service: string) => {
    const next = selectedServices.includes(service)
      ? selectedServices.filter((s) => s !== service)
      : [...selectedServices, service];
    setForm({ ...form, services: next.join(', ') });
  };

  const submit = async () => {
    await saveProfile(form);
    setSaved(true);
  };

  if (saved) {
    return (
      <div className="max-w-2xl mx-auto mt-20 text-center">
        <CheckCircle className="mx-auto text-cyber-success" size={48} />
        <h2 className="text-2xl font-bold mt-4">Security profile saved</h2>
        <p className="text-gray-400 mt-2">
          SME CyberShield now monitors {form.company_type || 'your company'} ({form.company_size}) in "{form.security_mode}" mode.
        </p>
      </div>
    );
  }

  const cardClass = (active: boolean) =>
    `p-3 rounded border text-left ${active ? 'border-cyber-accent bg-slate-700' : 'border-cyber-border hover:border-slate-500'}`;

  return (
    <div className="max-w-2xl mx-auto">
      <h2 className="text-2xl font-bold mb-2">SME Setup Wizard</h2>
      <p className="text-gray-400 mb-6">Four quick questions — no cybersecurity expertise required.</p>

      <div className="flex gap-2 mb-6">
        {['Company', 'Size', 'Services', 'Security mode'].map((label, i) => (
          <div key={label}
            className={`flex-1 text-center text-xs py-1 rounded ${i === step ? 'bg-cyber-accent text-slate-900 font-bold' : 'bg-cyber-panel text-gray-400'}`}>
            {i + 1}. {label}
          </div>
        ))}
      </div>

      <div className="bg-cyber-panel border border-cyber-border rounded-lg p-6">
        {step === 0 && (
          <div className="grid grid-cols-2 gap-3">
            {COMPANY_TYPES.map((t) => (
              <button key={t} onClick={() => setForm({ ...form, company_type: t })} className={cardClass(form.company_type === t)}>
                {t}
              </button>
            ))}
          </div>
        )}

        {step === 1 && (
          <div className="space-y-3">
            {SIZES.map((s) => (
              <button key={s} onClick={() => setForm({ ...form, company_size: s })} className={`w-full ${cardClass(form.company_size === s)}`}>
                {s}
              </button>
            ))}
          </div>
        )}

        {step === 2 && (
          <div className="grid grid-cols-2 gap-3">
            {SERVICES.map((s) => (
              <button key={s} onClick={() => toggleService(s)} className={cardClass(selectedServices.includes(s))}>
                {s}
              </button>
            ))}
          </div>
        )}

        {step === 3 && (
          <div className="space-y-3">
            {MODES.map((m) => (
              <button key={m.id} onClick={() => setForm({ ...form, security_mode: m.id })} className={`w-full ${cardClass(form.security_mode === m.id)}`}>
                <div className="font-bold">{m.label}</div>
                <div className="text-sm text-gray-400">{m.desc}</div>
              </button>
            ))}
          </div>
        )}

        <div className="flex justify-between mt-6">
          <button onClick={() => setStep(Math.max(0, step - 1))} disabled={step === 0}
            className="px-4 py-2 rounded bg-slate-700 disabled:opacity-40">
            Back
          </button>
          {step < 3 ? (
            <button onClick={() => setStep(step + 1)} className="px-4 py-2 rounded bg-cyber-accent text-slate-900 font-bold">
              Next
            </button>
          ) : (
            <button onClick={submit} className="px-4 py-2 rounded bg-cyber-success text-slate-900 font-bold">
              Save & Finish
            </button>
          )}
        </div>
      </div>
    </div>
  );
}