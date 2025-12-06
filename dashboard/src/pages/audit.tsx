import Layout from '@/components/Layout'
import {
  Shield,
  Search,
  Filter,
  Download,
  Calendar,
  User,
  Building2,
  FileText,
  MessageSquare,
  AlertTriangle,
  CheckCircle,
  Clock,
} from 'lucide-react'

const auditEntries = [
  {
    id: 1,
    type: 'change_order',
    title: 'Column spacing changed from 4.5m to 5.0m',
    description: 'Architect approved change due to parking requirements',
    site: 'Skyline Towers',
    user: 'Rajesh Kumar',
    timestamp: '2024-12-06T10:30:00',
    reference: 'CO-2024-089',
    previousValue: '4.5m',
    newValue: '5.0m',
    approvedBy: 'Ar. Sharma',
    status: 'approved',
  },
  {
    id: 2,
    type: 'rfi',
    title: 'RFI #45: Beam depth at grid B2-B3',
    description: 'Clarification on structural drawing SK-003',
    site: 'Skyline Towers',
    user: 'Vijay Sharma',
    timestamp: '2024-12-06T09:15:00',
    reference: 'RFI-2024-045',
    status: 'resolved',
  },
  {
    id: 3,
    type: 'blueprint_update',
    title: 'Blueprint revision uploaded',
    description: 'Updated structural drawings for Block A foundation',
    site: 'Green Valley',
    user: 'Admin',
    timestamp: '2024-12-05T16:45:00',
    reference: 'REV-003',
    previousValue: 'v2.1',
    newValue: 'v2.2',
    status: 'active',
  },
  {
    id: 4,
    type: 'decision',
    title: 'Material substitution approved',
    description: 'TMT 500D substituted for 550D due to supply constraints',
    site: 'Phoenix Mall',
    user: 'Site PM',
    timestamp: '2024-12-05T14:20:00',
    reference: 'DEC-2024-023',
    previousValue: 'Fe550D',
    newValue: 'Fe500D',
    approvedBy: 'Structural Consultant',
    status: 'approved',
  },
  {
    id: 5,
    type: 'query',
    title: 'Critical spec query answered',
    description: 'Rebar specifications for cantilever section',
    site: 'Marina Bay',
    user: 'Arun Singh',
    timestamp: '2024-12-05T11:30:00',
    reference: 'Q-12847',
    status: 'resolved',
  },
]

const typeIcons = {
  change_order: AlertTriangle,
  rfi: MessageSquare,
  blueprint_update: FileText,
  decision: CheckCircle,
  query: MessageSquare,
}

const typeColors = {
  change_order: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  rfi: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  blueprint_update: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  decision: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  query: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
}

export default function AuditPage() {
  return (
    <Layout companyName="ABC Developers">
      <div className="p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Audit Trail</h1>
            <p className="text-slate-400">
              Complete history of decisions, changes, and communications
            </p>
          </div>
          <button className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export All
          </button>
        </div>

        {/* Filters */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 mb-6">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex-1 min-w-[200px] relative">
              <Search className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search audit trail..."
                className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-white placeholder-slate-400 focus:outline-none focus:border-primary-500"
              />
            </div>
            <select className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary-500">
              <option>All Sites</option>
              <option>Skyline Towers</option>
              <option>Green Valley</option>
              <option>Phoenix Mall</option>
              <option>Marina Bay</option>
            </select>
            <select className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary-500">
              <option>All Types</option>
              <option>Change Orders</option>
              <option>RFIs</option>
              <option>Blueprint Updates</option>
              <option>Decisions</option>
              <option>Queries</option>
            </select>
            <select className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary-500">
              <option>Last 30 days</option>
              <option>Last 7 days</option>
              <option>Last 90 days</option>
              <option>All time</option>
            </select>
            <button className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-300 hover:bg-slate-700 transition-colors flex items-center gap-2">
              <Filter className="w-4 h-4" />
              More Filters
            </button>
          </div>
        </div>

        {/* Audit List */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl">
          <div className="divide-y divide-slate-800">
            {auditEntries.map((entry) => {
              const Icon = typeIcons[entry.type as keyof typeof typeIcons]
              const colorClass = typeColors[entry.type as keyof typeof typeColors]
              
              return (
                <div key={entry.id} className="p-6 hover:bg-slate-800/50 transition-colors">
                  <div className="flex items-start gap-4">
                    <div className={`p-3 rounded-lg border ${colorClass}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h3 className="font-medium text-white">{entry.title}</h3>
                          <p className="text-sm text-slate-400 mt-1">{entry.description}</p>
                        </div>
                        <span className={`px-2 py-1 rounded text-xs font-medium border ${
                          entry.status === 'approved' 
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                            : entry.status === 'resolved'
                            ? 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                            : 'bg-slate-500/10 text-slate-400 border-slate-500/20'
                        }`}>
                          {entry.status}
                        </span>
                      </div>
                      
                      {/* Metadata */}
                      <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm text-slate-400 mt-3">
                        <span className="flex items-center gap-1">
                          <Building2 className="w-3.5 h-3.5" />
                          {entry.site}
                        </span>
                        <span className="flex items-center gap-1">
                          <User className="w-3.5 h-3.5" />
                          {entry.user}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3.5 h-3.5" />
                          {new Date(entry.timestamp).toLocaleString('en-IN', {
                            day: 'numeric',
                            month: 'short',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </span>
                        <span className="flex items-center gap-1">
                          <FileText className="w-3.5 h-3.5" />
                          {entry.reference}
                        </span>
                      </div>
                      
                      {/* Change details */}
                      {entry.previousValue && (
                        <div className="mt-3 p-3 bg-slate-800/50 rounded-lg">
                          <div className="flex items-center gap-4 text-sm">
                            <span className="text-slate-400">Changed:</span>
                            <span className="text-red-400 line-through">{entry.previousValue}</span>
                            <span className="text-slate-400">→</span>
                            <span className="text-emerald-400">{entry.newValue}</span>
                            {entry.approvedBy && (
                              <>
                                <span className="text-slate-400 ml-2">Approved by:</span>
                                <span className="text-white">{entry.approvedBy}</span>
                              </>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
          
          {/* Pagination */}
          <div className="p-4 border-t border-slate-800 flex items-center justify-between">
            <p className="text-sm text-slate-400">Showing 1-5 of 1,234 entries</p>
            <div className="flex items-center gap-2">
              <button className="px-3 py-1.5 bg-slate-800 border border-slate-700 rounded text-sm text-slate-400 hover:text-white transition-colors">
                Previous
              </button>
              <button className="px-3 py-1.5 bg-primary-500 text-white rounded text-sm">
                1
              </button>
              <button className="px-3 py-1.5 bg-slate-800 border border-slate-700 rounded text-sm text-slate-400 hover:text-white transition-colors">
                2
              </button>
              <button className="px-3 py-1.5 bg-slate-800 border border-slate-700 rounded text-sm text-slate-400 hover:text-white transition-colors">
                3
              </button>
              <button className="px-3 py-1.5 bg-slate-800 border border-slate-700 rounded text-sm text-slate-400 hover:text-white transition-colors">
                Next
              </button>
            </div>
          </div>
        </div>

        {/* Export Options */}
        <div className="mt-6 bg-gradient-to-br from-slate-800/50 to-slate-900/50 border border-slate-700 rounded-xl p-6">
          <h3 className="font-semibold text-white mb-4">Export Options</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="p-4 bg-slate-900 border border-slate-700 rounded-lg hover:border-primary-500/50 transition-colors text-left">
              <FileText className="w-5 h-5 text-primary-400 mb-2" />
              <p className="font-medium text-white">PDF Report</p>
              <p className="text-sm text-slate-400">Formatted audit trail</p>
            </button>
            <button className="p-4 bg-slate-900 border border-slate-700 rounded-lg hover:border-primary-500/50 transition-colors text-left">
              <FileText className="w-5 h-5 text-emerald-400 mb-2" />
              <p className="font-medium text-white">Excel/CSV</p>
              <p className="text-sm text-slate-400">Raw data export</p>
            </button>
            <button className="p-4 bg-slate-900 border border-slate-700 rounded-lg hover:border-primary-500/50 transition-colors text-left">
              <Shield className="w-5 h-5 text-blue-400 mb-2" />
              <p className="font-medium text-white">Legal Package</p>
              <p className="text-sm text-slate-400">With citations & timestamps</p>
            </button>
          </div>
        </div>
      </div>
    </Layout>
  )
}

