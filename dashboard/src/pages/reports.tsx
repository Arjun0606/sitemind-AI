import { useState } from 'react'
import Layout from '@/components/Layout'
import {
  BarChart3,
  Download,
  Calendar,
  FileText,
  AlertTriangle,
  TrendingUp,
  Clock,
  Users,
  CheckCircle,
} from 'lucide-react'

const mockReport = {
  period: 'Week of Dec 9-15, 2024',
  summary: 'Overall project health is GOOD. 3 RFIs resolved, 2 new issues reported. No critical delays.',
  stats: {
    rfis_opened: 5,
    rfis_closed: 3,
    decisions_made: 12,
    issues_reported: 2,
    issues_resolved: 4,
    drawings_uploaded: 8,
  },
  risks: [
    { severity: 'medium', description: 'Tile delivery delayed by 2 days', mitigation: 'Expedite with supplier' },
    { severity: 'low', description: 'Labour shortage expected next week', mitigation: 'Coordinate with contractor' },
  ],
  contractors: [
    { name: 'ABC Electrical', score: 85, trend: 'up' },
    { name: 'XYZ Plumbing', score: 72, trend: 'stable' },
    { name: 'PQR Civil', score: 68, trend: 'down' },
  ],
}

export default function ReportsPage() {
  const [selectedProject, setSelectedProject] = useState('all')
  const [reportType, setReportType] = useState('weekly')

  return (
    <Layout companyName="ABC Developers">
      <div className="p-6 lg:p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white mb-2">Reports</h1>
            <p className="text-slate-400">
              Generate and download project reports
            </p>
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors">
            <Download className="w-5 h-5" />
            Download PDF
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-4 mb-8">
          <select 
            value={selectedProject}
            onChange={(e) => setSelectedProject(e.target.value)}
            className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-primary-500"
          >
            <option value="all">All Projects</option>
            <option value="1">Skyline Towers</option>
            <option value="2">Green Valley</option>
            <option value="3">Phoenix Mall</option>
          </select>

          <select 
            value={reportType}
            onChange={(e) => setReportType(e.target.value)}
            className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-white focus:outline-none focus:border-primary-500"
          >
            <option value="weekly">Weekly Report</option>
            <option value="monthly">Monthly Report</option>
          </select>
        </div>

        {/* Report Content */}
        <div className="space-y-6">
          {/* Header Card */}
          <div className="bg-gradient-to-r from-primary-500/20 to-transparent border border-primary-500/30 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-primary-500/20 flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-primary-400" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">Project Health Report</h2>
                <p className="text-primary-400">{mockReport.period}</p>
              </div>
            </div>
            <p className="text-slate-300">{mockReport.summary}</p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 lg:grid-cols-6 gap-4">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-orange-400">{mockReport.stats.rfis_opened}</p>
              <p className="text-slate-400 text-sm">RFIs Opened</p>
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-green-400">{mockReport.stats.rfis_closed}</p>
              <p className="text-slate-400 text-sm">RFIs Closed</p>
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-blue-400">{mockReport.stats.decisions_made}</p>
              <p className="text-slate-400 text-sm">Decisions</p>
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-red-400">{mockReport.stats.issues_reported}</p>
              <p className="text-slate-400 text-sm">Issues Reported</p>
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-green-400">{mockReport.stats.issues_resolved}</p>
              <p className="text-slate-400 text-sm">Issues Resolved</p>
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 text-center">
              <p className="text-2xl font-bold text-purple-400">{mockReport.stats.drawings_uploaded}</p>
              <p className="text-slate-400 text-sm">Drawings</p>
            </div>
          </div>

          {/* Two Column Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Risks */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-orange-400" />
                Active Risks
              </h3>
              
              {mockReport.risks.length === 0 ? (
                <p className="text-slate-400">No active risks</p>
              ) : (
                <div className="space-y-4">
                  {mockReport.risks.map((risk, i) => (
                    <div key={i} className="p-4 bg-slate-800/50 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`px-2 py-0.5 text-xs font-medium rounded ${
                          risk.severity === 'high' ? 'bg-red-500/20 text-red-400' :
                          risk.severity === 'medium' ? 'bg-orange-500/20 text-orange-400' :
                          'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {risk.severity.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-white mb-1">{risk.description}</p>
                      <p className="text-slate-400 text-sm">→ {risk.mitigation}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Contractor Performance */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                <Users className="w-5 h-5 text-blue-400" />
                Contractor Performance
              </h3>
              
              <div className="space-y-4">
                {mockReport.contractors.map((contractor, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center">
                        <span className="text-slate-400 text-sm font-medium">
                          {contractor.name.split(' ').map(n => n[0]).join('')}
                        </span>
                      </div>
                      <div>
                        <p className="text-white">{contractor.name}</p>
                        <div className="flex items-center gap-1">
                          {contractor.trend === 'up' && <TrendingUp className="w-3 h-3 text-green-400" />}
                          {contractor.trend === 'down' && <TrendingUp className="w-3 h-3 text-red-400 rotate-180" />}
                          {contractor.trend === 'stable' && <span className="w-3 h-3 text-slate-400">−</span>}
                          <span className="text-slate-400 text-xs capitalize">{contractor.trend}</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`text-lg font-bold ${
                        contractor.score >= 80 ? 'text-green-400' :
                        contractor.score >= 60 ? 'text-orange-400' :
                        'text-red-400'
                      }`}>
                        {contractor.score}
                      </p>
                      <p className="text-slate-500 text-xs">Score</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Quick Generate */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="flex items-center gap-3 p-4 bg-slate-900 border border-slate-800 rounded-xl hover:border-slate-700 transition-colors">
              <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <FileText className="w-5 h-5 text-blue-400" />
              </div>
              <div className="text-left">
                <p className="text-white font-medium">RFI Report</p>
                <p className="text-slate-400 text-sm">All RFIs and status</p>
              </div>
            </button>

            <button className="flex items-center gap-3 p-4 bg-slate-900 border border-slate-800 rounded-xl hover:border-slate-700 transition-colors">
              <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-green-400" />
              </div>
              <div className="text-left">
                <p className="text-white font-medium">Decision Log</p>
                <p className="text-slate-400 text-sm">All decisions with audit</p>
              </div>
            </button>

            <button className="flex items-center gap-3 p-4 bg-slate-900 border border-slate-800 rounded-xl hover:border-slate-700 transition-colors">
              <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                <Clock className="w-5 h-5 text-purple-400" />
              </div>
              <div className="text-left">
                <p className="text-white font-medium">Activity Log</p>
                <p className="text-slate-400 text-sm">Who did what, when</p>
              </div>
            </button>
          </div>
        </div>
      </div>
    </Layout>
  )
}
