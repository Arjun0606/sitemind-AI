import { useState } from 'react'
import Layout from '@/components/Layout'
import {
  Users,
  Plus,
  Search,
  MoreVertical,
  Phone,
  Mail,
  Clock,
  Shield,
  Trash2,
  Edit,
} from 'lucide-react'

interface Member {
  id: string
  name: string
  phone: string
  email: string
  role: string
  last_active: string
}

const mockMembers: Member[] = [
  { id: '1', name: 'Rajesh Kumar', phone: '+91 98765 43210', email: 'rajesh@abc.com', role: 'admin', last_active: '2 hours ago' },
  { id: '2', name: 'Arun Sharma', phone: '+91 98765 43211', email: 'arun@abc.com', role: 'site_engineer', last_active: '30 mins ago' },
  { id: '3', name: 'Vijay Patel', phone: '+91 98765 43212', email: 'vijay@abc.com', role: 'site_engineer', last_active: '1 day ago' },
  { id: '4', name: 'Suresh Reddy', phone: '+91 98765 43213', email: 'suresh@abc.com', role: 'project_manager', last_active: '5 hours ago' },
  { id: '5', name: 'Kiran Rao', phone: '+91 98765 43214', email: 'kiran@abc.com', role: 'site_engineer', last_active: '3 days ago' },
]

const roleLabels: Record<string, string> = {
  admin: 'Admin',
  project_manager: 'Project Manager',
  site_engineer: 'Site Engineer',
  viewer: 'Viewer',
}

const roleColors: Record<string, string> = {
  admin: 'bg-purple-500/20 text-purple-400',
  project_manager: 'bg-blue-500/20 text-blue-400',
  site_engineer: 'bg-green-500/20 text-green-400',
  viewer: 'bg-slate-500/20 text-slate-400',
}

export default function MembersPage() {
  const [members, setMembers] = useState(mockMembers)
  const [search, setSearch] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)

  const filteredMembers = members.filter(m => 
    m.name.toLowerCase().includes(search.toLowerCase()) ||
    m.email.toLowerCase().includes(search.toLowerCase()) ||
    m.phone.includes(search)
  )

  return (
    <Layout companyName="ABC Developers">
      <div className="p-6 lg:p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white mb-2">Team Members</h1>
            <p className="text-slate-400">
              Manage who has access to SiteMind
            </p>
          </div>
          <button 
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors"
          >
            <Plus className="w-5 h-5" />
            Add Member
          </button>
        </div>

        {/* Search */}
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            placeholder="Search by name, email, or phone..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-3 bg-slate-900 border border-slate-800 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-primary-500"
          />
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <p className="text-slate-400 text-sm mb-1">Total Members</p>
            <p className="text-2xl font-bold text-white">{members.length}</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <p className="text-slate-400 text-sm mb-1">Admins</p>
            <p className="text-2xl font-bold text-white">{members.filter(m => m.role === 'admin').length}</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <p className="text-slate-400 text-sm mb-1">Active Today</p>
            <p className="text-2xl font-bold text-white">{members.filter(m => m.last_active.includes('hour') || m.last_active.includes('min')).length}</p>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <p className="text-slate-400 text-sm mb-1">Unlimited Users</p>
            <p className="text-2xl font-bold text-green-400">✓</p>
          </div>
        </div>

        {/* Members List */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-800">
                  <th className="text-left p-4 text-slate-400 font-medium">Member</th>
                  <th className="text-left p-4 text-slate-400 font-medium">Contact</th>
                  <th className="text-left p-4 text-slate-400 font-medium">Role</th>
                  <th className="text-left p-4 text-slate-400 font-medium">Last Active</th>
                  <th className="text-right p-4 text-slate-400 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredMembers.map((member) => (
                  <tr key={member.id} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-primary-500/20 flex items-center justify-center">
                          <span className="text-primary-400 font-medium">
                            {member.name.split(' ').map(n => n[0]).join('')}
                          </span>
                        </div>
                        <span className="text-white font-medium">{member.name}</span>
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2 text-slate-400 text-sm">
                          <Phone className="w-4 h-4" />
                          {member.phone}
                        </div>
                        <div className="flex items-center gap-2 text-slate-400 text-sm">
                          <Mail className="w-4 h-4" />
                          {member.email}
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${roleColors[member.role]}`}>
                        {roleLabels[member.role]}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-2 text-slate-400 text-sm">
                        <Clock className="w-4 h-4" />
                        {member.last_active}
                      </div>
                    </td>
                    <td className="p-4">
                      <div className="flex items-center justify-end gap-2">
                        <button className="p-2 hover:bg-slate-700 rounded-lg transition-colors">
                          <Edit className="w-4 h-4 text-slate-400" />
                        </button>
                        <button className="p-2 hover:bg-red-500/20 rounded-lg transition-colors">
                          <Trash2 className="w-4 h-4 text-red-400" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Add via WhatsApp Note */}
        <div className="mt-6 p-4 bg-slate-900/50 border border-slate-800 rounded-xl">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center flex-shrink-0">
              <Phone className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <h3 className="font-medium text-white mb-1">Add Members via WhatsApp</h3>
              <p className="text-slate-400 text-sm">
                Team members can also be added directly from WhatsApp by an admin. 
                Just send: <code className="bg-slate-800 px-2 py-0.5 rounded text-primary-400">/addmember +91XXXXXXXXXX Name</code>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Add Member Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-xl w-full max-w-md p-6">
            <h2 className="text-xl font-bold text-white mb-4">Add Team Member</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-slate-400 mb-1">Name</label>
                <input
                  type="text"
                  placeholder="Full name"
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-primary-500"
                />
              </div>
              
              <div>
                <label className="block text-sm text-slate-400 mb-1">Phone (WhatsApp)</label>
                <input
                  type="tel"
                  placeholder="+91 98765 43210"
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-primary-500"
                />
              </div>
              
              <div>
                <label className="block text-sm text-slate-400 mb-1">Email (Optional)</label>
                <input
                  type="email"
                  placeholder="email@company.com"
                  className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-primary-500"
                />
              </div>
              
              <div>
                <label className="block text-sm text-slate-400 mb-1">Role</label>
                <select className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-primary-500">
                  <option value="site_engineer">Site Engineer</option>
                  <option value="project_manager">Project Manager</option>
                  <option value="admin">Admin</option>
                  <option value="viewer">Viewer</option>
                </select>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowAddModal(false)}
                className="flex-1 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button className="flex-1 px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors">
                Add Member
              </button>
            </div>
          </div>
        </div>
      )}
    </Layout>
  )
}

