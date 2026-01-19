# AWS Free Tier Ubuntu Deployment Guide

## Quick Start

### 1. Launch EC2 Instance
1. Go to AWS Console → EC2 → Launch Instance
2. Select **Ubuntu Server 22.04 LTS** (free tier eligible)
3. Instance type: **t2.micro** (free tier)
4. Create or select a key pair for SSH access
5. Security Group: Allow **HTTP (80)**, **HTTPS (443)**, and **SSH (22)**

### 2. Connect to EC2
```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### 3. Upload Project Files
```bash
# From your local machine
scp -i your-key.pem -r Company_performance_review ubuntu@your-ec2-ip:/home/ubuntu/performance_review
```

### 4. Run Deployment Script
```bash
cd /home/ubuntu/performance_review
chmod +x deploy_aws.sh
./deploy_aws.sh
```

### 5. Configure Your Domain/IP
```bash
# Edit .env file
nano /home/ubuntu/performance_review/.env

# Update these values:
DJANGO_ALLOWED_HOSTS=your-domain.com,your-ec2-ip
DJANGO_CSRF_ORIGINS=http://your-domain.com

# Edit Nginx config
sudo nano /etc/nginx/sites-available/performance_review
# Update server_name with your domain/IP
```

### 6. Restart Services
```bash
sudo systemctl restart performance_review
sudo systemctl restart nginx
```

### 7. Create Admin User
```bash
cd /home/ubuntu/performance_review
source venv/bin/activate
python manage.py createsuperuser
```

## Access Your App
- **URL**: `http://your-ec2-public-ip/`
- **Admin**: `http://your-ec2-public-ip/admin/`

## Useful Commands

| Task | Command |
|------|---------|
| View app logs | `sudo journalctl -u performance_review -f` |
| Restart app | `sudo systemctl restart performance_review` |
| Restart Nginx | `sudo systemctl restart nginx` |
| Check status | `sudo systemctl status performance_review` |
| Run migrations | `cd /home/ubuntu/performance_review && source venv/bin/activate && python manage.py migrate` |

## Security Checklist
- [ ] Update `.env` with strong secret key
- [ ] Set `DEBUG=False`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Set up SSL certificate (Let's Encrypt)
- [ ] Configure firewall (UFW)
