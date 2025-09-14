# cramCortex 🧠
## AI-Powered Test Structure Analyzer

**Transform passive test review into active, structured preparation through AI-powered test analysis and intelligent study modes.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

---

## 🎯 **Overview**

cramCortex is an intelligent test analysis platform that automatically processes exam documents, identifies questions, categorizes content, and provides structured study recommendations. Upload any past exam and receive comprehensive analysis including question categorization, topic clustering, and targeted study modes.

### **Key Features**

🔍 **Smart Document Processing**
- Multi-format support (PDF, DOCX, images with OCR)
- AI-powered question identification and extraction
- Intelligent text preprocessing and noise reduction

🌐 **Advanced Translation System**
- Hebrew-to-English translation with chunked processing
- Force-validated English output (no Hebrew characters remain)
- Context-aware translation for educational content

🧠 **AI-Powered Analysis**
- Automated question classification and difficulty assessment
- Semantic clustering of related topics
- Comprehensive topic extraction and categorization

📊 **Interactive Analytics**
- Visual test composition analysis
- Question pattern identification
- Performance tracking and recommendations

🎓 **Adaptive Study Modes**
- Targeted practice by question type or topic
- Difficulty-based progression
- Personalized learning recommendations

---

## 🏗️ **Architecture**

### **Frontend**
- **React 18** with TypeScript and Vite
- **Tailwind CSS** for styling with custom design system
- **Zustand** for lightweight state management
- **React Query** for server state management
- **Progressive Web App** capabilities

### **Backend**
- **FastAPI** with async support and automatic API documentation
- **Python 3.11+** with modern async/await patterns
- **OpenAI GPT integration** for intelligent analysis
- **SQLite** (dev) / **PostgreSQL** (prod) database
- **Redis** for caching and session management

### **AI/ML Pipeline**
- **Question Classification**: OpenAI GPT-4 with structured prompts
- **Text Embedding**: sentence-transformers for semantic analysis
- **Document Processing**: unstructured library with OCR support
- **Translation**: Custom Hebrew-to-English system with validation

---

## 🚀 **Quick Start**

### **Prerequisites**
```bash
# Required software
- Python 3.11+
- Node.js 18+
- Git
```

### **1. Clone Repository**
```bash
git clone https://github.com/davebruzil/cramCortex.git
cd cramCortex
```

### **2. Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your OpenAI API key and other settings

# Run database migrations
alembic upgrade head

# Start the backend server
python run.py
```

Backend will be available at: `http://localhost:8000`

### **3. Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

---

## 🔧 **Configuration**

### **Environment Variables**

Create `.env` file in the backend directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.1

# Database
DATABASE_URL=sqlite:///./cramcortex.db

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=cramCortex
DEBUG=True
```

### **API Documentation**

With the backend running, visit:
- **Interactive Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 📋 **API Endpoints**

### **Document Processing**
```http
POST /api/documents/upload
Content-Type: multipart/form-data

# Upload document for processing
```

### **Analysis**
```http
POST /api/analysis/analyze
Content-Type: application/json

{
  "document_id": "doc_123",
  "analysis_type": "comprehensive"
}
```

### **Translation**
```http
POST /api/translate/hebrew-to-english
Content-Type: application/json

{
  "text": "שלום עולם! זה מבחן באבטחת מידע.",
  "document_type": "exam"
}
```

### **Health Check**
```http
GET /api/health
```

---

## 🧪 **Testing**

### **Backend Tests**
```bash
cd backend

# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Test translation system specifically
python test_translation.py
```

### **Frontend Tests**
```bash
cd frontend

# Run unit tests
npm test

# Run with coverage
npm run test:coverage
```

---

## 🔍 **Translation System**

### **Hebrew-to-English Translation**

The system includes a robust Hebrew translation service:

```python
from app.services.translation_service import TranslationService

translator = TranslationService()

# Translate Hebrew exam
result = await translator.translate_exam_document(hebrew_text)
print(result['translated_text'])  # Guaranteed English output
```

**Features:**
- ✅ **Chunked Processing** - Handles large documents efficiently
- ✅ **Force Validation** - Guarantees no Hebrew characters in output
- ✅ **Context-Aware** - Optimized for educational content
- ✅ **Batch Processing** - Multiple chunks processed concurrently
- ✅ **Error Recovery** - Fallback mechanisms for failed translations

---

## 📖 **Usage Examples**

### **Document Analysis Workflow**

```javascript
// Frontend: Upload and analyze document
const analyzeDocument = async (file) => {
  // 1. Upload document
  const uploadResult = await uploadDocument(file);

  // 2. Start analysis
  const analysis = await analyzeDocument(uploadResult.document_id);

  // 3. Display results
  console.log(`Found ${analysis.questions.length} questions`);
  console.log(`Topics: ${analysis.topics.map(t => t.topic_name).join(', ')}`);
};
```

### **Translation Example**

```python
# Backend: Translate Hebrew exam
async def translate_exam():
    translator = TranslationService()

    hebrew_exam = "1. מה זה אבטחת מידע? א) הגנה על מחשבים..."
    result = await translator.translate_exam_document(hebrew_exam)

    if result['success']:
        print("English Translation:")
        print(result['translated_text'])
```

---

## 🛠️ **Development**

### **Project Structure**
```
cramCortex/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # Reusable React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API service functions
│   │   └── types/           # TypeScript type definitions
│   └── package.json
├── backend/                  # FastAPI backend application
│   ├── app/
│   │   ├── api/             # API route handlers
│   │   ├── core/            # Configuration and security
│   │   ├── schemas/         # Pydantic data models
│   │   └── services/        # Business logic services
│   ├── requirements.txt
│   └── run.py
├── docs/                     # Documentation files
├── tests/                    # Test files
└── README.md
```

### **Adding New Features**

1. **Backend**: Add service in `app/services/`
2. **API**: Create route in `app/api/`
3. **Frontend**: Add component in `src/components/`
4. **Types**: Define in `src/types/`

### **Code Style**

- **Python**: Follow PEP 8, use `black` for formatting
- **JavaScript/TypeScript**: Use Prettier and ESLint
- **Git**: Conventional commit messages

---

## 🤝 **Contributing**

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- OpenAI for GPT API integration
- FastAPI team for the excellent web framework
- React team for the robust frontend framework
- All contributors and testers

---

## 📞 **Support**

- **Issues**: [GitHub Issues](https://github.com/davebruzil/cramCortex/issues)
- **Documentation**: [Project Wiki](https://github.com/davebruzil/cramCortex/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/davebruzil/cramCortex/discussions)

---

**cramCortex** - Transforming test preparation through intelligent analysis 🎓✨