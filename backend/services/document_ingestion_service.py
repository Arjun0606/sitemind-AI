"""
SiteMind Document Ingestion Service
====================================

THE KEY INSIGHT:
Customers dump EVERYTHING into SiteMind:
- Drawings (PDF, DWG, images)
- Specifications
- BOQs (Excel, PDF)
- Contracts
- Site photos
- WhatsApp history
- Emails
- Meeting notes

Then AI knows the ENTIRE project context.

EXAMPLE:
Customer dumps: Drawing STR-07 (structural slab details)
Later, engineer asks: "Rebar for slab S1?"
SiteMind: "12mm @ 150c/c as per Drawing STR-07, Page 3"

THIS IS THE MAGIC.
"""

from typing import Dict, Any, List, Optional, BinaryIO
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import base64
import json
import re

from utils.logger import logger
from services.memory_service import memory_service
from services.gemini_service import gemini_service
from config import settings

# Try to import PDF library
try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("PyMuPDF not installed. PDF extraction will use Gemini vision.")


class DocumentType(Enum):
    """Types of documents that can be ingested"""
    DRAWING = "drawing"           # Architectural, structural, MEP drawings
    SPECIFICATION = "specification"  # Project specs, material specs
    BOQ = "boq"                   # Bill of quantities
    CONTRACT = "contract"         # Contracts, work orders
    PHOTO = "photo"              # Site photos
    REPORT = "report"            # Test reports, inspection reports
    MEETING_NOTES = "meeting_notes"  # MOM, discussions
    EMAIL = "email"              # Project emails
    WHATSAPP = "whatsapp"        # WhatsApp chat history
    OTHER = "other"


@dataclass
class IngestedDocument:
    """A document that has been ingested into SiteMind"""
    id: str
    company_id: str
    project_id: str
    
    filename: str
    doc_type: DocumentType
    
    # Content
    extracted_text: str = ""
    summary: str = ""
    key_info: List[str] = None  # Key extracted information
    
    # Metadata
    page_count: int = 0
    uploaded_by: str = ""
    uploaded_at: datetime = None
    
    # Storage
    storage_url: str = ""  # Supabase storage URL
    memory_ids: List[str] = None  # Supermemory IDs for chunks
    
    def __post_init__(self):
        if not self.uploaded_at:
            self.uploaded_at = datetime.utcnow()
        if self.key_info is None:
            self.key_info = []
        if self.memory_ids is None:
            self.memory_ids = []


class DocumentIngestionService:
    """
    Service to ingest ALL project documents into SiteMind
    
    Process:
    1. Upload document (PDF, image, Excel, etc.)
    2. Extract text/content using appropriate method
    3. Use Gemini to understand and summarize
    4. Store in Supermemory for semantic search
    5. Now AI can answer questions about the document!
    """
    
    def __init__(self):
        self._documents: Dict[str, List[IngestedDocument]] = {}
        self._counter = 0
        
        # Chunk size for splitting large documents
        self.CHUNK_SIZE = 2000  # characters
        self.CHUNK_OVERLAP = 200
    
    async def ingest_document(
        self,
        company_id: str,
        project_id: str,
        filename: str,
        file_data: bytes,
        doc_type: DocumentType = None,
        uploaded_by: str = "",
        metadata: Dict = None,
    ) -> IngestedDocument:
        """
        Ingest a document into SiteMind
        
        Supports:
        - PDF (drawings, specs, contracts)
        - Images (PNG, JPG - drawings, photos)
        - Text files
        - Coming soon: Excel, Word, DWG
        """
        
        logger.info(f"📄 Ingesting: {filename}")
        
        # Generate ID
        self._counter += 1
        doc_id = f"DOC-{datetime.utcnow().strftime('%y%m%d')}-{self._counter:04d}"
        
        # Detect type if not provided
        if not doc_type:
            doc_type = self._detect_document_type(filename, metadata)
        
        # Extract content based on file type
        file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        if file_ext == 'pdf':
            extracted = await self._extract_from_pdf(file_data, filename, doc_type)
        elif file_ext in ['png', 'jpg', 'jpeg', 'webp']:
            extracted = await self._extract_from_image(file_data, filename, doc_type)
        elif file_ext in ['txt', 'md']:
            extracted = await self._extract_from_text(file_data.decode('utf-8'), filename)
        else:
            # Try to process as image (for unknown types)
            extracted = await self._extract_from_image(file_data, filename, doc_type)
        
        # Create document record
        doc = IngestedDocument(
            id=doc_id,
            company_id=company_id,
            project_id=project_id,
            filename=filename,
            doc_type=doc_type,
            extracted_text=extracted.get("text", ""),
            summary=extracted.get("summary", ""),
            key_info=extracted.get("key_info", []),
            page_count=extracted.get("page_count", 1),
            uploaded_by=uploaded_by,
        )
        
        # Store chunks in Supermemory
        memory_ids = await self._store_in_memory(
            company_id=company_id,
            project_id=project_id,
            doc=doc,
        )
        doc.memory_ids = memory_ids
        
        # Store document record
        key = f"{company_id}_{project_id}"
        if key not in self._documents:
            self._documents[key] = []
        self._documents[key].append(doc)
        
        logger.info(f"✅ Ingested {filename}: {len(memory_ids)} memory chunks created")
        
        return doc
    
    async def ingest_whatsapp_export(
        self,
        company_id: str,
        project_id: str,
        chat_export: str,
        uploaded_by: str = "",
    ) -> Dict[str, Any]:
        """
        Ingest WhatsApp chat export
        
        Format expected:
        [DD/MM/YY, HH:MM:SS] Name: Message
        or
        DD/MM/YY, HH:MM - Name: Message
        """
        
        logger.info(f"📱 Ingesting WhatsApp history...")
        
        # Parse WhatsApp export
        messages = self._parse_whatsapp_export(chat_export)
        
        logger.info(f"   Found {len(messages)} messages")
        
        # Store each message (with batching)
        stored = 0
        for msg in messages:
            try:
                content = f"{msg['sender']}: {msg['message']}"
                if msg.get('date'):
                    content = f"[{msg['date']}] {content}"
                
                await memory_service.add_memory(
                    company_id=company_id,
                    project_id=project_id,
                    content=content,
                    memory_type="whatsapp_history",
                    metadata={
                        "sender": msg.get("sender", ""),
                        "date": msg.get("date", ""),
                        "imported": True,
                    },
                    user_id=msg.get("sender", uploaded_by),
                )
                stored += 1
                
            except Exception as e:
                logger.error(f"Failed to store message: {e}")
        
        logger.info(f"✅ Imported {stored}/{len(messages)} WhatsApp messages")
        
        return {
            "total_messages": len(messages),
            "stored": stored,
            "status": "success",
        }
    
    def _parse_whatsapp_export(self, export: str) -> List[Dict]:
        """Parse WhatsApp chat export format"""
        
        messages = []
        
        # Pattern for WhatsApp export
        # [DD/MM/YY, HH:MM:SS] Name: Message
        # or: DD/MM/YY, HH:MM - Name: Message
        patterns = [
            r'\[(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?)\]\s+([^:]+):\s+(.+?)(?=\[|\Z)',
            r'(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2})\s+-\s+([^:]+):\s+(.+?)(?=\d{1,2}/\d{1,2}/|\Z)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, export, re.DOTALL)
            if matches:
                for match in matches:
                    date, time, sender, message = match
                    messages.append({
                        "date": f"{date} {time}",
                        "sender": sender.strip(),
                        "message": message.strip(),
                    })
                break
        
        # Fallback: line by line
        if not messages:
            lines = export.strip().split('\n')
            for line in lines:
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        messages.append({
                            "sender": parts[0].strip()[-20:],  # Last 20 chars as sender
                            "message": parts[1].strip(),
                        })
        
        return messages
    
    async def _extract_from_pdf(
        self,
        file_data: bytes,
        filename: str,
        doc_type: DocumentType,
    ) -> Dict[str, Any]:
        """Extract content from PDF"""
        
        text_content = ""
        page_count = 0
        
        # Try PyMuPDF first
        if PDF_AVAILABLE:
            try:
                doc = fitz.open(stream=file_data, filetype="pdf")
                page_count = len(doc)
                
                for page in doc:
                    text_content += page.get_text() + "\n\n"
                
                doc.close()
                
            except Exception as e:
                logger.error(f"PyMuPDF extraction failed: {e}")
        
        # If no text or it's a drawing (mostly images), use Gemini vision
        if not text_content.strip() or doc_type == DocumentType.DRAWING:
            logger.info("   Using Gemini vision for PDF analysis...")
            
            # For now, we'll use the first page as image
            # In production, would convert each page
            vision_result = await self._analyze_with_gemini(
                file_data=file_data,
                filename=filename,
                doc_type=doc_type,
                is_pdf=True,
            )
            
            if vision_result.get("text"):
                text_content = vision_result["text"]
            
            return {
                "text": text_content,
                "summary": vision_result.get("summary", ""),
                "key_info": vision_result.get("key_info", []),
                "page_count": page_count or 1,
            }
        
        # Got text, now summarize with Gemini
        summary_result = await self._summarize_with_gemini(
            text_content, filename, doc_type
        )
        
        return {
            "text": text_content,
            "summary": summary_result.get("summary", ""),
            "key_info": summary_result.get("key_info", []),
            "page_count": page_count,
        }
    
    async def _extract_from_image(
        self,
        file_data: bytes,
        filename: str,
        doc_type: DocumentType,
    ) -> Dict[str, Any]:
        """Extract content from image (drawing, photo)"""
        
        result = await self._analyze_with_gemini(
            file_data=file_data,
            filename=filename,
            doc_type=doc_type,
            is_pdf=False,
        )
        
        return {
            "text": result.get("text", ""),
            "summary": result.get("summary", ""),
            "key_info": result.get("key_info", []),
            "page_count": 1,
        }
    
    async def _extract_from_text(
        self,
        content: str,
        filename: str,
    ) -> Dict[str, Any]:
        """Extract from text file"""
        
        summary_result = await self._summarize_with_gemini(
            content, filename, DocumentType.OTHER
        )
        
        return {
            "text": content,
            "summary": summary_result.get("summary", ""),
            "key_info": summary_result.get("key_info", []),
            "page_count": 1,
        }
    
    async def _analyze_with_gemini(
        self,
        file_data: bytes,
        filename: str,
        doc_type: DocumentType,
        is_pdf: bool = False,
    ) -> Dict[str, Any]:
        """Use Gemini to analyze image/PDF"""
        
        # Build prompt based on document type
        if doc_type == DocumentType.DRAWING:
            prompt = """Analyze this construction drawing. Extract:

1. **Drawing Number/Title** - What is this drawing called?
2. **Type** - Structural, architectural, MEP, or other?
3. **Key Specifications** - Dimensions, grades, materials mentioned
4. **Components** - What elements are shown (columns, beams, slabs, etc.)?
5. **Notes** - Any important notes or specifications written on the drawing

Format your response as:
TITLE: [drawing title/number]
TYPE: [drawing type]
SPECIFICATIONS:
- [spec 1]
- [spec 2]
...
COMPONENTS:
- [component 1]: [details]
- [component 2]: [details]
...
NOTES:
- [note 1]
- [note 2]
..."""

        elif doc_type == DocumentType.PHOTO:
            prompt = """Analyze this construction site photo. Describe:

1. **What work is shown** - What construction activity is visible?
2. **Stage of work** - Is it foundation, structure, finishing, etc.?
3. **Materials visible** - What materials can you identify?
4. **Quality observations** - Any quality issues or good practices visible?
5. **Safety observations** - Any safety concerns?

Be specific and practical. This will be used for project documentation."""

        else:
            prompt = """Analyze this document and extract all important information.

Include:
1. Document title/purpose
2. Key specifications or details
3. Important dates, names, or references
4. Any numbers, measurements, or quantities
5. Key decisions or instructions

Format clearly with headers."""

        try:
            result = await gemini_service.analyze_image(
                image_data=file_data,
                prompt=prompt,
            )
            
            analysis = result.get("analysis", "")
            
            # Extract key info from analysis
            key_info = self._extract_key_info(analysis)
            
            return {
                "text": analysis,
                "summary": analysis[:500] if analysis else "",
                "key_info": key_info,
            }
            
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            return {"text": "", "summary": f"Analysis failed: {e}", "key_info": []}
    
    async def _summarize_with_gemini(
        self,
        text: str,
        filename: str,
        doc_type: DocumentType,
    ) -> Dict[str, Any]:
        """Use Gemini to summarize text content"""
        
        # Truncate if too long
        text_for_summary = text[:10000] if len(text) > 10000 else text
        
        prompt = f"""Summarize this construction document: {filename}

DOCUMENT CONTENT:
{text_for_summary}

---

Provide:
1. **Summary** (2-3 sentences) - What is this document about?
2. **Key Information** - List the most important specs, dimensions, decisions, or instructions.
3. **References** - Any drawing numbers, codes, or standards mentioned.

Format:
SUMMARY: [your summary]

KEY INFORMATION:
- [item 1]
- [item 2]
...

REFERENCES:
- [ref 1]
- [ref 2]
..."""

        try:
            result = await gemini_service._generate(prompt)
            
            # Extract key info
            key_info = self._extract_key_info(result)
            
            # Extract summary
            summary_match = re.search(r'SUMMARY:\s*(.+?)(?=KEY|REFERENCES|\Z)', result, re.DOTALL)
            summary = summary_match.group(1).strip() if summary_match else result[:300]
            
            return {
                "summary": summary,
                "key_info": key_info,
            }
            
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return {"summary": "", "key_info": []}
    
    def _extract_key_info(self, text: str) -> List[str]:
        """Extract key information points from text"""
        
        key_info = []
        
        # Look for list items
        list_patterns = [
            r'[-•]\s*(.+)',
            r'\d+\.\s*(.+)',
            r'[A-Z][A-Z\s]+:\s*(.+)',
        ]
        
        for pattern in list_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match.strip()) > 10:  # Meaningful content
                    key_info.append(match.strip()[:200])
        
        return key_info[:20]  # Max 20 items
    
    async def _store_in_memory(
        self,
        company_id: str,
        project_id: str,
        doc: IngestedDocument,
    ) -> List[str]:
        """Store document content in Supermemory as chunks"""
        
        memory_ids = []
        
        # Store summary as one memory
        if doc.summary:
            try:
                mem = await memory_service.add_memory(
                    company_id=company_id,
                    project_id=project_id,
                    content=f"[Document: {doc.filename}]\n\nSummary: {doc.summary}",
                    memory_type="document",
                    metadata={
                        "doc_id": doc.id,
                        "filename": doc.filename,
                        "doc_type": doc.doc_type.value,
                        "is_summary": True,
                    },
                    user_id=doc.uploaded_by,
                )
                memory_ids.append(mem.id)
            except Exception as e:
                logger.error(f"Failed to store summary: {e}")
        
        # Store key info as memories
        for info in doc.key_info[:10]:  # Max 10 key items
            try:
                mem = await memory_service.add_memory(
                    company_id=company_id,
                    project_id=project_id,
                    content=f"[Document: {doc.filename}]\n\n{info}",
                    memory_type="document",
                    metadata={
                        "doc_id": doc.id,
                        "filename": doc.filename,
                        "doc_type": doc.doc_type.value,
                        "is_key_info": True,
                    },
                    user_id=doc.uploaded_by,
                )
                memory_ids.append(mem.id)
            except Exception as e:
                logger.error(f"Failed to store key info: {e}")
        
        # Chunk and store full text if available
        if doc.extracted_text:
            chunks = self._chunk_text(doc.extracted_text)
            
            for i, chunk in enumerate(chunks[:20]):  # Max 20 chunks
                try:
                    mem = await memory_service.add_memory(
                        company_id=company_id,
                        project_id=project_id,
                        content=f"[Document: {doc.filename}, Part {i+1}]\n\n{chunk}",
                        memory_type="document",
                        metadata={
                            "doc_id": doc.id,
                            "filename": doc.filename,
                            "doc_type": doc.doc_type.value,
                            "chunk": i + 1,
                        },
                        user_id=doc.uploaded_by,
                    )
                    memory_ids.append(mem.id)
                except Exception as e:
                    logger.error(f"Failed to store chunk {i}: {e}")
        
        return memory_ids
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks for storage"""
        
        chunks = []
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) < self.CHUNK_SIZE:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _detect_document_type(self, filename: str, metadata: Dict = None) -> DocumentType:
        """Detect document type from filename"""
        
        filename_lower = filename.lower()
        
        # Check filename patterns
        if any(x in filename_lower for x in ['drawing', 'dwg', 'str-', 'arch-', 'mep-', 'plan']):
            return DocumentType.DRAWING
        elif any(x in filename_lower for x in ['spec', 'specification']):
            return DocumentType.SPECIFICATION
        elif any(x in filename_lower for x in ['boq', 'bill', 'quantity', 'estimate']):
            return DocumentType.BOQ
        elif any(x in filename_lower for x in ['contract', 'agreement', 'work order', 'wo-']):
            return DocumentType.CONTRACT
        elif any(x in filename_lower for x in ['report', 'test', 'inspection']):
            return DocumentType.REPORT
        elif any(x in filename_lower for x in ['mom', 'meeting', 'minutes']):
            return DocumentType.MEETING_NOTES
        elif filename_lower.endswith(('.png', '.jpg', '.jpeg')):
            return DocumentType.PHOTO
        
        return DocumentType.OTHER
    
    def get_documents(self, company_id: str, project_id: str) -> List[IngestedDocument]:
        """Get all documents for a project"""
        key = f"{company_id}_{project_id}"
        return self._documents.get(key, [])


# Singleton
document_ingestion_service = DocumentIngestionService()

