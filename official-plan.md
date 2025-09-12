# cramCortex - Official Project Plan
## AI-Powered Test Structure Analyzer

---
ALWAYS USE GIT BEST PRACTICES !************

## 1. Executive Summary

**Project Vision**: Transform passive test review into active, structured preparation through AI-powered test analysis and intelligent study modes.

**Core Value Proposition**: Upload any past exam and receive comprehensive analysis including question categorization, topic clustering, and targeted study recommendations - enabling methodical preparation instead of random review.

**Target Users**: Students, educators, tutoring centers, and educational institutions seeking data-driven test preparation strategies.

---

## 2. Product Overview

### 2.1 Core Functionality
- **Document Processing**: Support PDF, DOCX, and image formats with OCR capabilities
- **AI Analysis**: Automated question identification, classification, and semantic clustering
- **Interactive Dashboard**: Visual analytics showing test composition and question patterns
- **Study Modes**: Targeted practice sessions by question type, topic, or difficulty level
- **Progress Tracking**: Performance analytics and learning recommendations

### 2.2 Key Differentiators
- Hybrid AI approach balancing accuracy and cost
- Real-time processing with WebSocket updates
- Collaborative study features
- Progressive Web App for cross-platform access
- Privacy-first architecture with local processing options

---

## 3. Technical Architecture

### 3.1 Frontend Stack
**Framework**: React 18 with Vite
**Language**: TypeScript for type safety
**Styling**: Tailwind CSS with custom design system
**State Management**: Zustand for lightweight state management
**Key Libraries**:
- `@tanstack/react-query` for server state management
- `react-router-dom` for routing
- `recharts` for data visualization
- `react-dropzone` for file uploads
- `socket.io-client` for real-time updates

### 3.2 Backend Stack
**Framework**: FastAPI with async support
**Language**: Python 3.11+
**Authentication**: JWT with refresh token rotation
**Key Libraries**:
- `pydantic` for data validation
- `sqlalchemy` for ORM
- `alembic` for database migrations
- `celery` for background task processing
- `redis` for caching and task queue
- `socketio` for real-time communication

### 3.3 AI/ML Pipeline
**Question Classification**:
- Primary: OpenAI GPT-4 with structured prompts
- Fallback: Fine-tuned BERT model for cost optimization

**Question Clustering**:
- Embedding Model: `sentence-transformers/all-MiniLM-L6-v2`
- Clustering: HDBSCAN for adaptive cluster detection
- Topic Modeling: BERTopic for theme extraction

**Document Processing**:
- `unstructured` for multi-format document parsing
- `pytesseract` for OCR capabilities
- Custom preprocessing pipeline for noise reduction

### 3.4 Database Design
**Development**: SQLite with full-text search
**Production**: PostgreSQL 15+ with pgvector extension
**Caching**: Redis for session data and processed results
**File Storage**: Local filesystem (dev) → AWS S3 (prod)

### 3.5 Infrastructure
**Containerization**: Docker with multi-stage builds
**Orchestration**: Docker Compose (dev) → Kubernetes (prod)
**Monitoring**: Prometheus + Grafana
**Logging**: Structured logging with ELK stack
**CI/CD**: GitHub Actions with automated testing and deployment

---

## 4. Security & Privacy

### 4.1 Data Protection
- End-to-end encryption for document uploads
- Automatic document deletion after processing (configurable)
- GDPR compliance with data export/deletion capabilities
- No persistent storage of document content (metadata only)

### 4.2 Authentication & Authorization
- OAuth2 with JWT access/refresh tokens
- Role-based access control (Student, Educator, Admin)
- API rate limiting and DDoS protection
- Input validation and sanitization

### 4.3 Infrastructure Security
- HTTPS enforcement with HSTS headers
- Security headers (CSP, CORS, etc.)
- Regular dependency updates and vulnerability scanning
- Secrets management with environment-specific configs

---

## 5. User Experience & Interface

### 5.1 Core User Flows
1. **Document Upload**: Drag-and-drop with real-time processing status
2. **Analysis Dashboard**: Interactive visualizations of test composition
3. **Study Mode**: Adaptive question presentation based on performance
4. **Progress Tracking**: Historical performance and improvement metrics

### 5.2 Responsive Design
- Mobile-first approach with progressive enhancement
- Touch-friendly interactions for mobile study sessions
- Offline capability through PWA features
- Dark/light mode support

### 5.3 Accessibility
- WCAG 2.1 AA compliance
- Screen reader optimization
- Keyboard navigation support
- Color contrast validation

---



## 9. Risk Assessment & Mitigation

### 9.1 Technical Risks
- **AI API Costs**: Implement smart caching and local fallback models
- **Scalability**: Design for horizontal scaling from day one
- **Data Privacy**: Implement privacy-by-design principles

### 9.2 Business Risks
- **Market Competition**: Focus on unique AI clustering capabilities
- **User Adoption**: Extensive user testing and iterative design
- **Regulatory Changes**: Build compliance framework early

---


---

*Document Version: 1.0*  
*Last Updated: September 12, 2025*  
*Next Review: October 12, 2025*