# StoreForge AI - Getting Started Guide

This guide will help you set up and launch StoreForge AI to compete with DropshipT and other Shopify store builders.

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Docker & Docker Compose
- Git
- Text editor

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd storeforge-ai
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 2. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit with your API keys
nano .env
```

### 3. Start Development
```bash
chmod +x scripts/dev.sh
./scripts/dev.sh
```

**That's it!** Your StoreForge AI is now running:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🔑 Required API Keys

### 1. OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Add to `.env`: `OPENAI_API_KEY=sk-...`

### 2. Leonardo AI API Key
1. Go to https://leonardo.ai/
2. Sign up and get API access
3. Add to `.env`: `LEONARDO_API_KEY=...`

### 3. Shopify Partner Account
1. Go to https://partners.shopify.com/
2. Create partner account
3. Create new app in Partner Dashboard
4. Get API secret: `SHOPIFY_API_SECRET=...`

### 4. AWS S3 (for image storage)
1. Create AWS account
2. Create S3 bucket
3. Create IAM user with S3 access
4. Add credentials to `.env`

### 5. Stripe (for billing)
1. Create Stripe account
2. Get API keys from dashboard
3. Add to `.env`: `STRIPE_SECRET_KEY=sk_...`

## 📋 Environment Variables

```bash
# Database
DATABASE_URL=postgresql://storeforge:storeforge123@localhost:5432/storeforge

# Redis
REDIS_URL=redis://localhost:6379

# AI APIs
OPENAI_API_KEY=your_openai_key_here
LEONARDO_API_KEY=your_leonardo_key_here

# Shopify
SHOPIFY_API_SECRET=your_shopify_secret_here
SHOPIFY_APP_URL=https://your-domain.com

# AWS S3
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=storeforge-assets

# Stripe
STRIPE_SECRET_KEY=your_stripe_secret
STRIPE_WEBHOOK_SECRET=your_webhook_secret

# NextAuth
NEXTAUTH_SECRET=your_random_secret_here
```

## 🏗️ Project Structure

```
storeforge-ai/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── api/            # REST API endpoints
│   │   ├── ai/             # AI content & image generation
│   │   ├── scraper/        # Product scraping
│   │   ├── services/       # Business logic
│   │   ├── models/         # Database models
│   │   └── core/           # Configuration
│   ├── alembic/            # Database migrations
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # Next.js React frontend
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/    # Reusable components
│   │   └── lib/          # Utilities
│   └── package.json      # Node dependencies
│
├── scripts/               # Setup and deployment scripts
├── docs/                 # Documentation
└── docker-compose.yml   # Container orchestration
```

## 🔧 Development Workflow

### Running Services Individually

**Backend only:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend only:**
```bash
cd frontend
npm install
npm run dev
```

**Database only:**
```bash
docker-compose up -d postgres redis
```

### Database Management

**Create migration:**
```bash
cd backend
alembic revision --autogenerate -m "Add new table"
```

**Run migrations:**
```bash
alembic upgrade head
```

**Reset database:**
```bash
docker-compose down -v
docker-compose up -d postgres
alembic upgrade head
```

## 🚀 Deployment Options

### Option 1: Hetzner Cloud (Recommended - €20/month)

```bash
# Create server
hcloud server create --type cx31 --image ubuntu-22.04 --name storeforge-prod

# Deploy
ssh root@your-server-ip
git clone <repo-url>
cd storeforge-ai
./scripts/setup.sh
docker-compose -f docker-compose.prod.yml up -d
```

### Option 2: DigitalOcean ($40/month)

```bash
# Use DigitalOcean App Platform
# Connect GitHub repo
# Set environment variables
# Deploy automatically
```

### Option 3: Railway ($20/month)

```bash
# Connect GitHub repo to Railway
# Set environment variables
# Deploy with one click
```

## 📈 Go-to-Market Strategy

### 1. Shopify App Store Launch

**Preparation:**
1. Complete app review checklist
2. Create compelling app listing
3. Add screenshots and demo video
4. Set up analytics tracking

**Listing Optimization:**
- Title: "StoreForge AI - Build Stores in Minutes"
- Description: Focus on speed, AI quality, and ease of use
- Keywords: AI, automation, dropshipping, store builder
- Screenshots: Show before/after transformations

### 2. Target Audience

**Primary:** Dropshipping entrepreneurs
- Pain: Time-consuming store setup
- Solution: 2-minute AI store generation

**Secondary:** E-commerce agencies
- Pain: Manual client work
- Solution: White-label automation

**Tertiary:** Small business owners
- Pain: Technical complexity
- Solution: No-code store building

### 3. Pricing Strategy

**Competitive Analysis:**
- DropshipT: $39-99/month
- Other apps: $29-149/month
- Our advantage: Better AI, faster generation

**Our Pricing:**
- Free: 1 store (lead generation)
- Pro: $39/month, 10 stores (compete directly)
- Agency: $99/month, unlimited (undercut competition)

### 4. Marketing Channels

**Organic:**
- YouTube tutorials (AI store building)
- TikTok demos (viral potential)
- SEO content marketing
- Shopify community engagement

**Paid:**
- Google Ads (dropshipping keywords)
- Facebook Ads (entrepreneur targeting)
- YouTube ads (competitor channels)
- Shopify App Store ads

### 5. Launch Timeline

**Week 1-2: Soft Launch**
- Deploy to production
- Submit to Shopify App Store
- Create initial content

**Week 3-4: Public Launch**
- Launch marketing campaigns
- Influencer partnerships
- Product Hunt launch

**Month 2-3: Scale**
- Optimize based on feedback
- Add requested features
- International expansion

## 📊 Success Metrics

### Technical KPIs
- Store generation time: <2 minutes
- Success rate: >95%
- AI content quality: >90% satisfaction
- Uptime: >99.9%

### Business KPIs
- Monthly Recurring Revenue (MRR)
- Customer Acquisition Cost (CAC)
- Lifetime Value (LTV)
- App Store ranking
- Customer satisfaction score

### Revenue Projections

**Month 1:** $2,000 MRR (50 Pro users)
**Month 3:** $8,000 MRR (150 Pro, 20 Agency)
**Month 6:** $25,000 MRR (400 Pro, 80 Agency)
**Month 12:** $60,000 MRR (1000 Pro, 200 Agency)

## 🎯 Competitive Advantages

### vs DropshipT
✅ **Better AI:** GPT-5 vs GPT-3.5
✅ **Faster:** 2 min vs 5+ min
✅ **Better Images:** Leonardo AI enhancement
✅ **Free Tier:** 1 store vs preview only

### vs Generic Builders
✅ **AI-First:** Built for automation
✅ **Shopify Native:** Deep integration
✅ **E-commerce Focus:** Not generic website builder
✅ **Modern Tech:** Next.js + FastAPI

## 🔧 Troubleshooting

### Common Issues

**"Port already in use" error:**
```bash
sudo lsof -i :3000  # Find process using port
sudo kill -9 <PID>  # Kill the process
```

**Database connection error:**
```bash
docker-compose restart postgres
# Wait 30 seconds
docker-compose logs postgres
```

**API key errors:**
- Check `.env` file formatting
- Ensure no trailing spaces
- Restart services after changes

**Shopify OAuth issues:**
- Verify app URLs in Partner Dashboard
- Check HTTPS in production
- Validate webhook endpoints

### Getting Help

1. **Documentation:** Check `/docs` folder
2. **API Docs:** http://localhost:8000/docs
3. **Logs:** `docker-compose logs -f`
4. **Community:** Create GitHub issues

## 🎉 Next Steps

1. **Complete Setup:** Follow this guide
2. **Test Locally:** Generate your first store
3. **Deploy:** Choose deployment option
4. **Launch:** Submit to Shopify App Store
5. **Scale:** Optimize and grow

**Ready to compete with DropshipT? Let's build the future of AI-powered e-commerce! 🚀**