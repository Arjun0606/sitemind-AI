import Layout from '@/components/Layout'
import {
  CreditCard,
  Download,
  Check,
  Building2,
  Calendar,
  FileText,
  ArrowRight,
  Percent,
} from 'lucide-react'

const currentPlan = {
  sites: 12,
  pricePerSite: 425, // 15% discount for 6+ sites
  basePrice: 500,
  discount: 15,
  total: 5100,
  totalINR: 424575, // $5100 * 83.25
  billingDate: '2025-01-01',
  status: 'active',
}

const invoices = [
  { id: 'INV-2024-012', date: '2024-12-01', amount: 5100, status: 'paid' },
  { id: 'INV-2024-011', date: '2024-11-01', amount: 4500, status: 'paid' },
  { id: 'INV-2024-010', date: '2024-10-01', amount: 4500, status: 'paid' },
  { id: 'INV-2024-009', date: '2024-09-01', amount: 4000, status: 'paid' },
]

const pricingTiers = [
  { sites: '1-2', discount: 0, price: 500 },
  { sites: '3-5', discount: 10, price: 450 },
  { sites: '6-9', discount: 15, price: 425 },
  { sites: '10+', discount: 25, price: 375 },
]

export default function BillingPage() {
  return (
    <Layout companyName="ABC Developers">
      <div className="p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Billing</h1>
            <p className="text-slate-400">
              Manage your subscription and invoices
            </p>
          </div>
          <button className="px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white hover:bg-slate-800 transition-colors flex items-center gap-2">
            <CreditCard className="w-4 h-4" />
            Update Payment
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Current Plan */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-gradient-to-br from-primary-500/20 to-primary-600/5 border border-primary-500/20 rounded-xl p-6">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <p className="text-sm text-slate-400 mb-1">Current Plan</p>
                  <h2 className="text-2xl font-bold text-white">
                    {currentPlan.sites} Active Sites
                  </h2>
                </div>
                <span className="px-3 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full text-sm font-medium">
                  {currentPlan.status}
                </span>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-slate-900/50 rounded-lg p-4">
                  <p className="text-xs text-slate-400 mb-1">Base Price</p>
                  <p className="text-xl font-bold text-white">${currentPlan.basePrice}</p>
                  <p className="text-xs text-slate-400">per site</p>
                </div>
                <div className="bg-slate-900/50 rounded-lg p-4">
                  <p className="text-xs text-slate-400 mb-1">Your Discount</p>
                  <p className="text-xl font-bold text-emerald-400">{currentPlan.discount}%</p>
                  <p className="text-xs text-slate-400">volume discount</p>
                </div>
                <div className="bg-slate-900/50 rounded-lg p-4">
                  <p className="text-xs text-slate-400 mb-1">Your Price</p>
                  <p className="text-xl font-bold text-white">${currentPlan.pricePerSite}</p>
                  <p className="text-xs text-slate-400">per site</p>
                </div>
                <div className="bg-slate-900/50 rounded-lg p-4">
                  <p className="text-xs text-slate-400 mb-1">Monthly Total</p>
                  <p className="text-xl font-bold gradient-text">${currentPlan.total.toLocaleString()}</p>
                  <p className="text-xs text-slate-400">₹{currentPlan.totalINR.toLocaleString()}</p>
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-primary-500/20">
                <div className="flex items-center gap-2 text-sm text-slate-400">
                  <Calendar className="w-4 h-4" />
                  <span>Next billing: {new Date(currentPlan.billingDate).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}</span>
                </div>
                <button className="text-sm text-primary-500 hover:text-primary-400 font-medium flex items-center gap-1">
                  Add more sites <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* What's Included */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">What's Included</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {[
                  'UNLIMITED AI queries',
                  'Blueprint analysis & search',
                  'Change order tracking',
                  'RFI management',
                  'WhatsApp integration',
                  'Web dashboard access',
                  'Weekly & monthly reports',
                  'ROI tracking',
                  'Audit trail & citations',
                  'Priority support',
                  '24/7 availability',
                  'API access',
                ].map((feature) => (
                  <div key={feature} className="flex items-center gap-2">
                    <Check className="w-4 h-4 text-emerald-400" />
                    <span className="text-slate-300">{feature}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Invoices */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl">
              <div className="p-6 border-b border-slate-800">
                <h3 className="text-lg font-semibold text-white">Invoice History</h3>
              </div>
              <div className="divide-y divide-slate-800">
                {invoices.map((invoice) => (
                  <div key={invoice.id} className="p-4 flex items-center justify-between hover:bg-slate-800/50 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="p-2 bg-slate-800 rounded">
                        <FileText className="w-4 h-4 text-slate-400" />
                      </div>
                      <div>
                        <p className="font-medium text-white">{invoice.id}</p>
                        <p className="text-sm text-slate-400">
                          {new Date(invoice.date).toLocaleDateString('en-IN', { month: 'long', year: 'numeric' })}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="font-medium text-white">${invoice.amount.toLocaleString()}</span>
                      <span className="px-2 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded text-xs">
                        {invoice.status}
                      </span>
                      <button className="p-2 hover:bg-slate-800 rounded transition-colors">
                        <Download className="w-4 h-4 text-slate-400" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Pricing Tiers */}
          <div className="space-y-6">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Volume Pricing</h3>
              <div className="space-y-3">
                {pricingTiers.map((tier) => (
                  <div 
                    key={tier.sites}
                    className={`p-4 rounded-lg border ${
                      tier.price === currentPlan.pricePerSite
                        ? 'bg-primary-500/10 border-primary-500/30'
                        : 'bg-slate-800/50 border-slate-700'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Building2 className="w-4 h-4 text-slate-400" />
                        <span className="font-medium text-white">{tier.sites} sites</span>
                      </div>
                      {tier.discount > 0 && (
                        <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 rounded text-xs">
                          {tier.discount}% off
                        </span>
                      )}
                    </div>
                    <p className="text-2xl font-bold text-white">
                      ${tier.price}
                      <span className="text-sm font-normal text-slate-400">/site/mo</span>
                    </p>
                    {tier.price === currentPlan.pricePerSite && (
                      <p className="text-xs text-primary-400 mt-2">← Your current tier</p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Savings Calculator */}
            <div className="bg-gradient-to-br from-emerald-500/10 to-emerald-600/5 border border-emerald-500/20 rounded-xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <Percent className="w-5 h-5 text-emerald-400" />
                <h3 className="font-semibold text-white">Your Savings</h3>
              </div>
              <p className="text-3xl font-bold text-emerald-400 mb-2">
                ${(currentPlan.sites * currentPlan.basePrice - currentPlan.total).toLocaleString()}/mo
              </p>
              <p className="text-sm text-slate-400">
                You save ${(currentPlan.basePrice - currentPlan.pricePerSite)} per site with your {currentPlan.discount}% volume discount
              </p>
            </div>

            {/* Need Help */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h3 className="font-semibold text-white mb-2">Need Help?</h3>
              <p className="text-sm text-slate-400 mb-4">
                Contact us for custom enterprise pricing or questions about your subscription.
              </p>
              <button className="w-full px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors">
                Contact Support
              </button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}

