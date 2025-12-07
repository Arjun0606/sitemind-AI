import { useState } from 'react';
import Head from 'next/head';
import Link from 'next/link';

// Mock data - in production, fetch from API
const MOCK_CUSTOMERS = [
  {
    id: 'org_abc123',
    name: 'ABC Builders Pvt Ltd',
    plan: 'pilot',
    status: 'active',
    sites: 3,
    users: 12,
    queries_this_month: 847,
    created_at: '2024-12-01',
    admin: { name: 'Rajesh Sharma', phone: '+919876543210' },
  },
  {
    id: 'org_def456',
    name: 'Prestige Developers',
    plan: 'standard',
    status: 'active',
    sites: 8,
    users: 34,
    queries_this_month: 2341,
    created_at: '2024-11-15',
    admin: { name: 'Priya Singh', phone: '+919876543211' },
  },
  {
    id: 'org_ghi789',
    name: 'Metro Construction',
    plan: 'pilot',
    status: 'active',
    sites: 2,
    users: 6,
    queries_this_month: 234,
    created_at: '2024-12-05',
    admin: { name: 'Amit Patel', phone: '+919876543212' },
  },
];

export default function CustomersPage() {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  const filteredCustomers = MOCK_CUSTOMERS.filter(c => {
    const matchesSearch = c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.admin.name.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === 'all' || c.plan === filter;
    return matchesSearch && matchesFilter;
  });

  return (
    <>
      <Head>
        <title>Customers | SiteMind Admin</title>
      </Head>

      <div className="min-h-screen bg-slate-950 text-white">
        {/* Header */}
        <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Link href="/admin" className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-400 rounded-lg flex items-center justify-center font-bold">
                SM
              </Link>
              <div>
                <h1 className="font-semibold">Customers</h1>
                <p className="text-sm text-slate-400">{MOCK_CUSTOMERS.length} organizations</p>
              </div>
            </div>
            <Link
              href="/admin/onboarding"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg font-medium transition-colors flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New Customer
            </Link>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-6 py-8">
          {/* Stats */}
          <div className="grid grid-cols-4 gap-4 mb-8">
            {[
              { label: 'Total Customers', value: MOCK_CUSTOMERS.length, color: 'blue' },
              { label: 'Active Sites', value: MOCK_CUSTOMERS.reduce((s, c) => s + c.sites, 0), color: 'green' },
              { label: 'Total Users', value: MOCK_CUSTOMERS.reduce((s, c) => s + c.users, 0), color: 'purple' },
              { label: 'Queries This Month', value: MOCK_CUSTOMERS.reduce((s, c) => s + c.queries_this_month, 0).toLocaleString(), color: 'amber' },
            ].map(stat => (
              <div key={stat.label} className="bg-slate-900 rounded-xl p-4">
                <div className="text-sm text-slate-400">{stat.label}</div>
                <div className={`text-2xl font-bold text-${stat.color}-400`}>{stat.value}</div>
              </div>
            ))}
          </div>

          {/* Filters */}
          <div className="flex items-center gap-4 mb-6">
            <div className="flex-1">
              <input
                type="text"
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Search customers..."
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <select
              value={filter}
              onChange={e => setFilter(e.target.value)}
              className="px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Plans</option>
              <option value="pilot">Pilot</option>
              <option value="standard">Standard</option>
              <option value="enterprise">Enterprise</option>
            </select>
          </div>

          {/* Customer List */}
          <div className="bg-slate-900 rounded-xl overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-800">
                  <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Company</th>
                  <th className="text-left px-6 py-4 text-sm font-medium text-slate-400">Admin</th>
                  <th className="text-center px-6 py-4 text-sm font-medium text-slate-400">Plan</th>
                  <th className="text-center px-6 py-4 text-sm font-medium text-slate-400">Sites</th>
                  <th className="text-center px-6 py-4 text-sm font-medium text-slate-400">Users</th>
                  <th className="text-center px-6 py-4 text-sm font-medium text-slate-400">Queries/Month</th>
                  <th className="text-right px-6 py-4 text-sm font-medium text-slate-400">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredCustomers.map(customer => (
                  <tr key={customer.id} className="border-b border-slate-800/50 hover:bg-slate-800/30">
                    <td className="px-6 py-4">
                      <div className="font-medium">{customer.name}</div>
                      <div className="text-sm text-slate-500">Since {customer.created_at}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div>{customer.admin.name}</div>
                      <div className="text-sm text-slate-500">{customer.admin.phone}</div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        customer.plan === 'pilot' ? 'bg-amber-500/20 text-amber-400' :
                        customer.plan === 'standard' ? 'bg-blue-500/20 text-blue-400' :
                        'bg-purple-500/20 text-purple-400'
                      }`}>
                        {customer.plan}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center font-medium">{customer.sites}</td>
                    <td className="px-6 py-4 text-center font-medium">{customer.users}</td>
                    <td className="px-6 py-4 text-center font-medium">{customer.queries_this_month.toLocaleString()}</td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          href={`/admin/customers/${customer.id}`}
                          className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm transition-colors"
                        >
                          View
                        </Link>
                        <Link
                          href={`/admin/customers/${customer.id}/config`}
                          className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm transition-colors"
                        >
                          Config
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </main>
      </div>
    </>
  );
}

