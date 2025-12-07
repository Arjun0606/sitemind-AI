import { useState } from 'react';
import Head from 'next/head';

// Types
interface TeamMember {
  name: string;
  phone: string;
  role: string;
}

interface Site {
  name: string;
  address: string;
  city: string;
  team: TeamMember[];
}

interface OnboardingData {
  companyName: string;
  adminName: string;
  adminEmail: string;
  adminPhone: string;
  plan: string;
  language: string;
  assistantName: string;
  morningBriefTime: string;
  sites: Site[];
}

const INITIAL_DATA: OnboardingData = {
  companyName: '',
  adminName: '',
  adminEmail: '',
  adminPhone: '',
  plan: 'pilot',
  language: 'hinglish',
  assistantName: 'SiteMind',
  morningBriefTime: '07:00',
  sites: [{ name: '', address: '', city: '', team: [] }],
};

const ROLES = [
  { value: 'site_engineer', label: 'Site Engineer', description: 'On-ground queries & photos' },
  { value: 'pm', label: 'Project Manager', description: 'Full project access' },
  { value: 'consultant', label: 'Consultant', description: 'External - limited access' },
  { value: 'viewer', label: 'Viewer', description: 'Read-only access' },
];

export default function OnboardingPage() {
  const [step, setStep] = useState(1);
  const [data, setData] = useState<OnboardingData>(INITIAL_DATA);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);

  const totalSteps = 5;

  const updateData = (field: string, value: any) => {
    setData(prev => ({ ...prev, [field]: value }));
  };

  const updateSite = (index: number, field: string, value: any) => {
    setData(prev => {
      const newSites = [...prev.sites];
      newSites[index] = { ...newSites[index], [field]: value };
      return { ...prev, sites: newSites };
    });
  };

  const addSite = () => {
    setData(prev => ({
      ...prev,
      sites: [...prev.sites, { name: '', address: '', city: '', team: [] }],
    }));
  };

  const removeSite = (index: number) => {
    setData(prev => ({
      ...prev,
      sites: prev.sites.filter((_, i) => i !== index),
    }));
  };

  const addTeamMember = (siteIndex: number) => {
    setData(prev => {
      const newSites = [...prev.sites];
      newSites[siteIndex].team.push({ name: '', phone: '', role: 'site_engineer' });
      return { ...prev, sites: newSites };
    });
  };

  const updateTeamMember = (siteIndex: number, memberIndex: number, field: string, value: string) => {
    setData(prev => {
      const newSites = [...prev.sites];
      newSites[siteIndex].team[memberIndex] = {
        ...newSites[siteIndex].team[memberIndex],
        [field]: value,
      };
      return { ...prev, sites: newSites };
    });
  };

  const removeTeamMember = (siteIndex: number, memberIndex: number) => {
    setData(prev => {
      const newSites = [...prev.sites];
      newSites[siteIndex].team = newSites[siteIndex].team.filter((_, i) => i !== memberIndex);
      return { ...prev, sites: newSites };
    });
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    // Format phone numbers
    const formatPhone = (phone: string) => {
      let p = phone.replace(/\s|-/g, '');
      if (!p.startsWith('+')) {
        p = p.startsWith('91') ? `+${p}` : `+91${p}`;
      }
      return p;
    };

    const payload = {
      company_name: data.companyName,
      admin_name: data.adminName,
      admin_email: data.adminEmail,
      admin_phone: formatPhone(data.adminPhone),
      plan: data.plan,
      sites: data.sites.map(site => ({
        name: site.name,
        address: site.address,
        city: site.city,
        team: site.team.map(m => ({
          name: m.name,
          phone: formatPhone(m.phone),
          role: m.role,
        })),
      })),
    };

    try {
      // In production, this would call the API
      // const res = await fetch('/api/admin/quick-setup', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(payload),
      // });
      // const result = await res.json();
      
      // Mock result for demo
      await new Promise(resolve => setTimeout(resolve, 1500));
      setResult({
        success: true,
        organization: { id: 'org_' + Math.random().toString(36).substr(2, 9), name: data.companyName },
        projects_created: data.sites.length,
        users_added: data.sites.reduce((sum, s) => sum + s.team.length, 0) + 1,
        welcome_messages: [
          { name: data.adminName, phone: formatPhone(data.adminPhone), role: 'owner' },
          ...data.sites.flatMap(s => s.team.map(t => ({ name: t.name, phone: formatPhone(t.phone), role: t.role }))),
        ],
      });
      setStep(6);
    } catch (error) {
      console.error(error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const canProceed = () => {
    switch (step) {
      case 1:
        return data.companyName.trim() !== '';
      case 2:
        return data.adminName.trim() !== '' && data.adminPhone.trim() !== '';
      case 3:
        return data.sites.every(s => s.name.trim() !== '');
      case 4:
        return true;
      case 5:
        return true;
      default:
        return false;
    }
  };

  return (
    <>
      <Head>
        <title>Customer Onboarding | SiteMind Admin</title>
      </Head>

      <div className="min-h-screen bg-slate-950 text-white">
        {/* Header */}
        <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur">
          <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-lg flex items-center justify-center font-bold">
                SM
              </div>
              <div>
                <h1 className="font-semibold">Customer Onboarding</h1>
                <p className="text-sm text-slate-400">Set up a new customer in minutes</p>
              </div>
            </div>
            {step <= 5 && (
              <div className="text-sm text-slate-400">
                Step {step} of {totalSteps}
              </div>
            )}
          </div>
        </header>

        {/* Progress Bar */}
        {step <= 5 && (
          <div className="max-w-4xl mx-auto px-6 pt-6">
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map(s => (
                <div
                  key={s}
                  className={`h-1 flex-1 rounded-full transition-colors ${
                    s <= step ? 'bg-blue-500' : 'bg-slate-700'
                  }`}
                />
              ))}
            </div>
            <div className="flex justify-between mt-2 text-xs text-slate-500">
              <span>Company</span>
              <span>Admin</span>
              <span>Sites</span>
              <span>Team</span>
              <span>Settings</span>
            </div>
          </div>
        )}

        {/* Content */}
        <main className="max-w-4xl mx-auto px-6 py-8">
          {/* Step 1: Company */}
          {step === 1 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold mb-2">Company Details</h2>
                <p className="text-slate-400">Let's start with the basics</p>
              </div>

              <div className="bg-slate-900 rounded-xl p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Company Name *
                  </label>
                  <input
                    type="text"
                    value={data.companyName}
                    onChange={e => updateData('companyName', e.target.value)}
                    placeholder="ABC Builders Pvt Ltd"
                    className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Plan
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {[
                      { value: 'pilot', label: 'Pilot', desc: '3 months free' },
                      { value: 'standard', label: 'Standard', desc: '$500/site/mo' },
                      { value: 'enterprise', label: 'Enterprise', desc: 'Custom' },
                    ].map(plan => (
                      <button
                        key={plan.value}
                        onClick={() => updateData('plan', plan.value)}
                        className={`p-4 rounded-lg border-2 text-left transition-colors ${
                          data.plan === plan.value
                            ? 'border-blue-500 bg-blue-500/10'
                            : 'border-slate-700 hover:border-slate-600'
                        }`}
                      >
                        <div className="font-medium">{plan.label}</div>
                        <div className="text-sm text-slate-400">{plan.desc}</div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Admin */}
          {step === 2 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold mb-2">Admin Details</h2>
                <p className="text-slate-400">Primary contact with full access</p>
              </div>

              <div className="bg-slate-900 rounded-xl p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Name *
                    </label>
                    <input
                      type="text"
                      value={data.adminName}
                      onChange={e => updateData('adminName', e.target.value)}
                      placeholder="Rajesh Sharma"
                      className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Email
                    </label>
                    <input
                      type="email"
                      value={data.adminEmail}
                      onChange={e => updateData('adminEmail', e.target.value)}
                      placeholder="rajesh@company.com"
                      className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Phone (WhatsApp) *
                  </label>
                  <div className="flex">
                    <span className="px-4 py-3 bg-slate-700 border border-slate-600 border-r-0 rounded-l-lg text-slate-400">
                      +91
                    </span>
                    <input
                      type="tel"
                      value={data.adminPhone}
                      onChange={e => updateData('adminPhone', e.target.value)}
                      placeholder="9876543210"
                      className="flex-1 px-4 py-3 bg-slate-800 border border-slate-700 rounded-r-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Sites */}
          {step === 3 && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold mb-2">Sites / Projects</h2>
                  <p className="text-slate-400">Add construction sites to manage</p>
                </div>
                <button
                  onClick={addSite}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-sm font-medium transition-colors"
                >
                  + Add Site
                </button>
              </div>

              <div className="space-y-4">
                {data.sites.map((site, i) => (
                  <div key={i} className="bg-slate-900 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-medium text-lg">Site {i + 1}</h3>
                      {data.sites.length > 1 && (
                        <button
                          onClick={() => removeSite(i)}
                          className="text-red-400 hover:text-red-300 text-sm"
                        >
                          Remove
                        </button>
                      )}
                    </div>
                    <div className="grid grid-cols-3 gap-4">
                      <div className="col-span-3 sm:col-span-1">
                        <label className="block text-sm text-slate-400 mb-1">Site Name *</label>
                        <input
                          type="text"
                          value={site.name}
                          onChange={e => updateSite(i, 'name', e.target.value)}
                          placeholder="Skyline Towers"
                          className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div className="col-span-3 sm:col-span-1">
                        <label className="block text-sm text-slate-400 mb-1">Address</label>
                        <input
                          type="text"
                          value={site.address}
                          onChange={e => updateSite(i, 'address', e.target.value)}
                          placeholder="Sector 62, Noida"
                          className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <div className="col-span-3 sm:col-span-1">
                        <label className="block text-sm text-slate-400 mb-1">City</label>
                        <input
                          type="text"
                          value={site.city}
                          onChange={e => updateSite(i, 'city', e.target.value)}
                          placeholder="Noida"
                          className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Step 4: Team */}
          {step === 4 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold mb-2">Team Members</h2>
                <p className="text-slate-400">Add engineers and managers for each site</p>
              </div>

              {data.sites.map((site, siteIndex) => (
                <div key={siteIndex} className="bg-slate-900 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-medium text-lg">{site.name || `Site ${siteIndex + 1}`}</h3>
                    <button
                      onClick={() => addTeamMember(siteIndex)}
                      className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm transition-colors"
                    >
                      + Add Member
                    </button>
                  </div>

                  {site.team.length === 0 ? (
                    <p className="text-slate-500 text-center py-8">
                      No team members yet. Click "Add Member" to add engineers.
                    </p>
                  ) : (
                    <div className="space-y-3">
                      {site.team.map((member, memberIndex) => (
                        <div key={memberIndex} className="flex items-center gap-3 p-3 bg-slate-800 rounded-lg">
                          <div className="flex-1 grid grid-cols-3 gap-3">
                            <input
                              type="text"
                              value={member.name}
                              onChange={e => updateTeamMember(siteIndex, memberIndex, 'name', e.target.value)}
                              placeholder="Name"
                              className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                            <input
                              type="tel"
                              value={member.phone}
                              onChange={e => updateTeamMember(siteIndex, memberIndex, 'phone', e.target.value)}
                              placeholder="Phone"
                              className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                            <select
                              value={member.role}
                              onChange={e => updateTeamMember(siteIndex, memberIndex, 'role', e.target.value)}
                              className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                              {ROLES.map(role => (
                                <option key={role.value} value={role.value}>{role.label}</option>
                              ))}
                            </select>
                          </div>
                          <button
                            onClick={() => removeTeamMember(siteIndex, memberIndex)}
                            className="p-2 text-red-400 hover:text-red-300 hover:bg-red-400/10 rounded-lg"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Step 5: Settings */}
          {step === 5 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold mb-2">Customization</h2>
                <p className="text-slate-400">Configure preferences (all can be changed later)</p>
              </div>

              <div className="bg-slate-900 rounded-xl p-6 space-y-6">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-3">
                    Response Language
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {[
                      { value: 'en', label: 'English' },
                      { value: 'hi', label: 'Hindi' },
                      { value: 'hinglish', label: 'Hinglish', recommended: true },
                    ].map(lang => (
                      <button
                        key={lang.value}
                        onClick={() => updateData('language', lang.value)}
                        className={`p-3 rounded-lg border-2 text-center transition-colors relative ${
                          data.language === lang.value
                            ? 'border-blue-500 bg-blue-500/10'
                            : 'border-slate-700 hover:border-slate-600'
                        }`}
                      >
                        {lang.label}
                        {lang.recommended && (
                          <span className="absolute -top-2 -right-2 px-2 py-0.5 bg-green-500 text-xs rounded-full">
                            Recommended
                          </span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Assistant Name
                    </label>
                    <input
                      type="text"
                      value={data.assistantName}
                      onChange={e => updateData('assistantName', e.target.value)}
                      placeholder="SiteMind"
                      className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="text-xs text-slate-500 mt-1">What the AI calls itself</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Morning Brief Time
                    </label>
                    <input
                      type="time"
                      value={data.morningBriefTime}
                      onChange={e => updateData('morningBriefTime', e.target.value)}
                      className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="text-xs text-slate-500 mt-1">Daily summary sent at this time</p>
                  </div>
                </div>
              </div>

              {/* Summary */}
              <div className="bg-slate-800/50 rounded-xl p-6">
                <h3 className="font-medium mb-4">Summary</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-slate-400">Company:</span>
                    <span className="ml-2">{data.companyName}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Admin:</span>
                    <span className="ml-2">{data.adminName}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Sites:</span>
                    <span className="ml-2">{data.sites.length}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Team Members:</span>
                    <span className="ml-2">{data.sites.reduce((sum, s) => sum + s.team.length, 0)}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Plan:</span>
                    <span className="ml-2 capitalize">{data.plan}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Language:</span>
                    <span className="ml-2 capitalize">{data.language}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 6: Success */}
          {step === 6 && result && (
            <div className="space-y-6">
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h2 className="text-2xl font-bold mb-2">Setup Complete!</h2>
                <p className="text-slate-400">Customer is ready to use SiteMind</p>
              </div>

              <div className="bg-slate-900 rounded-xl p-6">
                <div className="grid grid-cols-3 gap-6 text-center">
                  <div>
                    <div className="text-3xl font-bold text-blue-400">{result.projects_created}</div>
                    <div className="text-sm text-slate-400">Sites Created</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-green-400">{result.users_added}</div>
                    <div className="text-sm text-slate-400">Users Added</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold text-purple-400">{result.welcome_messages.length}</div>
                    <div className="text-sm text-slate-400">Welcome Messages</div>
                  </div>
                </div>
              </div>

              <div className="bg-slate-900 rounded-xl p-6">
                <h3 className="font-medium mb-4">Welcome Messages to Send</h3>
                <div className="space-y-3">
                  {result.welcome_messages.map((msg: any, i: number) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-slate-800 rounded-lg">
                      <div>
                        <div className="font-medium">{msg.name}</div>
                        <div className="text-sm text-slate-400">{msg.phone} • {msg.role}</div>
                      </div>
                      <button className="px-3 py-1.5 bg-green-600 hover:bg-green-500 rounded-lg text-sm transition-colors">
                        Send via WhatsApp
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-6">
                <h3 className="font-medium text-amber-400 mb-3">📋 Next Steps</h3>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <input type="checkbox" className="rounded" />
                    <span>Send welcome messages (click buttons above)</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <input type="checkbox" className="rounded" />
                    <span>Ask customer to share drawings (Drive link or WhatsApp forward)</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <input type="checkbox" className="rounded" />
                    <span>Demo first query with customer</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <input type="checkbox" className="rounded" />
                    <span>Schedule Day 3 check-in</span>
                  </li>
                </ul>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setStep(1);
                    setData(INITIAL_DATA);
                    setResult(null);
                  }}
                  className="flex-1 px-6 py-3 bg-slate-700 hover:bg-slate-600 rounded-lg font-medium transition-colors"
                >
                  Onboard Another Customer
                </button>
                <button
                  onClick={() => window.location.href = '/admin/customers'}
                  className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-lg font-medium transition-colors"
                >
                  View All Customers
                </button>
              </div>
            </div>
          )}

          {/* Navigation */}
          {step <= 5 && (
            <div className="flex justify-between mt-8 pt-6 border-t border-slate-800">
              <button
                onClick={() => setStep(s => s - 1)}
                disabled={step === 1}
                className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                  step === 1
                    ? 'text-slate-600 cursor-not-allowed'
                    : 'bg-slate-700 hover:bg-slate-600'
                }`}
              >
                Back
              </button>

              {step < 5 ? (
                <button
                  onClick={() => setStep(s => s + 1)}
                  disabled={!canProceed()}
                  className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                    canProceed()
                      ? 'bg-blue-600 hover:bg-blue-500'
                      : 'bg-slate-700 text-slate-500 cursor-not-allowed'
                  }`}
                >
                  Continue
                </button>
              ) : (
                <button
                  onClick={handleSubmit}
                  disabled={isSubmitting}
                  className="px-8 py-3 bg-green-600 hover:bg-green-500 rounded-lg font-medium transition-colors flex items-center gap-2"
                >
                  {isSubmitting ? (
                    <>
                      <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      Creating...
                    </>
                  ) : (
                    <>
                      Create Customer
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </>
                  )}
                </button>
              )}
            </div>
          )}
        </main>
      </div>
    </>
  );
}

