# StoreForge AI Deployment Guide

## Development Setup

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Quick Start
```bash
# Clone the repository
git clone <repo-url>
cd storeforge-ai

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Edit environment variables
cp .env.example .env
# Add your API keys to .env

# Start development environment
chmod +x scripts/dev.sh
./scripts/dev.sh
```

## Production Deployment

### Option 1: Hetzner Cloud (Recommended)

1. **Create Hetzner Server**
   ```bash
   # Create a CX31 server (8GB RAM, 4 vCPUs)
   hcloud server create --type cx31 --image ubuntu-22.04 --name storeforge-prod
   ```

2. **Setup Server**
   ```bash
   # SSH into server
   ssh root@your-server-ip

   # Install Docker
   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker $USER

   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Deploy Application**
   ```bash
   # Clone repository
   git clone <repo-url>
   cd storeforge-ai

   # Setup environment
   cp .env.example .env
   nano .env  # Add production API keys

   # Start production services
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Option 2: AWS ECS

1. **Setup ECS Cluster**
   ```bash
   # Create ECS cluster
   aws ecs create-cluster --cluster-name storeforge-cluster
   ```

2. **Build and Push Images**
   ```bash
   # Build images
   docker build -t storeforge-backend ./backend
   docker build -t storeforge-frontend ./frontend

   # Tag and push to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   docker tag storeforge-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/storeforge-backend:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/storeforge-backend:latest
   ```

3. **Deploy with ECS Service**
   ```bash
   # Create task definition and service
   aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
   aws ecs create-service --cluster storeforge-cluster --service-name storeforge-service --task-definition storeforge-task --desired-count 2
   ```

## Environment Variables

### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/storeforge

# Redis
REDIS_URL=redis://redis:6379

# AI APIs
OPENAI_API_KEY=your_openai_key
LEONARDO_API_KEY=your_leonardo_key

# Shopify
SHOPIFY_API_SECRET=your_shopify_secret
SHOPIFY_APP_URL=https://your-domain.com

# AWS S3
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=storeforge-assets

# Security
SECRET_KEY=your-secret-key-here

# Stripe
STRIPE_SECRET_KEY=your_stripe_secret
STRIPE_PUBLISHABLE_KEY=your_stripe_public
```

### Frontend (.env.local)
```bash
NEXTAUTH_URL=https://your-domain.com
NEXTAUTH_SECRET=your_nextauth_secret
NEXT_PUBLIC_API_URL=https://api.your-domain.com
SHOPIFY_APP_URL=https://your-domain.com
```

## SSL & Domain Setup

### Using Cloudflare (Recommended)
1. Add your domain to Cloudflare
2. Set DNS records:
   - A record: your-domain.com → server-ip
   - A record: api.your-domain.com → server-ip
3. Enable SSL/TLS (Full mode)
4. Configure page rules for caching

### Using Let's Encrypt
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d api.your-domain.com

# Setup auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring & Logs

### Application Logs
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Health Checks
- Backend: `https://api.your-domain.com/health`
- Frontend: `https://your-domain.com`
- Database: Check connection via backend logs

### Performance Monitoring
- Use services like DataDog, New Relic, or Grafana
- Monitor API response times
- Track database performance
- Monitor Redis memory usage

## Backup Strategy

### Database Backups
```bash
# Create backup script
#!/bin/bash
docker exec postgres pg_dump -U storeforge storeforge > backup_$(date +%Y%m%d_%H%M%S).sql

# Setup cron job for daily backups
0 2 * * * /path/to/backup-script.sh
```

### S3 Backups
- Enable S3 versioning
- Setup lifecycle policies
- Use S3 Cross-Region Replication

## Scaling Considerations

### Horizontal Scaling
- Use load balancer (nginx, HAProxy)
- Scale backend with multiple containers
- Use Redis for session storage
- Implement database read replicas

### Performance Optimization
- Enable Redis caching
- Use CDN for static assets
- Optimize database queries
- Implement API rate limiting

## Security Checklist

- [ ] Enable HTTPS everywhere
- [ ] Configure CORS properly
- [ ] Use environment variables for secrets
- [ ] Enable database SSL
- [ ] Setup firewall rules
- [ ] Regular security updates
- [ ] Implement API rate limiting
- [ ] Use strong passwords/keys
- [ ] Enable audit logging

## Troubleshooting

### Common Issues

**Container won't start:**
```bash
# Check logs
docker-compose logs service-name

# Check resources
docker stats
```

**Database connection errors:**
```bash
# Check if database is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U storeforge -d storeforge
```

**API errors:**
```bash
# Check backend logs
docker-compose logs backend

# Check environment variables
docker-compose exec backend env | grep API_KEY
```

### Performance Issues
- Check database query performance
- Monitor Redis memory usage
- Check API response times
- Monitor server resources (CPU, RAM, disk)