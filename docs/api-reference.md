# SiteMind API Reference

## Base URL

- **Development:** `http://localhost:8000`
- **Production:** `https://api.sitemind.ai`

## Authentication

Currently, the API uses WhatsApp phone number validation. Admin endpoints will require API key authentication in production.

---

## Health Endpoints

### GET /
Root endpoint returning service information.

**Response:**
```json
{
  "service": "SiteMind API",
  "version": "1.0.0",
  "status": "running",
  "tagline": "The AI Site Engineer - Fleetline for Construction",
  "docs": "/docs"
}
```

### GET /health
Comprehensive health check of all services.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "gemini": {"status": "healthy", "model": "gemini-2.0-flash"},
    "whisper": {"status": "healthy", "model": "whisper-1"},
    "whatsapp": {"status": "healthy"},
    "memory": {"status": "healthy"},
    "storage": {"status": "healthy"}
  }
}
```

### GET /ping
Simple uptime check.

**Response:**
```json
{"pong": true}
```

---

## WhatsApp Endpoints

### POST /whatsapp/webhook
Main webhook endpoint for incoming WhatsApp messages.

**Form Parameters (from Twilio):**
- `MessageSid` (string): Twilio message SID
- `From` (string): Sender phone (e.g., "whatsapp:+919876543210")
- `To` (string): Recipient (SiteMind number)
- `Body` (string): Message text
- `NumMedia` (string): Number of media attachments
- `MediaUrl0` (string, optional): URL of first media file
- `MediaContentType0` (string, optional): MIME type of media

**Response:** Empty TwiML (message sent via API)

### POST /whatsapp/status
Callback for message delivery status.

---

## Admin Endpoints

### Builders

#### POST /admin/builders
Create a new builder/client.

**Request Body:**
```json
{
  "name": "ABC Developers",
  "contact_person": "John Doe",
  "contact_email": "john@abc.com",
  "contact_phone": "+919876543210",
  "address": "Hyderabad, India",
  "monthly_fee": 500
}
```

#### GET /admin/builders
List all builders.

**Query Parameters:**
- `skip` (int): Offset for pagination (default: 0)
- `limit` (int): Max results (default: 50, max: 100)

#### GET /admin/builders/{builder_id}
Get a specific builder.

#### PATCH /admin/builders/{builder_id}
Update a builder.

---

### Projects

#### POST /admin/projects
Create a new project/site.

**Request Body:**
```json
{
  "builder_id": "uuid",
  "name": "Skyline Towers Block A",
  "description": "15-floor commercial building",
  "location": "Banjara Hills, Hyderabad",
  "whatsapp_number": "+919876543210",
  "project_value": 100.5
}
```

#### GET /admin/projects
List all projects.

**Query Parameters:**
- `builder_id` (uuid, optional): Filter by builder
- `status` (string, optional): Filter by status
- `skip` (int): Offset
- `limit` (int): Max results

#### GET /admin/projects/{project_id}
Get a specific project with details.

#### PATCH /admin/projects/{project_id}
Update a project.

---

### Blueprints

#### POST /admin/projects/{project_id}/blueprints
Upload a blueprint PDF.

**Form Parameters:**
- `file` (file): PDF file to upload
- `category` (string): Category (architectural, structural, mep, etc.)
- `revision` (string, optional): Revision number
- `drawing_number` (string, optional): Drawing reference

**Response:**
```json
{
  "id": "uuid",
  "filename": "floor-plan.pdf",
  "file_url": "https://s3.amazonaws.com/...",
  "category": "architectural",
  "is_processed": true,
  "uploaded_at": "2025-12-06T10:00:00Z"
}
```

#### GET /admin/projects/{project_id}/blueprints
List blueprints for a project.

#### DELETE /admin/blueprints/{blueprint_id}
Delete a blueprint.

---

### Site Engineers

#### POST /admin/projects/{project_id}/engineers
Add a site engineer.

**Request Body:**
```json
{
  "project_id": "uuid",
  "name": "Rajesh Kumar",
  "phone_number": "+919876543210",
  "role": "Site Engineer"
}
```

**Query Parameters:**
- `send_welcome` (bool): Send welcome message (default: true)

#### GET /admin/projects/{project_id}/engineers
List engineers for a project.

#### DELETE /admin/engineers/{engineer_id}
Deactivate an engineer.

---

### Memory

#### POST /admin/projects/{project_id}/memory
Add a memory to project knowledge base.

**Form Parameters:**
- `content` (string): Memory content
- `doc_type` (string): Type (rfi, change_order, meeting_notes, note)
- `drawing` (string, optional): Related drawing reference

#### GET /admin/projects/{project_id}/memory
Get all memories for a project.

#### GET /admin/projects/{project_id}/memory/search
Search project memory.

**Query Parameters:**
- `query` (string): Search query
- `limit` (int): Max results (default: 5)

---

## Analytics Endpoints

### GET /analytics/dashboard
Get overall dashboard statistics.

**Response:**
```json
{
  "total_builders": 10,
  "total_projects": 45,
  "active_projects": 38,
  "total_queries_today": 245,
  "total_queries_month": 5420,
  "total_revenue": 22500,
  "avg_response_time_ms": 6500
}
```

### GET /analytics/projects/{project_id}
Get project-specific analytics.

### GET /analytics/projects/{project_id}/chats
Get chat history for a project.

**Query Parameters:**
- `skip` (int): Offset
- `limit` (int): Max results
- `user_phone` (string, optional): Filter by user

### GET /analytics/usage/daily
Get daily usage statistics.

**Query Parameters:**
- `days` (int): Number of days (default: 30)
- `project_id` (uuid, optional): Filter by project

### GET /analytics/usage/by-type
Get usage breakdown by message type.

### POST /analytics/feedback/{chat_log_id}
Submit feedback for a response.

**Query Parameters:**
- `rating` (int): 1-5 rating
- `comment` (string, optional): Feedback text

---

## Error Responses

All errors return JSON with this format:

```json
{
  "detail": "Error message here"
}
```

Common status codes:
- `400`: Bad request / validation error
- `404`: Resource not found
- `500`: Internal server error

