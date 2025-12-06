import Layout from '@/components/Layout'
import {
  Users,
  Plus,
  Search,
  MoreVertical,
  Phone,
  Building2,
  MessageSquare,
  Clock,
  Shield,
  Edit,
  Trash2,
  Mail,
} from 'lucide-react'

const users = [
  {
    id: 1,
    name: 'Rajesh Kumar',
    phone: '+91 98765 43210',
    email: 'rajesh@site.com',
    role: 'Site Engineer',
    site: 'Skyline Towers',
    queries: 156,
    lastActive: '2024-12-06T10:30:00',
    status: 'active',
  },
  {
    id: 2,
    name: 'Arun Singh',
    phone: '+91 98765 43211',
    email: 'arun@site.com',
    role: 'Site Engineer',
    site: 'Green Valley',
    queries: 134,
    lastActive: '2024-12-06T09:45:00',
    status: 'active',
  },
  {
    id: 3,
    name: 'Vijay Sharma',
    phone: '+91 98765 43212',
    email: 'vijay@site.com',
    role: 'Project Manager',
    site: 'Phoenix Mall',
    queries: 89,
    lastActive: '2024-12-06T08:15:00',
    status: 'active',
  },
  {
    id: 4,
    name: 'Priya Reddy',
    phone: '+91 98765 43213',
    email: 'priya@abc.com',
    role: 'Admin',
    site: 'All Sites',
    queries: 45,
    lastActive: '2024-12-05T18:30:00',
    status: 'active',
  },
  {
    id: 5,
    name: 'Mohammed Ali',
    phone: '+91 98765 43214',
    email: 'ali@site.com',
    role: 'Site Engineer',
    site: 'Marina Bay',
    queries: 67,
    lastActive: '2024-12-05T16:00:00',
    status: 'active',
  },
]

const roleColors = {
  'Site Engineer': 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  'Project Manager': 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  'Admin': 'bg-primary-500/10 text-primary-400 border-primary-500/20',
}

export default function UsersPage() {
  return (
    <Layout companyName="ABC Developers">
      <div className="p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Users</h1>
            <p className="text-slate-400">
              Manage site engineers and dashboard access
            </p>
          </div>
          <button className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Add User
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
            <div className="p-3 bg-blue-500/10 rounded-lg">
              <Users className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">34</p>
              <p className="text-sm text-slate-400">Total Users</p>
            </div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
            <div className="p-3 bg-emerald-500/10 rounded-lg">
              <Users className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">28</p>
              <p className="text-sm text-slate-400">Site Engineers</p>
            </div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
            <div className="p-3 bg-purple-500/10 rounded-lg">
              <Shield className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">4</p>
              <p className="text-sm text-slate-400">Project Managers</p>
            </div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
            <div className="p-3 bg-primary-500/10 rounded-lg">
              <Shield className="w-5 h-5 text-primary-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">2</p>
              <p className="text-sm text-slate-400">Admins</p>
            </div>
          </div>
        </div>

        {/* Search */}
        <div className="flex items-center gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search users..."
              className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-10 pr-4 py-2.5 text-white placeholder-slate-400 focus:outline-none focus:border-primary-500"
            />
          </div>
          <select className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-primary-500">
            <option>All Sites</option>
            <option>Skyline Towers</option>
            <option>Green Valley</option>
            <option>Phoenix Mall</option>
          </select>
          <select className="bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:border-primary-500">
            <option>All Roles</option>
            <option>Site Engineer</option>
            <option>Project Manager</option>
            <option>Admin</option>
          </select>
        </div>

        {/* Users Table */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <table className="w-full">
            <thead className="bg-slate-800/50">
              <tr>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">User</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Role</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Site</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Queries</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Last Active</th>
                <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Status</th>
                <th className="text-right px-6 py-4 text-sm font-medium text-slate-400">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-slate-800/50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500/20 to-primary-600/10 flex items-center justify-center">
                        <span className="text-sm font-semibold text-primary-400">
                          {user.name.split(' ').map(n => n[0]).join('')}
                        </span>
                      </div>
                      <div>
                        <p className="font-medium text-white">{user.name}</p>
                        <div className="flex items-center gap-2 text-sm text-slate-400">
                          <Phone className="w-3 h-3" />
                          {user.phone}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium border ${roleColors[user.role as keyof typeof roleColors]}`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2 text-slate-300">
                      <Building2 className="w-4 h-4 text-slate-400" />
                      {user.site}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2 text-slate-300">
                      <MessageSquare className="w-4 h-4 text-slate-400" />
                      {user.queries}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2 text-slate-400 text-sm">
                      <Clock className="w-4 h-4" />
                      {new Date(user.lastActive).toLocaleString('en-IN', {
                        day: 'numeric',
                        month: 'short',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      user.status === 'active'
                        ? 'bg-emerald-500/10 text-emerald-400'
                        : 'bg-slate-500/10 text-slate-400'
                    }`}>
                      {user.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button className="p-2 hover:bg-slate-700 rounded transition-colors">
                        <Edit className="w-4 h-4 text-slate-400" />
                      </button>
                      <button className="p-2 hover:bg-red-500/10 rounded transition-colors">
                        <Trash2 className="w-4 h-4 text-slate-400 hover:text-red-400" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Help Section */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h3 className="font-semibold text-white mb-4">How Users Connect</h3>
            <ol className="space-y-3 text-sm">
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-primary-500/10 text-primary-400 flex items-center justify-center text-xs font-medium flex-shrink-0">1</span>
                <span className="text-slate-300">Add user with their WhatsApp number</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-primary-500/10 text-primary-400 flex items-center justify-center text-xs font-medium flex-shrink-0">2</span>
                <span className="text-slate-300">Assign them to a site (or multiple sites)</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-primary-500/10 text-primary-400 flex items-center justify-center text-xs font-medium flex-shrink-0">3</span>
                <span className="text-slate-300">User messages SiteMind WhatsApp number</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-primary-500/10 text-primary-400 flex items-center justify-center text-xs font-medium flex-shrink-0">4</span>
                <span className="text-slate-300">AI automatically knows their site context</span>
              </li>
            </ol>
          </div>
          
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h3 className="font-semibold text-white mb-4">Role Permissions</h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-start justify-between">
                <span className="text-slate-300">Site Engineer</span>
                <span className="text-slate-400">WhatsApp queries only</span>
              </div>
              <div className="flex items-start justify-between">
                <span className="text-slate-300">Project Manager</span>
                <span className="text-slate-400">WhatsApp + Dashboard (single site)</span>
              </div>
              <div className="flex items-start justify-between">
                <span className="text-slate-300">Admin</span>
                <span className="text-slate-400">Full dashboard (all sites)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

