import { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { useRouter } from 'next/router';

// Mock customer data
const MOCK_CUSTOMER = {
  id: 'org_abc123',
  name: 'ABC Builders Pvt Ltd',
  plan: 'pilot',
};

// Default config structure
const DEFAULT_CONFIG = {
  // General
  language: 'hinglish',
  timezone: 'Asia/Kolkata',
  
  // Branding
  assistant_name: 'SiteMind',
  
  // Features
  features: {
    red_flags: true,
    task_management: true,
    material_tracking: true,
    progress_photos: true,
    office_site_sync: true,
    integrations: false,
    advanced_analytics: false,
    custom_reports: false,
    api_access: false,
  },
  
  // Notifications
  notifications: {
    morning_brief_enabled: true,
    morning_brief_time: '07:00',
    red_flag_alerts: true,
    weekly_reports: true,
    daily_summary: false,
  },
  
  // AI Behavior
  ai_config: {
    response_style: 'professional',
    safety_emphasis: 'high',
    include_citations: true,
    response_length: 'medium',
  },
};

export default function CustomerConfigPage() {
  const router = useRouter();
  const { id } = router.query;
  
  const [config, setConfig] = useState(DEFAULT_CONFIG);
  const [activeTab, setActiveTab] = useState('general');
  const [isSaving, setIsSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const updateConfig = (path: string, value: any) => {
    setConfig(prev => {
      const keys = path.split('.');
      const newConfig = { ...prev };
      let current: any = newConfig;
      
      for (let i = 0; i < keys.length - 1; i++) {
        current[keys[i]] = { ...current[keys[i]] };
        current = current[keys[i]];
      }
      
      current[keys[keys.length - 1]] = value;
      return newConfig;
    });
    setSaved(false);
  };

  const handleSave = async () => {
    setIsSaving(true);
    // In production, call API
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const tabs = [
    { id: 'general', label: 'General', icon: '⚙️' },
    { id: 'features', label: 'Features', icon: '🎛️' },
    { id: 'notifications', label: 'Notifications', icon: '🔔' },
    { id: 'ai', label: 'AI Behavior', icon: '🤖' },
  ];

  return (
    <>
      <Head>
        <title>Config - {MOCK_CUSTOMER.name} | SiteMind Admin</title>
      </Head>

      <div className="min-h-screen bg-slate-950 text-white">
        {/* Header */}
        <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur sticky top-0 z-10">
          <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/admin/customers" className="text-slate-400 hover:text-white">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </Link>
              <div>
                <h1 className="font-semibold">{MOCK_CUSTOMER.name}</h1>
                <p className="text-sm text-slate-400">Configuration Settings</p>
              </div>
            </div>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 ${
                saved 
                  ? 'bg-green-600' 
                  : 'bg-blue-600 hover:bg-blue-500'
              }`}
            >
              {isSaving ? (
                <>
                  <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Saving...
                </>
              ) : saved ? (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Saved!
                </>
              ) : (
                'Save Changes'
              )}
            </button>
          </div>
        </header>

        <main className="max-w-5xl mx-auto px-6 py-8">
          <div className="flex gap-8">
            {/* Sidebar */}
            <div className="w-48 shrink-0">
              <nav className="space-y-1">
                {tabs.map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full text-left px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
                      activeTab === tab.id
                        ? 'bg-blue-600 text-white'
                        : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                    }`}
                  >
                    <span>{tab.icon}</span>
                    <span>{tab.label}</span>
                  </button>
                ))}
              </nav>
            </div>

            {/* Content */}
            <div className="flex-1 space-y-6">
              {/* General Tab */}
              {activeTab === 'general' && (
                <>
                  <div className="bg-slate-900 rounded-xl p-6">
                    <h3 className="font-semibold mb-4">Language & Region</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm text-slate-400 mb-2">Response Language</label>
                        <select
                          value={config.language}
                          onChange={e => updateConfig('language', e.target.value)}
                          className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg"
                        >
                          <option value="en">English</option>
                          <option value="hi">Hindi</option>
                          <option value="hinglish">Hinglish (Recommended)</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm text-slate-400 mb-2">Timezone</label>
                        <select
                          value={config.timezone}
                          onChange={e => updateConfig('timezone', e.target.value)}
                          className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg"
                        >
                          <option value="Asia/Kolkata">India (IST)</option>
                          <option value="Asia/Dubai">Dubai (GST)</option>
                          <option value="Asia/Singapore">Singapore (SGT)</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  <div className="bg-slate-900 rounded-xl p-6">
                    <h3 className="font-semibold mb-4">Branding</h3>
                    <div>
                      <label className="block text-sm text-slate-400 mb-2">Assistant Name</label>
                      <input
                        type="text"
                        value={config.assistant_name}
                        onChange={e => updateConfig('assistant_name', e.target.value)}
                        className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg"
                        placeholder="SiteMind"
                      />
                      <p className="text-xs text-slate-500 mt-1">What the AI calls itself in responses</p>
                    </div>
                  </div>
                </>
              )}

              {/* Features Tab */}
              {activeTab === 'features' && (
                <div className="bg-slate-900 rounded-xl p-6">
                  <h3 className="font-semibold mb-4">Feature Toggles</h3>
                  <div className="space-y-4">
                    {Object.entries(config.features).map(([key, enabled]) => (
                      <div key={key} className="flex items-center justify-between py-2">
                        <div>
                          <div className="font-medium capitalize">{key.replace(/_/g, ' ')}</div>
                          <div className="text-sm text-slate-500">
                            {key === 'red_flags' && 'Proactive risk detection'}
                            {key === 'task_management' && 'Task tracking via WhatsApp'}
                            {key === 'material_tracking' && 'Inventory management'}
                            {key === 'progress_photos' && 'Photo-based progress tracking'}
                            {key === 'office_site_sync' && 'Office-site communication'}
                            {key === 'integrations' && 'External system connections'}
                            {key === 'advanced_analytics' && 'Detailed usage analytics'}
                            {key === 'custom_reports' && 'Custom report templates'}
                            {key === 'api_access' && 'Direct API access'}
                          </div>
                        </div>
                        <button
                          onClick={() => updateConfig(`features.${key}`, !enabled)}
                          className={`w-12 h-6 rounded-full transition-colors ${
                            enabled ? 'bg-blue-600' : 'bg-slate-700'
                          }`}
                        >
                          <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${
                            enabled ? 'translate-x-6' : 'translate-x-0.5'
                          }`} />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Notifications Tab */}
              {activeTab === 'notifications' && (
                <div className="space-y-6">
                  <div className="bg-slate-900 rounded-xl p-6">
                    <h3 className="font-semibold mb-4">Morning Brief</h3>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium">Enable Morning Brief</div>
                          <div className="text-sm text-slate-500">Daily summary sent to PM & Owner</div>
                        </div>
                        <button
                          onClick={() => updateConfig('notifications.morning_brief_enabled', !config.notifications.morning_brief_enabled)}
                          className={`w-12 h-6 rounded-full transition-colors ${
                            config.notifications.morning_brief_enabled ? 'bg-blue-600' : 'bg-slate-700'
                          }`}
                        >
                          <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${
                            config.notifications.morning_brief_enabled ? 'translate-x-6' : 'translate-x-0.5'
                          }`} />
                        </button>
                      </div>
                      {config.notifications.morning_brief_enabled && (
                        <div>
                          <label className="block text-sm text-slate-400 mb-2">Send Time</label>
                          <input
                            type="time"
                            value={config.notifications.morning_brief_time}
                            onChange={e => updateConfig('notifications.morning_brief_time', e.target.value)}
                            className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg"
                          />
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="bg-slate-900 rounded-xl p-6">
                    <h3 className="font-semibold mb-4">Other Notifications</h3>
                    <div className="space-y-4">
                      {[
                        { key: 'red_flag_alerts', label: 'Red Flag Alerts', desc: 'Immediate alerts for risks' },
                        { key: 'weekly_reports', label: 'Weekly Reports', desc: 'Weekly summary emails' },
                        { key: 'daily_summary', label: 'Daily Summary', desc: 'End of day activity summary' },
                      ].map(item => (
                        <div key={item.key} className="flex items-center justify-between py-2">
                          <div>
                            <div className="font-medium">{item.label}</div>
                            <div className="text-sm text-slate-500">{item.desc}</div>
                          </div>
                          <button
                            onClick={() => updateConfig(`notifications.${item.key}`, !(config.notifications as any)[item.key])}
                            className={`w-12 h-6 rounded-full transition-colors ${
                              (config.notifications as any)[item.key] ? 'bg-blue-600' : 'bg-slate-700'
                            }`}
                          >
                            <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${
                              (config.notifications as any)[item.key] ? 'translate-x-6' : 'translate-x-0.5'
                            }`} />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* AI Tab */}
              {activeTab === 'ai' && (
                <div className="bg-slate-900 rounded-xl p-6">
                  <h3 className="font-semibold mb-4">AI Behavior</h3>
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm text-slate-400 mb-2">Response Style</label>
                      <select
                        value={config.ai_config.response_style}
                        onChange={e => updateConfig('ai_config.response_style', e.target.value)}
                        className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg"
                      >
                        <option value="professional">Professional</option>
                        <option value="friendly">Friendly</option>
                        <option value="brief">Brief</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm text-slate-400 mb-2">Safety Emphasis</label>
                      <select
                        value={config.ai_config.safety_emphasis}
                        onChange={e => updateConfig('ai_config.safety_emphasis', e.target.value)}
                        className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg"
                      >
                        <option value="high">High - Always emphasize safety</option>
                        <option value="medium">Medium - Mention when relevant</option>
                        <option value="low">Low - Only when critical</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm text-slate-400 mb-2">Response Length</label>
                      <select
                        value={config.ai_config.response_length}
                        onChange={e => updateConfig('ai_config.response_length', e.target.value)}
                        className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg"
                      >
                        <option value="brief">Brief - Just the answer</option>
                        <option value="medium">Medium - Answer + context</option>
                        <option value="detailed">Detailed - Full explanation</option>
                      </select>
                    </div>

                    <div className="flex items-center justify-between py-2">
                      <div>
                        <div className="font-medium">Include Citations</div>
                        <div className="text-sm text-slate-500">Reference drawings in responses</div>
                      </div>
                      <button
                        onClick={() => updateConfig('ai_config.include_citations', !config.ai_config.include_citations)}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          config.ai_config.include_citations ? 'bg-blue-600' : 'bg-slate-700'
                        }`}
                      >
                        <div className={`w-5 h-5 rounded-full bg-white transform transition-transform ${
                          config.ai_config.include_citations ? 'translate-x-6' : 'translate-x-0.5'
                        }`} />
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </main>
      </div>
    </>
  );
}

