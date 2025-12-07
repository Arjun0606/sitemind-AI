import { useState } from 'react';
import Layout from '../components/Layout';

interface Project {
  name: string;
  stage: 'planning' | 'active' | 'finishing' | 'handover' | 'archived';
  queries: number;
  documents: number;
  storageGb: number;
  photos: number;
}

// Pricing constants (mirror backend)
const PRICING = {
  perSeat: 75,
  includedSeats: 5,
  projectBase: {
    planning: 300,
    active: 750,
    finishing: 750,
    handover: 400,
    archived: 150,
  },
  includedQueries: 500,
  perQuery: 0.10,
  includedDocuments: 20,
  perDocument: 2.00,
  includedStorageGb: 5,
  perGb: 1.00,
  includedPhotos: 100,
  perPhoto: 0.25,
  volumeDiscounts: [
    { threshold: 30000, discount: 0.20 },
    { threshold: 15000, discount: 0.15 },
    { threshold: 7500, discount: 0.10 },
    { threshold: 3000, discount: 0.05 },
  ],
  annualDiscount: 0.17,
  usdToInr: 83,
};

export default function PricingCalculator() {
  const [users, setUsers] = useState(15);
  const [projects, setProjects] = useState<Project[]>([
    { name: 'Project 1', stage: 'active', queries: 500, documents: 20, storageGb: 5, photos: 100 },
  ]);

  const addProject = () => {
    setProjects([
      ...projects,
      { name: `Project ${projects.length + 1}`, stage: 'active', queries: 500, documents: 20, storageGb: 5, photos: 100 },
    ]);
  };

  const removeProject = (index: number) => {
    setProjects(projects.filter((_, i) => i !== index));
  };

  const updateProject = (index: number, field: keyof Project, value: any) => {
    const updated = [...projects];
    updated[index] = { ...updated[index], [field]: value };
    setProjects(updated);
  };

  // Calculate pricing
  const calculateProjectCost = (project: Project) => {
    const base = PRICING.projectBase[project.stage];
    
    const queryOverage = Math.max(0, project.queries - PRICING.includedQueries);
    const queryCost = queryOverage * PRICING.perQuery;
    
    const docOverage = Math.max(0, project.documents - PRICING.includedDocuments);
    const docCost = docOverage * PRICING.perDocument;
    
    const storageOverage = Math.max(0, project.storageGb - PRICING.includedStorageGb);
    const storageCost = storageOverage * PRICING.perGb;
    
    const photoOverage = Math.max(0, project.photos - PRICING.includedPhotos);
    const photoCost = photoOverage * PRICING.perPhoto;
    
    return {
      base,
      queryCost,
      docCost,
      storageCost,
      photoCost,
      total: base + queryCost + docCost + storageCost + photoCost,
    };
  };

  const billableSeats = Math.max(0, users - PRICING.includedSeats);
  const seatsCost = billableSeats * PRICING.perSeat;
  
  const projectCosts = projects.map(calculateProjectCost);
  const projectsTotal = projectCosts.reduce((sum, p) => sum + p.total, 0);
  
  const subtotal = seatsCost + projectsTotal;
  
  // Volume discount
  let volumeDiscountPercent = 0;
  for (const { threshold, discount } of PRICING.volumeDiscounts) {
    if (subtotal >= threshold) {
      volumeDiscountPercent = discount * 100;
      break;
    }
  }
  const volumeDiscount = subtotal * (volumeDiscountPercent / 100);
  
  const monthlyUsd = subtotal - volumeDiscount;
  const monthlyInr = monthlyUsd * PRICING.usdToInr;
  const annualUsd = monthlyUsd * 12 * (1 - PRICING.annualDiscount);

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Pricing Calculator</h1>
        <p className="text-slate-400 mb-8">Calculate your custom SiteMind pricing based on team size and usage</p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Section */}
          <div className="space-y-6">
            {/* Team Size */}
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <span className="text-2xl">👥</span> Team Size
              </h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-slate-400 mb-2">
                    Total unique users (across all projects)
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="200"
                    value={users}
                    onChange={(e) => setUsers(Number(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-sm mt-1">
                    <span className="text-slate-500">1</span>
                    <span className="text-xl font-bold text-blue-400">{users} users</span>
                    <span className="text-slate-500">200</span>
                  </div>
                </div>
                
                <div className="text-sm text-slate-400">
                  <span className="text-green-400">✓ First {PRICING.includedSeats} users included</span>
                  <br />
                  {billableSeats > 0 && (
                    <span>+ {billableSeats} additional × ${PRICING.perSeat} = ${seatsCost}</span>
                  )}
                </div>
              </div>
            </div>

            {/* Projects */}
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold flex items-center gap-2">
                  <span className="text-2xl">🏗️</span> Projects
                </h2>
                <button
                  onClick={addProject}
                  className="px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm"
                >
                  + Add Project
                </button>
              </div>

              <div className="space-y-4">
                {projects.map((project, index) => (
                  <div key={index} className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                    <div className="flex justify-between items-start mb-3">
                      <input
                        type="text"
                        value={project.name}
                        onChange={(e) => updateProject(index, 'name', e.target.value)}
                        className="bg-transparent border-b border-slate-600 focus:border-blue-500 outline-none text-lg font-medium"
                      />
                      {projects.length > 1 && (
                        <button
                          onClick={() => removeProject(index)}
                          className="text-slate-500 hover:text-red-400"
                        >
                          ✕
                        </button>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <label className="text-slate-400">Stage</label>
                        <select
                          value={project.stage}
                          onChange={(e) => updateProject(index, 'stage', e.target.value)}
                          className="w-full mt-1 bg-slate-800 border border-slate-600 rounded px-2 py-1"
                        >
                          <option value="planning">Planning ($300)</option>
                          <option value="active">Active ($750)</option>
                          <option value="finishing">Finishing ($750)</option>
                          <option value="handover">Handover ($400)</option>
                          <option value="archived">Archived ($150)</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="text-slate-400">Queries/mo</label>
                        <input
                          type="number"
                          value={project.queries}
                          onChange={(e) => updateProject(index, 'queries', Number(e.target.value))}
                          className="w-full mt-1 bg-slate-800 border border-slate-600 rounded px-2 py-1"
                        />
                      </div>
                      
                      <div>
                        <label className="text-slate-400">Documents</label>
                        <input
                          type="number"
                          value={project.documents}
                          onChange={(e) => updateProject(index, 'documents', Number(e.target.value))}
                          className="w-full mt-1 bg-slate-800 border border-slate-600 rounded px-2 py-1"
                        />
                      </div>
                      
                      <div>
                        <label className="text-slate-400">Storage (GB)</label>
                        <input
                          type="number"
                          value={project.storageGb}
                          onChange={(e) => updateProject(index, 'storageGb', Number(e.target.value))}
                          className="w-full mt-1 bg-slate-800 border border-slate-600 rounded px-2 py-1"
                        />
                      </div>
                      
                      <div>
                        <label className="text-slate-400">Photos</label>
                        <input
                          type="number"
                          value={project.photos}
                          onChange={(e) => updateProject(index, 'photos', Number(e.target.value))}
                          className="w-full mt-1 bg-slate-800 border border-slate-600 rounded px-2 py-1"
                        />
                      </div>
                      
                      <div className="flex items-end">
                        <span className="text-lg font-bold text-blue-400">
                          ${projectCosts[index]?.total.toFixed(0)}/mo
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Summary Section */}
          <div className="space-y-6">
            {/* Total */}
            <div className="bg-gradient-to-br from-blue-900/50 to-purple-900/50 rounded-xl p-6 border border-blue-700/50">
              <h2 className="text-xl font-semibold mb-4">Your Price</h2>
              
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-slate-300">Team ({users} users)</span>
                  <span>${seatsCost.toFixed(0)}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-slate-300">Projects ({projects.length})</span>
                  <span>${projectsTotal.toFixed(0)}</span>
                </div>
                
                <div className="border-t border-slate-600 pt-2 flex justify-between">
                  <span className="text-slate-300">Subtotal</span>
                  <span>${subtotal.toFixed(0)}</span>
                </div>
                
                {volumeDiscountPercent > 0 && (
                  <div className="flex justify-between text-green-400">
                    <span>Volume discount ({volumeDiscountPercent}%)</span>
                    <span>-${volumeDiscount.toFixed(0)}</span>
                  </div>
                )}
                
                <div className="border-t border-slate-600 pt-3">
                  <div className="flex justify-between text-2xl font-bold">
                    <span>Monthly</span>
                    <span className="text-blue-400">${monthlyUsd.toLocaleString()}</span>
                  </div>
                  <div className="text-right text-slate-400">
                    ₹{monthlyInr.toLocaleString()}
                  </div>
                </div>
                
                <div className="bg-green-900/30 rounded-lg p-3 mt-4">
                  <div className="flex justify-between">
                    <span className="text-green-400">Annual (save 17%)</span>
                    <span className="text-green-400 font-bold">${annualUsd.toLocaleString()}</span>
                  </div>
                  <div className="text-right text-slate-400 text-sm">
                    ₹{(annualUsd * PRICING.usdToInr).toLocaleString()}
                  </div>
                </div>
              </div>
            </div>

            {/* Breakdown */}
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h2 className="text-xl font-semibold mb-4">Breakdown</h2>
              
              <div className="space-y-4 text-sm">
                <div>
                  <h3 className="font-medium text-slate-300 mb-2">👥 Seats</h3>
                  <div className="text-slate-400">
                    {PRICING.includedSeats} included + {billableSeats} × ${PRICING.perSeat} = ${seatsCost}
                  </div>
                </div>
                
                {projects.map((project, index) => {
                  const cost = projectCosts[index];
                  return (
                    <div key={index}>
                      <h3 className="font-medium text-slate-300 mb-2">🏗️ {project.name}</h3>
                      <div className="text-slate-400 space-y-1">
                        <div>Base ({project.stage}): ${cost.base}</div>
                        {cost.queryCost > 0 && <div>Query overage: ${cost.queryCost.toFixed(0)}</div>}
                        {cost.docCost > 0 && <div>Document overage: ${cost.docCost.toFixed(0)}</div>}
                        {cost.storageCost > 0 && <div>Storage overage: ${cost.storageCost.toFixed(0)}</div>}
                        {cost.photoCost > 0 && <div>Photo overage: ${cost.photoCost.toFixed(0)}</div>}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Included */}
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h2 className="text-xl font-semibold mb-4">What's Included</h2>
              
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="text-slate-400">✓ {PRICING.includedSeats} users included</div>
                <div className="text-slate-400">✓ {PRICING.includedQueries} queries/project</div>
                <div className="text-slate-400">✓ {PRICING.includedDocuments} documents/project</div>
                <div className="text-slate-400">✓ {PRICING.includedStorageGb} GB storage/project</div>
                <div className="text-slate-400">✓ {PRICING.includedPhotos} photos/project</div>
                <div className="text-slate-400">✓ 24/7 WhatsApp support</div>
                <div className="text-slate-400">✓ Complete audit trail</div>
                <div className="text-slate-400">✓ Personal onboarding</div>
              </div>
            </div>

            {/* CTA */}
            <button className="w-full py-4 bg-blue-600 hover:bg-blue-700 rounded-xl text-lg font-semibold transition-colors">
              Get Custom Quote →
            </button>
          </div>
        </div>

        {/* Quick Examples */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold mb-6">Quick Examples</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[
              { name: 'Small', users: 12, projects: 1, price: '~$1,200' },
              { name: 'Medium', users: 30, projects: 3, price: '~$3,800' },
              { name: 'Large', users: 65, projects: 6, price: '~$8,500' },
              { name: 'Enterprise', users: 120, projects: 8, price: '~$18,000' },
            ].map((example) => (
              <div
                key={example.name}
                className="bg-slate-800/50 rounded-xl p-4 border border-slate-700 cursor-pointer hover:border-blue-500 transition-colors"
                onClick={() => {
                  setUsers(example.users);
                  // Set appropriate projects
                }}
              >
                <h3 className="font-semibold text-lg">{example.name}</h3>
                <div className="text-slate-400 text-sm">
                  {example.users} users, {example.projects} projects
                </div>
                <div className="text-blue-400 font-bold mt-2">{example.price}/mo</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}

