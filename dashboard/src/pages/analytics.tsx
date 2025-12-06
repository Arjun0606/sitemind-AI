import Layout from '@/components/Layout'
import StatsCard from '@/components/StatsCard'
import {
  MessageSquare,
  Clock,
  IndianRupee,
  TrendingUp,
  Building2,
  Calendar,
  Download,
} from 'lucide-react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts'

const queryData = [
  { date: 'Week 1', queries: 520, value: 45000 },
  { date: 'Week 2', queries: 680, value: 62000 },
  { date: 'Week 3', queries: 720, value: 68000 },
  { date: 'Week 4', queries: 890, value: 82000 },
]

const siteBreakdown = [
  { name: 'Skyline Towers', queries: 456, color: '#ed7620' },
  { name: 'Green Valley', queries: 389, color: '#f19241' },
  { name: 'Phoenix Mall', queries: 234, color: '#f6b978' },
  { name: 'Marina Bay', queries: 198, color: '#fad6ac' },
]

const queryTypes = [
  { type: 'Blueprint specs', count: 456, percentage: 35 },
  { type: 'Material queries', count: 324, percentage: 25 },
  { type: 'Change orders', count: 260, percentage: 20 },
  { type: 'Safety protocols', count: 156, percentage: 12 },
  { type: 'RFI lookups', count: 104, percentage: 8 },
]

const responseTimeData = [
  { hour: '6AM', time: 3.2 },
  { hour: '8AM', time: 4.8 },
  { hour: '10AM', time: 5.2 },
  { hour: '12PM', time: 4.1 },
  { hour: '2PM', time: 4.5 },
  { hour: '4PM', time: 3.8 },
  { hour: '6PM', time: 3.0 },
]

export default function AnalyticsPage() {
  return (
    <Layout companyName="ABC Developers">
      <div className="p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Analytics</h1>
            <p className="text-slate-400">
              Deep insights into your SiteMind usage and ROI
            </p>
          </div>
          <div className="flex items-center gap-3">
            <select className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary-500">
              <option>Last 30 days</option>
              <option>Last 7 days</option>
              <option>Last 90 days</option>
              <option>This year</option>
            </select>
            <button className="px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white hover:bg-slate-800 transition-colors flex items-center gap-2">
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Total Queries"
            value="2,847"
            subtitle="This month"
            icon={MessageSquare}
            trend={{ value: 35, isPositive: true }}
            color="blue"
          />
          <StatsCard
            title="Avg Response"
            value="4.2s"
            subtitle="vs 30min industry avg"
            icon={Clock}
            color="purple"
          />
          <StatsCard
            title="Est. Value"
            value="₹28.4L"
            subtitle="Time & error savings"
            icon={IndianRupee}
            trend={{ value: 28, isPositive: true }}
            color="green"
          />
          <StatsCard
            title="ROI"
            value="34.8x"
            subtitle="Value vs subscription"
            icon={TrendingUp}
            color="orange"
          />
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Query Trend */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-6">Query Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={queryData}>
                <defs>
                  <linearGradient id="queryGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ed7620" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#ed7620" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1e293b', 
                    border: '1px solid #334155',
                    borderRadius: '8px'
                  }}
                />
                <Area 
                  type="monotone" 
                  dataKey="queries" 
                  stroke="#ed7620" 
                  strokeWidth={2}
                  fill="url(#queryGradient)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Site Breakdown */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-6">Queries by Site</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={siteBreakdown} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis type="number" stroke="#64748b" />
                <YAxis dataKey="name" type="category" stroke="#64748b" width={100} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1e293b', 
                    border: '1px solid #334155',
                    borderRadius: '8px'
                  }}
                />
                <Bar dataKey="queries" radius={[0, 4, 4, 0]}>
                  {siteBreakdown.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Query Types */}
          <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-6">Query Categories</h3>
            <div className="space-y-4">
              {queryTypes.map((item) => (
                <div key={item.type}>
                  <div className="flex items-center justify-between text-sm mb-2">
                    <span className="text-slate-300">{item.type}</span>
                    <span className="text-white font-medium">{item.count} ({item.percentage}%)</span>
                  </div>
                  <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-primary-500 to-primary-400 rounded-full"
                      style={{ width: `${item.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Response Time by Hour */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-2">Response Time</h3>
            <p className="text-sm text-slate-400 mb-6">Average by hour of day</p>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={responseTimeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="hour" stroke="#64748b" />
                <YAxis stroke="#64748b" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1e293b', 
                    border: '1px solid #334155',
                    borderRadius: '8px'
                  }}
                  formatter={(value: number) => [`${value}s`, 'Avg Time']}
                />
                <Bar dataKey="time" fill="#ed7620" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* ROI Breakdown */}
        <div className="mt-8 bg-gradient-to-br from-primary-500/10 to-primary-600/5 border border-primary-500/20 rounded-xl p-8">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h3 className="text-xl font-semibold text-white mb-2">ROI Breakdown</h3>
              <p className="text-slate-400">How we calculate your estimated value</p>
            </div>
            <button className="text-sm text-primary-500 hover:text-primary-400 font-medium">
              View methodology →
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-slate-900/50 rounded-lg p-4">
              <p className="text-sm text-slate-400 mb-2">Time Saved</p>
              <p className="text-2xl font-bold text-white">~237 hours</p>
              <p className="text-sm text-slate-400 mt-1">
                @ avg 5min per manual lookup
              </p>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-4">
              <p className="text-sm text-slate-400 mb-2">Errors Prevented</p>
              <p className="text-2xl font-bold text-white">~12 issues</p>
              <p className="text-sm text-slate-400 mt-1">
                Based on industry error rates
              </p>
            </div>
            <div className="bg-slate-900/50 rounded-lg p-4">
              <p className="text-sm text-slate-400 mb-2">Cost Avoided</p>
              <p className="text-2xl font-bold text-white">₹28.4L</p>
              <p className="text-sm text-slate-400 mt-1">
                Conservative estimate
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

