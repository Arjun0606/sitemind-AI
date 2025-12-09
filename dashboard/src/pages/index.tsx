import { useState, useEffect } from 'react'
import Layout from '@/components/Layout'
import Link from 'next/link'
import {
  Building2,
  MessageSquare,
  FileText,
  AlertTriangle,
  CheckCircle,
  Clock,
  Users,
  TrendingUp,
  ArrowRight,
  Search,
  Bell,
  BarChart3,
} from 'lucide-react'

// Types
interface ProjectSummary {
  id: string
  name: string
  location: string
  stage: string
  rfis: number
  issues: number
  decisions: number
}

interface CompanyStats {
  total_rfis: number
  open_rfis: number
  total_decisions: number
  total_issues: number
  open_issues: number
  total_drawings: number
}

// Mock data - replace with API calls
const mockData = {
  company: {
    id: 'company-1',
    name: 'ABC Developers',
    is_pilot: false,
  },
  stats: {
    total_rfis: 45,
    open_rfis: 8,
    total_decisions: 156,
    total_issues: 23,
    open_issues: 5,
    total_drawings: 89,
  },
  projects: [
    { id: '1', name: 'Skyline Towers Block A', location: 'Hyderabad', stage: 'active', rfis: 3, issues: 2, decisions: 45 },
    { id: '2', name: 'Green Valley Residency', location: 'Hyderabad', stage: 'active', rfis: 2, issues: 1, decisions: 38 },
    { id: '3', name: 'Phoenix Mall Extension', location: 'Bangalore', stage: 'active', rfis: 3, issues: 2, decisions: 28 },
    { id: '4', name: 'Marina Heights', location: 'Chennai', stage: 'active', rfis: 0, issues: 0, decisions: 15 },
  ],
  members: 34,
  active_users: 28,
}

export default function Dashboard() {
  const [data, setData] = useState(mockData)
  const [loading, setLoading] = useState(false)

  // In production, fetch from API
  // useEffect(() => {
  //   fetch('/api/dashboard/company/company-1')
  //     .then(res => res.json())
  //     .then(setData)
  // }, [])

  const stats = data.stats

  return (
    <Layout companyName={data.company.name}>
      <div className="p-6 lg:p-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white mb-2">Dashboard</h1>
          <p className="text-slate-400">
            Overview of all your projects
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {/* Open RFIs */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-lg bg-orange-500/20 flex items-center justify-center">
                <Clock className="w-5 h-5 text-orange-400" />
              </div>
              <span className="text-slate-400 text-sm">Open RFIs</span>
            </div>
            <p className="text-3xl font-bold text-white">{stats.open_rfis}</p>
            <p className="text-slate-500 text-sm mt-1">of {stats.total_rfis} total</p>
          </div>

          {/* Open Issues */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-red-400" />
              </div>
              <span className="text-slate-400 text-sm">Open Issues</span>
            </div>
            <p className="text-3xl font-bold text-white">{stats.open_issues}</p>
            <p className="text-slate-500 text-sm mt-1">of {stats.total_issues} total</p>
          </div>

          {/* Decisions */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-green-400" />
              </div>
              <span className="text-slate-400 text-sm">Decisions</span>
            </div>
            <p className="text-3xl font-bold text-white">{stats.total_decisions}</p>
            <p className="text-slate-500 text-sm mt-1">logged this month</p>
          </div>

          {/* Drawings */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                <FileText className="w-5 h-5 text-blue-400" />
              </div>
              <span className="text-slate-400 text-sm">Drawings</span>
            </div>
            <p className="text-3xl font-bold text-white">{stats.total_drawings}</p>
            <p className="text-slate-500 text-sm mt-1">indexed</p>
          </div>
        </div>

        {/* Attention Required */}
        {(stats.open_rfis > 0 || stats.open_issues > 0) && (
          <div className="bg-orange-500/10 border border-orange-500/30 rounded-xl p-5 mb-8">
            <div className="flex items-center gap-3 mb-4">
              <Bell className="w-5 h-5 text-orange-400" />
              <h2 className="font-semibold text-white">Attention Required</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {stats.open_rfis > 0 && (
                <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
                  <div>
                    <p className="text-white font-medium">{stats.open_rfis} RFIs pending response</p>
                    <p className="text-slate-400 text-sm">Across all projects</p>
                  </div>
                  <Link href="/rfis" className="text-orange-400 hover:text-orange-300">
                    <ArrowRight className="w-5 h-5" />
                  </Link>
                </div>
              )}
              {stats.open_issues > 0 && (
                <div className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
                  <div>
                    <p className="text-white font-medium">{stats.open_issues} issues need attention</p>
                    <p className="text-slate-400 text-sm">Across all projects</p>
                  </div>
                  <Link href="/issues" className="text-orange-400 hover:text-orange-300">
                    <ArrowRight className="w-5 h-5" />
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Projects */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">Projects ({data.projects.length})</h2>
            <Link 
              href="/projects" 
              className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-1"
            >
              View all <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.projects.map((project) => (
              <Link
                key={project.id}
                href={`/projects/${project.id}`}
                className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-colors"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-medium text-white">{project.name}</h3>
                    <p className="text-slate-500 text-sm">{project.location}</p>
                  </div>
                  {(project.rfis > 0 || project.issues > 0) ? (
                    <span className="px-2 py-1 text-xs font-medium bg-orange-500/20 text-orange-400 rounded-full">
                      {project.rfis + project.issues} pending
                    </span>
                  ) : (
                    <span className="px-2 py-1 text-xs font-medium bg-green-500/20 text-green-400 rounded-full">
                      Clear
                    </span>
                  )}
                </div>
                
                <div className="flex items-center gap-4 text-sm text-slate-400">
                  <span className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {project.rfis} RFIs
                  </span>
                  <span className="flex items-center gap-1">
                    <AlertTriangle className="w-4 h-4" />
                    {project.issues} issues
                  </span>
                  <span className="flex items-center gap-1">
                    <CheckCircle className="w-4 h-4" />
                    {project.decisions} decisions
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Bottom Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Team */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-white">Team</h3>
              <Link href="/members" className="text-sm text-primary-400 hover:text-primary-300">
                Manage
              </Link>
            </div>
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-primary-500/20 flex items-center justify-center">
                <Users className="w-6 h-6 text-primary-400" />
              </div>
              <div>
                <p className="text-2xl font-bold text-white">{data.members}</p>
                <p className="text-slate-400 text-sm">{data.active_users} active this week</p>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <h3 className="font-semibold text-white mb-4">Quick Actions</h3>
            <div className="space-y-2">
              <Link 
                href="/reports" 
                className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-800 transition-colors"
              >
                <BarChart3 className="w-5 h-5 text-slate-400" />
                <span className="text-slate-300">Generate Weekly Report</span>
              </Link>
              <Link 
                href="/search" 
                className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-800 transition-colors"
              >
                <Search className="w-5 h-5 text-slate-400" />
                <span className="text-slate-300">Search All Projects</span>
              </Link>
            </div>
          </div>

          {/* Usage */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-white">Usage This Month</h3>
              <Link href="/billing" className="text-sm text-primary-400 hover:text-primary-300">
                Details
              </Link>
            </div>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-400">AI Queries</span>
                  <span className="text-white">456 / 1,000</span>
                </div>
                <div className="h-2 bg-slate-800 rounded-full">
                  <div className="h-full bg-primary-500 rounded-full" style={{ width: '45.6%' }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-slate-400">Documents</span>
                  <span className="text-white">23 / 50</span>
                </div>
                <div className="h-2 bg-slate-800 rounded-full">
                  <div className="h-full bg-blue-500 rounded-full" style={{ width: '46%' }} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
