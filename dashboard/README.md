# SiteMind Dashboard

Web dashboard for builders, project managers, and management to monitor SiteMind usage, analytics, and ROI.

## 🎯 Who Uses This

| Role | Access Level | Key Features |
|------|--------------|--------------|
| **Site Engineers** | WhatsApp only | Real-time queries via WhatsApp |
| **Project Managers** | WhatsApp + Dashboard | Site reports, blueprints, team management |
| **Management** | Dashboard only | Analytics, ROI, billing, all sites |

## 📱 Features

### Overview Dashboard
- Real-time stats across all sites
- Recent query activity
- Alerts and notifications
- ROI summary

### Sites Management
- View all active sites
- Add/remove sites
- Per-site analytics
- Engineer assignment

### Analytics
- Query trends and patterns
- Usage by site/engineer
- Response time metrics
- ROI breakdown

### Reports
- Automated weekly/monthly reports
- Scheduled email delivery
- PDF export
- Custom report generation

### User Management
- Add site engineers (by phone number)
- Role-based access control
- Activity tracking
- Multi-site assignment

### Blueprints
- Upload and organize drawings
- Version control
- AI processing status
- Query tracking per document

### Audit Trail
- Complete decision history
- Change order tracking
- RFI management
- Legal export with citations

### Billing
- Subscription management
- Invoice history
- Volume discount visibility
- Payment methods

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
cd dashboard
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Production Build

```bash
npm run build
npm start
```

## 🔧 Configuration

Create `.env.local` from `.env.example`:

```bash
cp .env.example .env.local
```

Configure:
- `BACKEND_URL`: FastAPI backend URL
- `NEXTAUTH_URL`: Dashboard URL (for auth)
- `NEXTAUTH_SECRET`: Auth secret key

## 🎨 Tech Stack

- **Framework**: Next.js 14
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **State**: TanStack Query

## 📁 Structure

```
dashboard/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Next.js pages
│   ├── lib/            # Utilities and API client
│   └── styles/         # Global styles
├── public/             # Static assets
└── package.json
```

## 🔗 API Integration

Dashboard connects to the FastAPI backend:

```javascript
// All API calls are proxied through Next.js
// See next.config.js for rewrite rules
fetch('/api/sites')         // → backend/api/sites
fetch('/api/analytics')     // → backend/api/analytics
```

## 🎨 Design

- **Theme**: Dark mode with orange accents (construction theme)
- **Colors**: Slate backgrounds, orange primary, semantic colors
- **Typography**: Inter font family
- **Components**: Card-based, hover animations

## 📋 TODO

- [ ] Authentication (NextAuth.js)
- [ ] Real-time updates (WebSocket)
- [ ] Mobile responsive refinements
- [ ] Dark/light theme toggle
- [ ] PDF report generation
- [ ] Email notification settings

