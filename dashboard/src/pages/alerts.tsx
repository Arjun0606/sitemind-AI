import Layout from '@/components/Layout'
import {
  AlertTriangle,
  CheckCircle,
  XCircle,
  Eye,
  Camera,
  FileText,
  Clock,
  IndianRupee,
  Filter,
  Download,
  ChevronDown,
} from 'lucide-react'
import { useState } from 'react'

// Types
interface MismatchAlert {
  id: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  description: string
  project: string
  projectId: string
  detectedValue: string
  expectedValue: string
  sourceDocument: string
  costImpact: number // in lakhs
  photoUrl?: string
  createdAt: string
  status: 'open' | 'resolved' | 'false_alarm'
  resolvedBy?: string
  resolvedAt?: string
}

// Mock data
const mockAlerts: MismatchAlert[] = [
  {
    id: 'ALT-001',
    severity: 'critical',
    description: 'Rebar diameter mismatch at Column C2, Floor 3',
    project: 'Skyline Towers Block A',
    projectId: 'proj-1',
    detectedValue: '10mm rebar @ 200mm c/c',
    expectedValue: '12mm rebar @ 150mm c/c',
    sourceDocument: 'Drawing STR-07, Page 3',
    costImpact: 4.5,
    createdAt: '2 hours ago',
    status: 'open',
  },
  {
    id: 'ALT-002',
    severity: 'high',
    description: 'Column dimension appears undersized at Grid B2',
    project: 'Skyline Towers Block A',
    projectId: 'proj-1',
    detectedValue: '~400mm x 400mm',
    expectedValue: '450mm x 450mm',
    sourceDocument: 'Drawing STR-03',
    costImpact: 2.8,
    createdAt: '5 hours ago',
    status: 'resolved',
    resolvedBy: 'Rajesh Kumar',
    resolvedAt: '3 hours ago',
  },
  {
    id: 'ALT-003',
    severity: 'medium',
    description: 'Cover block spacing appears inconsistent',
    project: 'Phoenix Mall Extension',
    projectId: 'proj-3',
    detectedValue: 'Cover ~30mm in some areas',
    expectedValue: '40mm minimum as per IS 456',
    sourceDocument: 'IS 456:2000',
    costImpact: 1.2,
    createdAt: '1 day ago',
    status: 'open',
  },
  {
    id: 'ALT-004',
    severity: 'high',
    description: 'Stirrup spacing wider than specification',
    project: 'Green Valley Residency',
    projectId: 'proj-2',
    detectedValue: '~200mm c/c',
    expectedValue: '150mm c/c near supports',
    sourceDocument: 'Drawing STR-12',
    costImpact: 3.2,
    createdAt: '2 days ago',
    status: 'false_alarm',
    resolvedBy: 'System',
    resolvedAt: '2 days ago',
  },
  {
    id: 'ALT-005',
    severity: 'low',
    description: 'Minor crack observed in curing concrete',
    project: 'Phoenix Mall Extension',
    projectId: 'proj-3',
    detectedValue: 'Hairline crack ~0.2mm width',
    expectedValue: 'No visible cracks expected',
    sourceDocument: 'Quality Standards',
    costImpact: 0.5,
    createdAt: '3 days ago',
    status: 'open',
  },
]

const severityConfig = {
  critical: {
    color: 'red',
    bgClass: 'bg-red-500/10',
    textClass: 'text-red-400',
    borderClass: 'border-red-500/20',
    label: 'CRITICAL',
  },
  high: {
    color: 'orange',
    bgClass: 'bg-orange-500/10',
    textClass: 'text-orange-400',
    borderClass: 'border-orange-500/20',
    label: 'HIGH',
  },
  medium: {
    color: 'yellow',
    bgClass: 'bg-yellow-500/10',
    textClass: 'text-yellow-400',
    borderClass: 'border-yellow-500/20',
    label: 'MEDIUM',
  },
  low: {
    color: 'blue',
    bgClass: 'bg-blue-500/10',
    textClass: 'text-blue-400',
    borderClass: 'border-blue-500/20',
    label: 'LOW',
  },
}

const statusConfig = {
  open: {
    bgClass: 'bg-red-500/10',
    textClass: 'text-red-400',
    borderClass: 'border-red-500/20',
    label: 'Open',
    icon: AlertTriangle,
  },
  resolved: {
    bgClass: 'bg-emerald-500/10',
    textClass: 'text-emerald-400',
    borderClass: 'border-emerald-500/20',
    label: 'Resolved',
    icon: CheckCircle,
  },
  false_alarm: {
    bgClass: 'bg-slate-500/10',
    textClass: 'text-slate-400',
    borderClass: 'border-slate-500/20',
    label: 'False Alarm',
    icon: XCircle,
  },
}

export default function AlertsPage() {
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [filterSeverity, setFilterSeverity] = useState<string>('all')
  const [selectedAlert, setSelectedAlert] = useState<MismatchAlert | null>(null)
  
  // Filter alerts
  const filteredAlerts = mockAlerts.filter(alert => {
    if (filterStatus !== 'all' && alert.status !== filterStatus) return false
    if (filterSeverity !== 'all' && alert.severity !== filterSeverity) return false
    return true
  })
  
  // Stats
  const openAlerts = mockAlerts.filter(a => a.status === 'open').length
  const totalValueAtRisk = mockAlerts
    .filter(a => a.status === 'open')
    .reduce((sum, a) => sum + a.costImpact, 0)
  const resolvedThisMonth = mockAlerts.filter(a => a.status === 'resolved').length
  const totalValueSaved = mockAlerts
    .filter(a => a.status === 'resolved')
    .reduce((sum, a) => sum + a.costImpact, 0)

  return (
    <Layout companyName="ABC Developers">
      <div className="p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Mismatch Alerts</h1>
          <p className="text-slate-400">
            Connected Intelligence catching expensive mistakes before they happen.
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-slate-900 border border-red-500/20 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-2">
              <AlertTriangle className="w-5 h-5 text-red-400" />
              <span className="text-slate-400">Open Alerts</span>
            </div>
            <p className="text-3xl font-bold text-white">{openAlerts}</p>
            <p className="text-sm text-red-400 mt-1">Requires attention</p>
          </div>
          
          <div className="bg-slate-900 border border-orange-500/20 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-2">
              <IndianRupee className="w-5 h-5 text-orange-400" />
              <span className="text-slate-400">Value at Risk</span>
            </div>
            <p className="text-3xl font-bold text-white">₹{totalValueAtRisk.toFixed(1)}L</p>
            <p className="text-sm text-orange-400 mt-1">If not addressed</p>
          </div>
          
          <div className="bg-slate-900 border border-emerald-500/20 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-2">
              <CheckCircle className="w-5 h-5 text-emerald-400" />
              <span className="text-slate-400">Resolved This Month</span>
            </div>
            <p className="text-3xl font-bold text-white">{resolvedThisMonth}</p>
            <p className="text-sm text-emerald-400 mt-1">Mismatches fixed</p>
          </div>
          
          <div className="bg-slate-900 border border-emerald-500/20 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-2">
              <IndianRupee className="w-5 h-5 text-emerald-400" />
              <span className="text-slate-400">Value Saved</span>
            </div>
            <p className="text-3xl font-bold text-emerald-400">₹{totalValueSaved.toFixed(1)}L</p>
            <p className="text-sm text-slate-400 mt-1">By catching early</p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4 mb-6">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <span className="text-sm text-slate-400">Filter:</span>
          </div>
          
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
          >
            <option value="all">All Status</option>
            <option value="open">Open</option>
            <option value="resolved">Resolved</option>
            <option value="false_alarm">False Alarm</option>
          </select>
          
          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white"
          >
            <option value="all">All Severity</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          
          <div className="flex-1" />
          
          <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export Report
          </button>
        </div>

        {/* Alerts Table */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Alert</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Project</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Detected vs Expected</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Cost Impact</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Status</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredAlerts.map((alert) => {
                const severity = severityConfig[alert.severity]
                const status = statusConfig[alert.status]
                const StatusIcon = status.icon
                
                return (
                  <tr key={alert.id} className="border-b border-slate-800 hover:bg-slate-800/50">
                    <td className="px-6 py-4">
                      <div className="flex items-start gap-3">
                        <div className={`w-10 h-10 rounded-lg ${severity.bgClass} flex items-center justify-center flex-shrink-0`}>
                          <AlertTriangle className={`w-5 h-5 ${severity.textClass}`} />
                        </div>
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <span className={`px-2 py-0.5 text-xs font-medium rounded ${severity.bgClass} ${severity.textClass}`}>
                              {severity.label}
                            </span>
                            <span className="text-xs text-slate-500">{alert.id}</span>
                          </div>
                          <p className="text-white font-medium">{alert.description}</p>
                          <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {alert.createdAt}
                          </p>
                        </div>
                      </div>
                    </td>
                    
                    <td className="px-6 py-4">
                      <p className="text-white">{alert.project}</p>
                      <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
                        <FileText className="w-3 h-3" />
                        {alert.sourceDocument}
                      </p>
                    </td>
                    
                    <td className="px-6 py-4">
                      <div className="space-y-1">
                        <p className="text-red-400 text-sm">
                          <span className="text-slate-500">Found:</span> {alert.detectedValue}
                        </p>
                        <p className="text-emerald-400 text-sm">
                          <span className="text-slate-500">Expected:</span> {alert.expectedValue}
                        </p>
                      </div>
                    </td>
                    
                    <td className="px-6 py-4">
                      <p className={`text-lg font-bold ${alert.status === 'open' ? 'text-red-400' : 'text-emerald-400'}`}>
                        ₹{alert.costImpact}L
                      </p>
                      <p className="text-xs text-slate-500">
                        {alert.status === 'open' ? 'At risk' : 'Saved'}
                      </p>
                    </td>
                    
                    <td className="px-6 py-4">
                      <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full ${status.bgClass} ${status.textClass} border ${status.borderClass}`}>
                        <StatusIcon className="w-3.5 h-3.5" />
                        <span className="text-xs font-medium">{status.label}</span>
                      </div>
                      {alert.resolvedBy && (
                        <p className="text-xs text-slate-500 mt-1">
                          by {alert.resolvedBy}
                        </p>
                      )}
                    </td>
                    
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <button 
                          onClick={() => setSelectedAlert(alert)}
                          className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
                        >
                          <Eye className="w-4 h-4 text-slate-400" />
                        </button>
                        {alert.status === 'open' && (
                          <>
                            <button className="px-3 py-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 rounded-lg text-xs font-medium">
                              Resolve
                            </button>
                            <button className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-xs font-medium">
                              False Alarm
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>

        {/* Empty state */}
        {filteredAlerts.length === 0 && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center">
            <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-white mb-2">No alerts found</h3>
            <p className="text-slate-400">
              {filterStatus !== 'all' || filterSeverity !== 'all'
                ? 'Try adjusting your filters'
                : 'All clear! No mismatches detected.'}
            </p>
          </div>
        )}

        {/* Alert Detail Modal (simplified) */}
        {selectedAlert && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setSelectedAlert(null)}>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 max-w-2xl w-full mx-4" onClick={e => e.stopPropagation()}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold text-white">Alert Details</h3>
                <button onClick={() => setSelectedAlert(null)} className="text-slate-400 hover:text-white">
                  <XCircle className="w-6 h-6" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <span className={`px-2 py-1 text-xs font-medium rounded ${severityConfig[selectedAlert.severity].bgClass} ${severityConfig[selectedAlert.severity].textClass}`}>
                    {severityConfig[selectedAlert.severity].label}
                  </span>
                  <h4 className="text-lg font-medium text-white mt-2">{selectedAlert.description}</h4>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-800 rounded-lg p-4">
                    <p className="text-sm text-slate-400 mb-1">What We Detected</p>
                    <p className="text-red-400">{selectedAlert.detectedValue}</p>
                  </div>
                  <div className="bg-slate-800 rounded-lg p-4">
                    <p className="text-sm text-slate-400 mb-1">What Spec Says</p>
                    <p className="text-emerald-400">{selectedAlert.expectedValue}</p>
                  </div>
                </div>
                
                <div className="bg-slate-800 rounded-lg p-4">
                  <p className="text-sm text-slate-400 mb-1">Source Document</p>
                  <p className="text-white">{selectedAlert.sourceDocument}</p>
                </div>
                
                <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
                  <p className="text-sm text-slate-400 mb-1">Potential Cost Impact</p>
                  <p className="text-2xl font-bold text-red-400">₹{selectedAlert.costImpact} Lakh</p>
                  <p className="text-sm text-slate-400 mt-1">If not fixed before concrete pour</p>
                </div>
              </div>
              
              {selectedAlert.status === 'open' && (
                <div className="flex gap-3 mt-6">
                  <button className="flex-1 px-4 py-3 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg font-medium">
                    Mark as Resolved
                  </button>
                  <button className="flex-1 px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium">
                    Mark as False Alarm
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}

