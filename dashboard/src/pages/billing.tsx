import Layout from '@/components/Layout'
import {
  CreditCard,
  Download,
  TrendingUp,
  Calendar,
  CheckCircle,
  AlertCircle,
} from 'lucide-react'

const mockUsage = {
  billing_cycle: '2024-12',
  plan: 'Enterprise',
  flat_fee: 1000,
  usage: {
    queries: 456,
    documents: 23,
    photos: 89,
    storage_gb: 2.3,
  },
  included: {
    queries: 1000,
    documents: 50,
    photos: 200,
    storage_gb: 10,
  },
  overages: {
    queries: 0,
    documents: 0,
    photos: 0,
    storage_gb: 0,
  },
  overage_charges: 0,
  total: 1000,
}

const invoices = [
  { id: 'INV-2024-12', date: 'Dec 2024', amount: 1000, status: 'current' },
  { id: 'INV-2024-11', date: 'Nov 2024', amount: 1050, status: 'paid' },
  { id: 'INV-2024-10', date: 'Oct 2024', amount: 1000, status: 'paid' },
]

export default function BillingPage() {
  const usage = mockUsage

  return (
    <Layout companyName="ABC Developers">
      <div className="p-6 lg:p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white mb-2">Billing & Usage</h1>
            <p className="text-slate-400">
              Billing cycle: {usage.billing_cycle}
            </p>
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors">
            <Download className="w-5 h-5" />
            Download Invoice
          </button>
        </div>

        {/* Current Bill */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-white mb-4">Current Bill</h2>
            
            <div className="space-y-4">
              {/* Flat Fee */}
              <div className="flex items-center justify-between py-3 border-b border-slate-800">
                <div>
                  <p className="text-white font-medium">Enterprise Plan</p>
                  <p className="text-slate-400 text-sm">Unlimited users & projects</p>
                </div>
                <p className="text-white font-bold">${usage.flat_fee}</p>
              </div>

              {/* Usage */}
              <div className="py-3 border-b border-slate-800">
                <p className="text-slate-400 text-sm mb-3">Usage (within limits)</p>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex justify-between">
                    <span className="text-slate-300">AI Queries</span>
                    <span className="text-slate-400">{usage.usage.queries} / {usage.included.queries}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-300">Documents</span>
                    <span className="text-slate-400">{usage.usage.documents} / {usage.included.documents}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-300">Photos</span>
                    <span className="text-slate-400">{usage.usage.photos} / {usage.included.photos}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-300">Storage</span>
                    <span className="text-slate-400">{usage.usage.storage_gb} / {usage.included.storage_gb} GB</span>
                  </div>
                </div>
              </div>

              {/* Overages */}
              {usage.overage_charges > 0 && (
                <div className="flex items-center justify-between py-3 border-b border-slate-800">
                  <div>
                    <p className="text-white font-medium">Overage Charges</p>
                    <p className="text-slate-400 text-sm">Usage above included limits</p>
                  </div>
                  <p className="text-orange-400 font-bold">+${usage.overage_charges}</p>
                </div>
              )}

              {/* Total */}
              <div className="flex items-center justify-between pt-3">
                <p className="text-lg font-semibold text-white">Total Due</p>
                <p className="text-2xl font-bold text-primary-400">${usage.total}</p>
              </div>
            </div>
          </div>

          {/* Plan Info */}
          <div className="bg-gradient-to-br from-primary-500/20 to-transparent border border-primary-500/30 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-primary-500/20 flex items-center justify-center">
                <CreditCard className="w-5 h-5 text-primary-400" />
              </div>
              <div>
                <p className="text-white font-semibold">Enterprise Plan</p>
                <p className="text-primary-400 text-sm">$1,000/month</p>
              </div>
            </div>

            <div className="space-y-2 mb-6">
              <div className="flex items-center gap-2 text-slate-300 text-sm">
                <CheckCircle className="w-4 h-4 text-green-400" />
                Unlimited users
              </div>
              <div className="flex items-center gap-2 text-slate-300 text-sm">
                <CheckCircle className="w-4 h-4 text-green-400" />
                Unlimited projects
              </div>
              <div className="flex items-center gap-2 text-slate-300 text-sm">
                <CheckCircle className="w-4 h-4 text-green-400" />
                1,000 AI queries/month
              </div>
              <div className="flex items-center gap-2 text-slate-300 text-sm">
                <CheckCircle className="w-4 h-4 text-green-400" />
                50 documents/month
              </div>
              <div className="flex items-center gap-2 text-slate-300 text-sm">
                <CheckCircle className="w-4 h-4 text-green-400" />
                10 GB storage
              </div>
            </div>

            <p className="text-slate-400 text-xs">
              Overages billed at: $0.15/query, $2.50/document, $0.50/photo, $2/GB
            </p>
          </div>
        </div>

        {/* Usage Progress */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 mb-8">
          <h2 className="text-lg font-semibold text-white mb-4">Usage This Month</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Queries */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-400">AI Queries</span>
                <span className="text-white">{Math.round(usage.usage.queries / usage.included.queries * 100)}%</span>
              </div>
              <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary-500 rounded-full transition-all"
                  style={{ width: `${usage.usage.queries / usage.included.queries * 100}%` }}
                />
              </div>
              <p className="text-slate-500 text-xs mt-1">{usage.usage.queries} of {usage.included.queries} used</p>
            </div>

            {/* Documents */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-400">Documents</span>
                <span className="text-white">{Math.round(usage.usage.documents / usage.included.documents * 100)}%</span>
              </div>
              <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-blue-500 rounded-full transition-all"
                  style={{ width: `${usage.usage.documents / usage.included.documents * 100}%` }}
                />
              </div>
              <p className="text-slate-500 text-xs mt-1">{usage.usage.documents} of {usage.included.documents} used</p>
            </div>

            {/* Photos */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-400">Photos</span>
                <span className="text-white">{Math.round(usage.usage.photos / usage.included.photos * 100)}%</span>
              </div>
              <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-purple-500 rounded-full transition-all"
                  style={{ width: `${usage.usage.photos / usage.included.photos * 100}%` }}
                />
              </div>
              <p className="text-slate-500 text-xs mt-1">{usage.usage.photos} of {usage.included.photos} used</p>
            </div>

            {/* Storage */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-400">Storage</span>
                <span className="text-white">{Math.round(usage.usage.storage_gb / usage.included.storage_gb * 100)}%</span>
              </div>
              <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-green-500 rounded-full transition-all"
                  style={{ width: `${usage.usage.storage_gb / usage.included.storage_gb * 100}%` }}
                />
              </div>
              <p className="text-slate-500 text-xs mt-1">{usage.usage.storage_gb} of {usage.included.storage_gb} GB used</p>
            </div>
          </div>
        </div>

        {/* Invoice History */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-slate-800">
            <h2 className="font-semibold text-white">Invoice History</h2>
          </div>
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="text-left p-4 text-slate-400 font-medium">Invoice</th>
                <th className="text-left p-4 text-slate-400 font-medium">Period</th>
                <th className="text-left p-4 text-slate-400 font-medium">Amount</th>
                <th className="text-left p-4 text-slate-400 font-medium">Status</th>
                <th className="text-right p-4 text-slate-400 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {invoices.map((invoice) => (
                <tr key={invoice.id} className="border-b border-slate-800/50">
                  <td className="p-4 text-white">{invoice.id}</td>
                  <td className="p-4 text-slate-400">{invoice.date}</td>
                  <td className="p-4 text-white">${invoice.amount}</td>
                  <td className="p-4">
                    {invoice.status === 'paid' ? (
                      <span className="flex items-center gap-1 text-green-400 text-sm">
                        <CheckCircle className="w-4 h-4" />
                        Paid
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-orange-400 text-sm">
                        <AlertCircle className="w-4 h-4" />
                        Current
                      </span>
                    )}
                  </td>
                  <td className="p-4 text-right">
                    <button className="text-primary-400 hover:text-primary-300 text-sm">
                      Download
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  )
}
