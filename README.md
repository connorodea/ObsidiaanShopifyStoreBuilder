# StoreForge AI

An AI-powered Shopify app that builds complete ecommerce stores from a single product link — generating product descriptions, branded images, SEO copy, and a ready-to-launch Shopify theme within minutes.

## Architecture

### Backend (FastAPI + Python)
- **API**: FastAPI with async endpoints
- **Database**: PostgreSQL for data persistence
- **Queue**: Celery + Redis for background tasks
- **AI Integration**: OpenAI GPT-5 for content generation
- **Image Processing**: Leonardo API for visual enhancement
- **Web Scraping**: BeautifulSoup + Playwright for product data extraction

### Frontend (Next.js + React)
- **Framework**: Next.js 14 with App Router
- **UI Library**: Shopify Polaris components
- **Styling**: TailwindCSS
- **Auth**: Shopify OAuth 2.0
- **State Management**: Zustand

### Deployment
- **Containerization**: Docker + Docker Compose
- **Cloud**: Hetzner Cloud / AWS ECS
- **Storage**: AWS S3 for media files
- **CDN**: CloudFlare for global distribution

## Features

### Core Functionality
- ✅ Shopify OAuth login and store connection
- ✅ Product link import (AliExpress, Amazon, etc.)
- ✅ CSV bulk import for multiple products
- ✅ AI-powered content generation
- ✅ Leonardo API image enhancement
- ✅ Automatic store page generation
- ✅ One-click Shopify deployment

### Advanced Features
- ✅ SEO optimization
- ✅ Upsell and bundle flows
- ✅ Multi-language support
- ✅ Analytics dashboard
- ✅ Brand kit generator
- ✅ Template marketplace

## Competitive Analysis

**vs DropshipT/Atlas:**
- Better AI models (GPT-5 vs older models)
- Superior image enhancement with Leonardo API
- More flexible pricing with true freemium tier
- Modern tech stack for better performance
- Advanced features like CSV import and brand kit generation

## Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd storeforge-ai

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
npm run dev

# Development with Docker
docker-compose up -d
```

## Environment Variables

```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/storeforge
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your_openai_key
LEONARDO_API_KEY=your_leonardo_key
SHOPIFY_API_SECRET=your_shopify_secret
AWS_S3_BUCKET=your_s3_bucket

# Frontend (.env.local)
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your_nextauth_secret
SHOPIFY_APP_URL=your_shopify_app_url
```

## API Documentation

Once running, visit:
- Backend API docs: http://localhost:8000/docs
- Frontend app: http://localhost:3000

## License

MIT License - see LICENSE file for details.