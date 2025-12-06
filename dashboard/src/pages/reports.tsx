import Layout from '@/components/Layout'
import {
  FileText,
  Download,
  Calendar,
  Building2,
  TrendingUp,
  Clock,
  Mail,
  Plus,
} from 'lucide-react'

const reports = [
  {
    id: 1,
    title: 'Monthly Summary - November 2024',
    type: 'monthly',
    date: '2024-12-01',
    sites: 12,
    status: 'ready',
  },
  {
    id: 2,
    title: 'Weekly Report - Week 48',
    type: 'weekly',
    date: '2024-12-01',
    sites: 12,
    status: 'ready',
  },
  {
    id: 3,
    title: 'Site Report - Skyline Towers',
    type: 'site',
    date: '2024-11-30',
    sites: 1,
    status: 'ready',
  },
  {
    id: 4,
    title: 'ROI Analysis - Q3 2024',
    type: 'roi',
    date: '2024-10-01',
    sites: 12,
    status: 'ready',
  },
  {
    id: 5,
    title: 'Weekly Report - Week 47',
    type: 'weekly',
    date: '2024-11-24',
    sites: 12,
    status: 'ready',
  },
]

const scheduledReports = [
  {
    id: 1,
    title: 'Weekly Summary',
    frequency: 'Every Monday 8AM',
    recipients: ['management@abcdev.com'],
    nextRun: '2024-12-09',
  },
  {
    id: 2,
    title: 'Monthly ROI Report',
    frequency: 'First of month',
    recipients: ['cfo@abcdev.com', 'md@abcdev.com'],
    nextRun: '2025-01-01',
  },
]

const typeColors = {
  monthly: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  weekly: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  site: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  roi: 'bg-primary-500/10 text-primary-400 border-primary-500/20',
}

export default function ReportsPage() {
  return (
    <Layout companyName="ABC Developers">
      <div className="p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Reports</h1>
            <p className="text-slate-400">
              Automated reports for stakeholders
            </p>
          </div>
          <button className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Generate Report
          </button>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
            <div className="p-3 bg-blue-500/10 rounded-lg">
              <FileText className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">24</p>
              <p className="text-sm text-slate-400">Reports Generated</p>
            </div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
            <div className="p-3 bg-emerald-500/10 rounded-lg">
              <Clock className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">2</p>
              <p className="text-sm text-slate-400">Scheduled Reports</p>
            </div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
            <div className="p-3 bg-purple-500/10 rounded-lg">
              <Mail className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">156</p>
              <p className="text-sm text-slate-400">Emails Sent</p>
            </div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
            <div className="p-3 bg-primary-500/10 rounded-lg">
              <TrendingUp className="w-5 h-5 text-primary-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">₹28.4L</p>
              <p className="text-sm text-slate-400">Reported ROI</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recent Reports */}
          <div className="lg:col-span-2">
            <div className="bg-slate-900 border border-slate-800 rounded-xl">
              <div className="p-6 border-b border-slate-800 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">Recent Reports</h2>
                <select className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none">
                  <option>All Types</option>
                  <option>Monthly</option>
                  <option>Weekly</option>
                  <option>Site</option>
                  <option>ROI</option>
                </select>
              </div>
              <div className="divide-y divide-slate-800">
                {reports.map((report) => (
                  <div key={report.id} className="p-6 flex items-center justify-between hover:bg-slate-800/50 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="p-3 bg-slate-800 rounded-lg">
                        <FileText className="w-5 h-5 text-slate-400" />
                      </div>
                      <div>
                        <h3 className="font-medium text-white">{report.title}</h3>
                        <div className="flex items-center gap-3 mt-1">
                          <span className={`px-2 py-0.5 rounded text-xs font-medium border ${typeColors[report.type as keyof typeof typeColors]}`}>
                            {report.type}
                          </span>
                          <span className="text-sm text-slate-400 flex items-center gap-1">
                            <Calendar className="w-3.5 h-3.5" />
                            {new Date(report.date).toLocaleDateString('en-IN', { 
                              day: 'numeric', 
                              month: 'short', 
                              year: 'numeric' 
                            })}
                          </span>
                          <span className="text-sm text-slate-400 flex items-center gap-1">
                            <Building2 className="w-3.5 h-3.5" />
                            {report.sites} site{report.sites > 1 ? 's' : ''}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button className="px-3 py-1.5 text-sm text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors">
                        View
                      </button>
                      <button className="px-3 py-1.5 text-sm bg-primary-500/10 text-primary-400 hover:bg-primary-500/20 rounded-lg transition-colors flex items-center gap-1.5">
                        <Download className="w-4 h-4" />
                        PDF
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              <div className="p-4 border-t border-slate-800">
                <button className="text-sm text-primary-500 hover:text-primary-400 font-medium">
                  View all reports →
                </button>
              </div>
            </div>
          </div>

          {/* Scheduled Reports */}
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl">
              <div className="p-6 border-b border-slate-800 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">Scheduled</h2>
                <button className="text-sm text-primary-500 hover:text-primary-400">
                  + Add
                </button>
              </div>
              <div className="divide-y divide-slate-800">
                {scheduledReports.map((report) => (
                  <div key={report.id} className="p-4">
                    <h3 className="font-medium text-white">{report.title}</h3>
                    <p className="text-sm text-slate-400 mt-1">{report.frequency}</p>
                    <div className="mt-3 flex items-center gap-2 flex-wrap">
                      {report.recipients.map((email) => (
                        <span key={email} className="px-2 py-1 bg-slate-800 rounded text-xs text-slate-300">
                          {email}
                        </span>
                      ))}
                    </div>
                    <p className="text-xs text-slate-500 mt-2">
                      Next: {new Date(report.nextRun).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Generate */}
            <div className="bg-gradient-to-br from-primary-500/10 to-primary-600/5 border border-primary-500/20 rounded-xl p-6">
              <h3 className="font-semibold text-white mb-4">Quick Generate</h3>
              <div className="space-y-3">
                <button className="w-full px-4 py-3 bg-slate-900/50 hover:bg-slate-900 border border-slate-700 rounded-lg text-left transition-colors">
                  <p className="font-medium text-white">Weekly Summary</p>
                  <p className="text-xs text-slate-400">All sites, this week</p>
                </button>
                <button className="w-full px-4 py-3 bg-slate-900/50 hover:bg-slate-900 border border-slate-700 rounded-lg text-left transition-colors">
                  <p className="font-medium text-white">ROI Report</p>
                  <p className="text-xs text-slate-400">Value delivered breakdown</p>
                </button>
                <button className="w-full px-4 py-3 bg-slate-900/50 hover:bg-slate-900 border border-slate-700 rounded-lg text-left transition-colors">
                  <p className="font-medium text-white">Audit Export</p>
                  <p className="text-xs text-slate-400">All decisions & citations</p>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

