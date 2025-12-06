import Layout from '@/components/Layout'
import {
  Building2,
  Search,
  Filter,
  Plus,
  MapPin,
  Users,
  MessageSquare,
  Calendar,
  MoreVertical,
  ArrowUpRight,
} from 'lucide-react'
import Link from 'next/link'

const sites = [
  {
    id: 'site_1',
    name: 'Skyline Towers Block A',
    city: 'Hyderabad',
    address: 'Gachibowli, Hyderabad',
    status: 'active',
    engineers: 8,
    queries: 456,
    blueprints: 12,
    startDate: '2024-06-15',
    subscription: 'active',
    monthlyQueries: 156,
  },
  {
    id: 'site_2',
    name: 'Green Valley Residency',
    city: 'Hyderabad',
    address: 'Madhapur, Hyderabad',
    status: 'active',
    engineers: 6,
    queries: 389,
    blueprints: 8,
    startDate: '2024-07-01',
    subscription: 'active',
    monthlyQueries: 134,
  },
  {
    id: 'site_3',
    name: 'Phoenix Mall Extension',
    city: 'Bangalore',
    address: 'Whitefield, Bangalore',
    status: 'active',
    engineers: 5,
    queries: 234,
    blueprints: 15,
    startDate: '2024-08-10',
    subscription: 'active',
    monthlyQueries: 89,
  },
  {
    id: 'site_4',
    name: 'Marina Bay Complex',
    city: 'Chennai',
    address: 'OMR, Chennai',
    status: 'active',
    engineers: 4,
    queries: 198,
    blueprints: 6,
    startDate: '2024-09-01',
    subscription: 'pilot',
    monthlyQueries: 67,
  },
]

export default function SitesPage() {
  return (
    <Layout companyName="ABC Developers">
      <div className="p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Sites</h1>
            <p className="text-slate-400">
              Manage all your construction sites in one place
            </p>
          </div>
          <button className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Add New Site
          </button>
        </div>

        {/* Search and Filters */}
        <div className="flex items-center gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search sites..."
              className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-10 pr-4 py-2.5 text-white placeholder-slate-400 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
            />
          </div>
          <button className="px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-slate-300 hover:bg-slate-800 transition-colors flex items-center gap-2">
            <Filter className="w-4 h-4" />
            Filters
          </button>
        </div>

        {/* Sites Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {sites.map((site) => (
            <Link
              key={site.id}
              href={`/sites/${site.id}`}
              className="bg-slate-900 border border-slate-800 rounded-xl p-6 hover:border-primary-500/50 transition-all card-hover group"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary-500/20 to-primary-600/5 border border-primary-500/20 flex items-center justify-center">
                  <Building2 className="w-6 h-6 text-primary-500" />
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    site.subscription === 'active'
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      : 'bg-purple-500/10 text-purple-400 border border-purple-500/20'
                  }`}>
                    {site.subscription === 'active' ? 'Active' : 'Pilot'}
                  </span>
                  <button className="p-1 hover:bg-slate-800 rounded">
                    <MoreVertical className="w-4 h-4 text-slate-400" />
                  </button>
                </div>
              </div>

              <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-primary-500 transition-colors">
                {site.name}
              </h3>

              <div className="flex items-center gap-2 text-slate-400 text-sm mb-4">
                <MapPin className="w-4 h-4" />
                <span>{site.address}</span>
              </div>

              <div className="grid grid-cols-3 gap-4 pt-4 border-t border-slate-800">
                <div>
                  <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
                    <Users className="w-3.5 h-3.5" />
                    <span>Engineers</span>
                  </div>
                  <p className="font-semibold text-white">{site.engineers}</p>
                </div>
                <div>
                  <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
                    <MessageSquare className="w-3.5 h-3.5" />
                    <span>Queries</span>
                  </div>
                  <p className="font-semibold text-white">{site.monthlyQueries}</p>
                </div>
                <div>
                  <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>Since</span>
                  </div>
                  <p className="font-semibold text-white">
                    {new Date(site.startDate).toLocaleDateString('en-IN', { month: 'short', year: '2-digit' })}
                  </p>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-slate-800 flex items-center justify-between">
                <span className="text-sm text-slate-400">
                  {site.blueprints} blueprints uploaded
                </span>
                <ArrowUpRight className="w-4 h-4 text-primary-500 opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
            </Link>
          ))}

          {/* Add Site Card */}
          <button className="bg-slate-900/50 border-2 border-dashed border-slate-700 rounded-xl p-6 hover:border-primary-500/50 hover:bg-slate-900 transition-all flex flex-col items-center justify-center min-h-[280px] group">
            <div className="w-16 h-16 rounded-full bg-slate-800 group-hover:bg-primary-500/10 flex items-center justify-center mb-4 transition-colors">
              <Plus className="w-8 h-8 text-slate-400 group-hover:text-primary-500 transition-colors" />
            </div>
            <p className="text-lg font-medium text-slate-400 group-hover:text-white transition-colors">
              Add New Site
            </p>
            <p className="text-sm text-slate-500 mt-1">
              $500/month per site
            </p>
          </button>
        </div>
      </div>
    </Layout>
  )
}

