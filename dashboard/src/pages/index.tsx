import Layout from '@/components/Layout'
import StatsCard from '@/components/StatsCard'
import {
  Building2,
  MessageSquare,
  IndianRupee,
  Clock,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  ArrowRight,
} from 'lucide-react'

// Mock data - will come from API
const stats = {
  totalSites: 12,
  totalQueries: 2847,
  estimatedValue: '₹28.4L',
  avgResponseTime: '4.2s',
}

const sites = [
  {
    id: 1,
    name: 'Skyline Towers Block A',
    city: 'Hyderabad',
    status: 'active',
    queries: 456,
    engineers: 8,
    lastActivity: '2 mins ago',
  },
  {
    id: 2,
    name: 'Green Valley Residency',
    city: 'Hyderabad',
    status: 'active',
    queries: 389,
    engineers: 6,
    lastActivity: '15 mins ago',
  },
  {
    id: 3,
    name: 'Phoenix Mall Extension',
    city: 'Bangalore',
    status: 'active',
    queries: 234,
    engineers: 5,
    lastActivity: '1 hour ago',
  },
  {
    id: 4,
    name: 'Marina Bay Complex',
    city: 'Chennai',
    status: 'active',
    queries: 198,
    engineers: 4,
    lastActivity: '3 hours ago',
  },
]

const recentQueries = [
  {
    id: 1,
    query: 'What is the beam size at grid B2 on floor 3?',
    site: 'Skyline Towers',
    engineer: 'Rajesh Kumar',
    time: '2 mins ago',
    answered: true,
  },
  {
    id: 2,
    query: 'Column spacing on grid A?',
    site: 'Green Valley',
    engineer: 'Arun Singh',
    time: '15 mins ago',
    answered: true,
  },
  {
    id: 3,
    query: 'Rebar specification for slab S3?',
    site: 'Phoenix Mall',
    engineer: 'Vijay Sharma',
    time: '1 hour ago',
    answered: true,
  },
]

const alerts = [
  {
    id: 1,
    type: 'warning',
    message: 'Blueprint revision uploaded for Skyline Towers',
    time: '1 hour ago',
  },
  {
    id: 2,
    type: 'info',
    message: 'Weekly report generated for all sites',
    time: '6 hours ago',
  },
]

export default function Dashboard() {
  return (
    <Layout companyName="ABC Developers">
      <div className="p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
          <p className="text-slate-400">
            Welcome back! Here's what's happening across your sites.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Active Sites"
            value={stats.totalSites}
            subtitle="All performing well"
            icon={Building2}
            trend={{ value: 20, isPositive: true }}
            color="orange"
          />
          <StatsCard
            title="Queries This Month"
            value={stats.totalQueries.toLocaleString()}
            subtitle="Unlimited included"
            icon={MessageSquare}
            trend={{ value: 35, isPositive: true }}
            color="blue"
          />
          <StatsCard
            title="Estimated Value"
            value={stats.estimatedValue}
            subtitle="Based on industry benchmarks"
            icon={IndianRupee}
            trend={{ value: 28, isPositive: true }}
            color="green"
          />
          <StatsCard
            title="Avg Response Time"
            value={stats.avgResponseTime}
            subtitle="vs 30min industry avg"
            icon={Clock}
            color="purple"
          />
        </div>

        {/* Two column layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Sites List */}
          <div className="lg:col-span-2">
            <div className="bg-slate-900 border border-slate-800 rounded-xl">
              <div className="p-6 border-b border-slate-800 flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-white">Your Sites</h2>
                  <p className="text-sm text-slate-400 mt-1">Click to view details</p>
                </div>
                <button className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors flex items-center gap-2">
                  <Building2 className="w-4 h-4" />
                  Add Site
                </button>
              </div>
              <div className="divide-y divide-slate-800">
                {sites.map((site) => (
                  <div
                    key={site.id}
                    className="p-6 hover:bg-slate-800/50 transition-colors cursor-pointer flex items-center justify-between"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500/20 to-primary-600/5 border border-primary-500/20 flex items-center justify-center">
                        <Building2 className="w-6 h-6 text-primary-500" />
                      </div>
                      <div>
                        <h3 className="font-medium text-white">{site.name}</h3>
                        <p className="text-sm text-slate-400">{site.city} • {site.engineers} engineers</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-6">
                      <div className="text-right">
                        <p className="font-medium text-white">{site.queries} queries</p>
                        <p className="text-sm text-slate-400">{site.lastActivity}</p>
                      </div>
                      <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                        site.status === 'active'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : 'bg-slate-500/10 text-slate-400 border border-slate-500/20'
                      }`}>
                        {site.status}
                      </div>
                      <ArrowRight className="w-5 h-5 text-slate-400" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right sidebar */}
          <div className="space-y-8">
            {/* Recent Queries */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl">
              <div className="p-6 border-b border-slate-800">
                <h2 className="text-lg font-semibold text-white">Recent Queries</h2>
              </div>
              <div className="divide-y divide-slate-800">
                {recentQueries.map((query) => (
                  <div key={query.id} className="p-4">
                    <div className="flex items-start gap-3">
                      <CheckCircle className="w-5 h-5 text-emerald-400 mt-0.5 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-white line-clamp-2">{query.query}</p>
                        <p className="text-xs text-slate-400 mt-1">
                          {query.engineer} • {query.site} • {query.time}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="p-4 border-t border-slate-800">
                <button className="text-sm text-primary-500 hover:text-primary-400 font-medium">
                  View all queries →
                </button>
              </div>
            </div>

            {/* Alerts */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl">
              <div className="p-6 border-b border-slate-800">
                <h2 className="text-lg font-semibold text-white">Alerts</h2>
              </div>
              <div className="divide-y divide-slate-800">
                {alerts.map((alert) => (
                  <div key={alert.id} className="p-4">
                    <div className="flex items-start gap-3">
                      <AlertTriangle className={`w-5 h-5 flex-shrink-0 ${
                        alert.type === 'warning' ? 'text-amber-400' : 'text-blue-400'
                      }`} />
                      <div>
                        <p className="text-sm text-white">{alert.message}</p>
                        <p className="text-xs text-slate-400 mt-1">{alert.time}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* ROI Card */}
            <div className="bg-gradient-to-br from-primary-500/20 to-primary-600/5 border border-primary-500/20 rounded-xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="w-5 h-5 text-primary-500" />
                <h3 className="font-semibold text-white">This Month's ROI</h3>
              </div>
              <p className="text-4xl font-bold gradient-text mb-2">~34.8x</p>
              <p className="text-sm text-slate-400">
                Based on ₹28.4L estimated value vs ₹41,500 subscription
              </p>
              <button className="mt-4 text-sm text-primary-500 hover:text-primary-400 font-medium">
                View detailed report →
              </button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

