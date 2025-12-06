import Layout from '@/components/Layout'
import {
  FolderOpen,
  Upload,
  Search,
  Filter,
  FileImage,
  Building2,
  Calendar,
  Download,
  Eye,
  Trash2,
  MoreVertical,
  FileText,
  Plus,
} from 'lucide-react'

const blueprints = [
  {
    id: 1,
    name: 'Structural Foundation Plan',
    filename: 'SK-001-Foundation.pdf',
    site: 'Skyline Towers',
    uploadedBy: 'Admin',
    uploadDate: '2024-11-15',
    version: 'v2.3',
    pages: 12,
    size: '4.5 MB',
    queries: 89,
    type: 'structural',
  },
  {
    id: 2,
    name: 'Floor Plan - Ground Floor',
    filename: 'AR-101-Ground.pdf',
    site: 'Skyline Towers',
    uploadedBy: 'Admin',
    uploadDate: '2024-11-14',
    version: 'v1.5',
    pages: 3,
    size: '2.1 MB',
    queries: 67,
    type: 'architectural',
  },
  {
    id: 3,
    name: 'MEP Services Layout',
    filename: 'MEP-001-Services.pdf',
    site: 'Green Valley',
    uploadedBy: 'Admin',
    uploadDate: '2024-11-10',
    version: 'v1.2',
    pages: 8,
    size: '3.2 MB',
    queries: 45,
    type: 'mep',
  },
  {
    id: 4,
    name: 'Beam Schedule',
    filename: 'SK-BS-001.pdf',
    site: 'Phoenix Mall',
    uploadedBy: 'Admin',
    uploadDate: '2024-11-08',
    version: 'v1.0',
    pages: 4,
    size: '1.8 MB',
    queries: 123,
    type: 'structural',
  },
  {
    id: 5,
    name: 'Column Schedule',
    filename: 'SK-CS-001.pdf',
    site: 'Phoenix Mall',
    uploadedBy: 'Admin',
    uploadDate: '2024-11-08',
    version: 'v1.1',
    pages: 6,
    size: '2.4 MB',
    queries: 98,
    type: 'structural',
  },
]

const typeColors = {
  structural: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  architectural: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  mep: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  electrical: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
}

export default function BlueprintsPage() {
  return (
    <Layout companyName="ABC Developers">
      <div className="p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Blueprints</h1>
            <p className="text-slate-400">
              Manage project drawings and documents
            </p>
          </div>
          <button className="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors flex items-center gap-2">
            <Upload className="w-4 h-4" />
            Upload Blueprints
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
            <div className="p-3 bg-blue-500/10 rounded-lg">
              <FileImage className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">67</p>
              <p className="text-sm text-slate-400">Total Blueprints</p>
            </div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
            <div className="p-3 bg-emerald-500/10 rounded-lg">
              <FolderOpen className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">12</p>
              <p className="text-sm text-slate-400">Sites Covered</p>
            </div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
            <div className="p-3 bg-purple-500/10 rounded-lg">
              <FileText className="w-5 h-5 text-purple-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">234</p>
              <p className="text-sm text-slate-400">Total Pages</p>
            </div>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center gap-4">
            <div className="p-3 bg-primary-500/10 rounded-lg">
              <Eye className="w-5 h-5 text-primary-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">1,847</p>
              <p className="text-sm text-slate-400">AI Queries</p>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search blueprints..."
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
            <option>All Types</option>
            <option>Structural</option>
            <option>Architectural</option>
            <option>MEP</option>
            <option>Electrical</option>
          </select>
          <button className="px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-slate-300 hover:bg-slate-800 transition-colors flex items-center gap-2">
            <Filter className="w-4 h-4" />
            Filters
          </button>
        </div>

        {/* Blueprints Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {blueprints.map((blueprint) => (
            <div
              key={blueprint.id}
              className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden hover:border-primary-500/50 transition-all card-hover group"
            >
              {/* Preview Area */}
              <div className="h-40 bg-slate-800 flex items-center justify-center relative">
                <FileImage className="w-16 h-16 text-slate-600" />
                <div className="absolute top-3 right-3">
                  <button className="p-2 bg-slate-900/80 hover:bg-slate-900 rounded-lg transition-colors">
                    <MoreVertical className="w-4 h-4 text-slate-400" />
                  </button>
                </div>
                <div className="absolute bottom-3 left-3">
                  <span className={`px-2 py-1 rounded text-xs font-medium border ${typeColors[blueprint.type as keyof typeof typeColors]}`}>
                    {blueprint.type}
                  </span>
                </div>
              </div>

              <div className="p-5">
                <h3 className="font-medium text-white mb-1 group-hover:text-primary-500 transition-colors">
                  {blueprint.name}
                </h3>
                <p className="text-sm text-slate-400 mb-3">{blueprint.filename}</p>

                <div className="flex items-center gap-4 text-sm text-slate-400 mb-4">
                  <span className="flex items-center gap-1">
                    <Building2 className="w-3.5 h-3.5" />
                    {blueprint.site}
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5" />
                    {new Date(blueprint.uploadDate).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })}
                  </span>
                </div>

                <div className="grid grid-cols-4 gap-2 text-center text-xs mb-4">
                  <div className="bg-slate-800/50 rounded p-2">
                    <p className="text-white font-medium">{blueprint.version}</p>
                    <p className="text-slate-500">version</p>
                  </div>
                  <div className="bg-slate-800/50 rounded p-2">
                    <p className="text-white font-medium">{blueprint.pages}</p>
                    <p className="text-slate-500">pages</p>
                  </div>
                  <div className="bg-slate-800/50 rounded p-2">
                    <p className="text-white font-medium">{blueprint.size}</p>
                    <p className="text-slate-500">size</p>
                  </div>
                  <div className="bg-slate-800/50 rounded p-2">
                    <p className="text-primary-400 font-medium">{blueprint.queries}</p>
                    <p className="text-slate-500">queries</p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button className="flex-1 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm transition-colors flex items-center justify-center gap-2">
                    <Eye className="w-4 h-4" />
                    View
                  </button>
                  <button className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm transition-colors">
                    <Download className="w-4 h-4" />
                  </button>
                  <button className="px-3 py-2 bg-slate-800 hover:bg-red-500/10 text-slate-400 hover:text-red-400 rounded-lg text-sm transition-colors">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}

          {/* Upload New Card */}
          <div className="bg-slate-900/50 border-2 border-dashed border-slate-700 rounded-xl p-6 hover:border-primary-500/50 hover:bg-slate-900 transition-all flex flex-col items-center justify-center min-h-[380px] cursor-pointer group">
            <div className="w-16 h-16 rounded-full bg-slate-800 group-hover:bg-primary-500/10 flex items-center justify-center mb-4 transition-colors">
              <Plus className="w-8 h-8 text-slate-400 group-hover:text-primary-500 transition-colors" />
            </div>
            <p className="text-lg font-medium text-slate-400 group-hover:text-white transition-colors">
              Upload Blueprint
            </p>
            <p className="text-sm text-slate-500 mt-1 text-center">
              PDF, PNG, or DWG files<br />
              Max 50MB per file
            </p>
          </div>
        </div>

        {/* AI Processing Notice */}
        <div className="mt-8 bg-gradient-to-br from-primary-500/10 to-primary-600/5 border border-primary-500/20 rounded-xl p-6">
          <h3 className="font-semibold text-white mb-2">🤖 AI Blueprint Processing</h3>
          <p className="text-slate-400 text-sm">
            When you upload blueprints, Gemini 2.5 Pro analyzes them to extract:
          </p>
          <ul className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-2 text-sm text-slate-300">
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-primary-500 rounded-full" />
              Dimensions & specifications
            </li>
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-primary-500 rounded-full" />
              Grid references & locations
            </li>
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-primary-500 rounded-full" />
              Material schedules
            </li>
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-primary-500 rounded-full" />
              Structural relationships
            </li>
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-primary-500 rounded-full" />
              Annotations & notes
            </li>
            <li className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-primary-500 rounded-full" />
              Revision history
            </li>
          </ul>
        </div>
      </div>
    </Layout>
  )
}

