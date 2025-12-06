import React from 'react'
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react'

interface StatsCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: LucideIcon
  trend?: {
    value: number
    isPositive: boolean
  }
  color?: 'orange' | 'blue' | 'green' | 'purple'
}

const colorClasses = {
  orange: 'from-primary-500/20 to-primary-600/5 border-primary-500/20',
  blue: 'from-blue-500/20 to-blue-600/5 border-blue-500/20',
  green: 'from-emerald-500/20 to-emerald-600/5 border-emerald-500/20',
  purple: 'from-purple-500/20 to-purple-600/5 border-purple-500/20',
}

const iconColorClasses = {
  orange: 'bg-primary-500/20 text-primary-500',
  blue: 'bg-blue-500/20 text-blue-500',
  green: 'bg-emerald-500/20 text-emerald-500',
  purple: 'bg-purple-500/20 text-purple-500',
}

export default function StatsCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  color = 'orange',
}: StatsCardProps) {
  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} border rounded-xl p-6 card-hover`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-400 mb-1">{title}</p>
          <p className="text-3xl font-bold text-white">{value}</p>
          {subtitle && (
            <p className="text-sm text-slate-400 mt-1">{subtitle}</p>
          )}
          {trend && (
            <div className={`flex items-center gap-1 mt-2 text-sm ${
              trend.isPositive ? 'text-emerald-400' : 'text-red-400'
            }`}>
              {trend.isPositive ? (
                <TrendingUp className="w-4 h-4" />
              ) : (
                <TrendingDown className="w-4 h-4" />
              )}
              <span>{trend.value}% vs last month</span>
            </div>
          )}
        </div>
        <div className={`p-3 rounded-lg ${iconColorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  )
}

