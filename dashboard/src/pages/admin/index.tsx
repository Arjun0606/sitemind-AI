import Head from 'next/head';
import Link from 'next/link';

export default function AdminDashboard() {
  return (
    <>
      <Head>
        <title>Admin Dashboard | SiteMind</title>
      </Head>

      <div className="min-h-screen bg-slate-950 text-white">
        {/* Header */}
        <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-lg flex items-center justify-center font-bold">
                SM
              </div>
              <div>
                <h1 className="font-semibold">SiteMind Admin</h1>
                <p className="text-sm text-slate-400">Customer Management</p>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-6 py-12">
          {/* Quick Actions */}
          <h2 className="text-xl font-bold mb-6">Quick Actions</h2>
          <div className="grid grid-cols-3 gap-6 mb-12">
            <Link
              href="/admin/onboarding"
              className="bg-gradient-to-br from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 rounded-xl p-6 transition-all hover:scale-[1.02]"
            >
              <div className="w-12 h-12 bg-white/10 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-1">Onboard Customer</h3>
              <p className="text-sm text-blue-200">Set up a new customer in 5 minutes</p>
            </Link>

            <Link
              href="/admin/customers"
              className="bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-xl p-6 transition-all hover:scale-[1.02]"
            >
              <div className="w-12 h-12 bg-slate-700 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-1">View Customers</h3>
              <p className="text-sm text-slate-400">Manage existing organizations</p>
            </Link>

            <Link
              href="/admin/analytics"
              className="bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-xl p-6 transition-all hover:scale-[1.02]"
            >
              <div className="w-12 h-12 bg-slate-700 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-1">Analytics</h3>
              <p className="text-sm text-slate-400">Usage stats and insights</p>
            </Link>
          </div>

          {/* Stats Overview */}
          <h2 className="text-xl font-bold mb-6">Overview</h2>
          <div className="grid grid-cols-4 gap-4 mb-12">
            {[
              { label: 'Total Customers', value: '3', change: '+1 this week', positive: true },
              { label: 'Active Sites', value: '13', change: '+3 this week', positive: true },
              { label: 'Total Users', value: '52', change: '+8 this week', positive: true },
              { label: 'Queries Today', value: '847', change: '+12% vs avg', positive: true },
            ].map(stat => (
              <div key={stat.label} className="bg-slate-900 rounded-xl p-6">
                <div className="text-sm text-slate-400 mb-1">{stat.label}</div>
                <div className="text-3xl font-bold mb-2">{stat.value}</div>
                <div className={`text-sm ${stat.positive ? 'text-green-400' : 'text-red-400'}`}>
                  {stat.change}
                </div>
              </div>
            ))}
          </div>

          {/* Recent Activity */}
          <h2 className="text-xl font-bold mb-6">Recent Activity</h2>
          <div className="bg-slate-900 rounded-xl overflow-hidden">
            <div className="divide-y divide-slate-800">
              {[
                { action: 'New customer onboarded', customer: 'Metro Construction', time: '2 hours ago', icon: '🎉' },
                { action: 'Site added', customer: 'ABC Builders', time: '5 hours ago', icon: '🏗️' },
                { action: 'User added', customer: 'Prestige Developers', time: '1 day ago', icon: '👤' },
                { action: 'Config updated', customer: 'ABC Builders', time: '2 days ago', icon: '⚙️' },
                { action: 'Red flag detected', customer: 'Prestige Developers', time: '2 days ago', icon: '🚩' },
              ].map((activity, i) => (
                <div key={i} className="px-6 py-4 flex items-center gap-4 hover:bg-slate-800/50">
                  <span className="text-2xl">{activity.icon}</span>
                  <div className="flex-1">
                    <div className="font-medium">{activity.action}</div>
                    <div className="text-sm text-slate-400">{activity.customer}</div>
                  </div>
                  <div className="text-sm text-slate-500">{activity.time}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Links */}
          <div className="mt-12 grid grid-cols-4 gap-4">
            {[
              { label: 'Onboarding Cheatsheet', href: '/docs/cheatsheet', icon: '📋' },
              { label: 'Roles & Permissions', href: '/docs/roles', icon: '🔐' },
              { label: 'API Documentation', href: '/docs/api', icon: '📖' },
              { label: 'Support', href: '/support', icon: '💬' },
            ].map(link => (
              <Link
                key={link.label}
                href={link.href}
                className="bg-slate-900/50 hover:bg-slate-800 border border-slate-800 rounded-lg p-4 flex items-center gap-3 transition-colors"
              >
                <span className="text-xl">{link.icon}</span>
                <span className="text-sm">{link.label}</span>
              </Link>
            ))}
          </div>
        </main>
      </div>
    </>
  );
}

