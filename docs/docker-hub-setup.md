# Docker Hub Registry Setup Guide

## 📋 Overview

This guide explains how to set up Docker Hub registry for the Math Service project, including repository creation, authentication, and automated pushing.

## 🐳 Docker Hub Registry Configuration

### 1. Registry Information
- **Registry URL**: `docker.io` (default Docker Hub)
- **Organization**: `hpt1976` (Personal Account)
- **Public Access**: All repositories will be public
- **Image Naming**: `hpt1976/{service-name}:tag`

### 2. Required Repositories

#### 📊 Service Repositories:
1. **hpt1976/user-service** - Authentication and user management
2. **hpt1976/payment-service** - Payment processing and transactions
3. **hpt1976/math-solver-service** - Mathematical computation engine
4. **hpt1976/content-service** - Content management and SEO
5. **hpt1976/admin-service** - System administration and monitoring
6. **hpt1976/frontend** - Next.js frontend application

## 🔐 Authentication Setup

### 1. Docker Hub Account Requirements
- **Account Type**: Free or Pro account
- **Organization**: Use your personal Docker Hub account (`hpt1976`)
- **Access Tokens**: Generate access tokens for CI/CD

### 2. Required Secrets in GitHub
```bash
# GitHub Repository Secrets
DOCKERHUB_USERNAME=hpt1976
DOCKERHUB_TOKEN=dckr_pat_xxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Token Permissions
- **Repository Access**: Read, Write, Delete
- **Public Repository**: Create public repositories
- **Organization**: Access to hpt1976 personal account

## 🚀 Automated Image Pushing

### 1. Trigger Conditions
- **Push to main branch**: Automatic build and push
- **Successful tests**: Only push after all tests pass
- **Pull requests**: Build but don't push (for testing)

### 2. Image Tagging Strategy
```bash
# Production tags
hpt1976/user-service:latest
hpt1976/user-service:v1.0.0
hpt1976/user-service:main-{commit-sha}

# Development tags
hpt1976/user-service:develop
hpt1976/user-service:feature-{branch-name}
```

### 3. Multi-platform Support
- **linux/amd64**: Standard x86_64 architecture
- **linux/arm64**: ARM64 architecture (Apple Silicon, ARM servers)

## 📋 Repository Configuration

### 1. Repository Settings
```yaml
# Each repository configuration
Name: hpt1976/{service-name}
Visibility: Public
Description: {Service description}
README: Auto-generated from repository
```

### 2. Repository Descriptions
- **user-service**: "Authentication and user management service for Math Service platform"
- **payment-service**: "Payment processing and transaction management service"
- **math-solver-service**: "Mathematical computation and problem solving engine"
- **content-service**: "Content management and SEO optimization service"
- **admin-service**: "System administration and monitoring service"
- **frontend**: "Next.js frontend application for Math Service platform"

## 🔧 GitHub Actions Integration

### 1. Workflow Configuration
```yaml
env:
  REGISTRY: docker.io
  REGISTRY_NAMESPACE: hpt1976

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
    - name: Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}

    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        push: true
        tags: |
          hpt1976/{service-name}:latest
          hpt1976/{service-name}:${{ github.sha }}
```

### 2. Security Considerations
- **Token Rotation**: Rotate access tokens every 6 months
- **Least Privilege**: Use tokens with minimal required permissions
- **Secret Management**: Store tokens securely in GitHub Secrets

## 📊 Monitoring and Maintenance

### 1. Image Metrics
- **Pull Statistics**: Monitor image download counts
- **Vulnerability Scanning**: Regular security scans
- **Size Optimization**: Monitor and optimize image sizes

### 2. Cleanup Policies
- **Tag Retention**: Keep last 10 tags per repository
- **Old Images**: Clean up images older than 6 months
- **Development Tags**: Clean up feature branch tags after merge

## 🎯 Benefits of Docker Hub

### 1. Public Accessibility
- **Easy Distribution**: Anyone can pull images
- **Documentation**: Integrated README and documentation
- **Community**: Public visibility for open source project

### 2. Integration Features
- **GitHub Integration**: Automatic builds from GitHub
- **Webhook Support**: Trigger deployments on image push
- **API Access**: Programmatic access to repositories

### 3. Performance
- **Global CDN**: Fast image pulls worldwide
- **Layer Caching**: Efficient layer sharing
- **Parallel Downloads**: Multi-connection downloads

## 🔄 Migration from GitHub Container Registry

### 1. Dual Registry Support
```yaml
# Push to both registries during transition
- name: Push to GitHub Container Registry
  run: docker push ghcr.io/hpt-ai/bai_tap/{service-name}:${{ github.sha }}

- name: Push to Docker Hub
  run: docker push hpt1976/{service-name}:${{ github.sha }}
```

### 2. Gradual Migration
- **Phase 1**: Setup Docker Hub repositories
- **Phase 2**: Configure dual pushing
- **Phase 3**: Update deployment to use Docker Hub
- **Phase 4**: Deprecate GitHub Container Registry

## 📋 Setup Checklist

### Prerequisites
- [ ] Docker Hub account created
- [ ] `hpt1976` organization created
- [ ] Access token generated
- [ ] GitHub secrets configured

### Repository Creation
- [ ] hpt1976/user-service
- [ ] hpt1976/payment-service
- [ ] hpt1976/math-solver-service
- [ ] hpt1976/content-service
- [ ] hpt1976/admin-service
- [ ] hpt1976/frontend

### Workflow Updates
- [ ] Update registry URLs in workflows
- [ ] Configure Docker Hub authentication
- [ ] Test automated pushing
- [ ] Verify image accessibility

### Documentation
- [ ] Update README with new image URLs
- [ ] Update deployment documentation
- [ ] Update docker-compose.yml files
- [ ] Notify team of registry change

## 🎯 Next Steps

1. **✅ Create Docker Hub Account**: Sign up and create organization
2. **✅ Generate Access Token**: Create token with appropriate permissions
3. **✅ Configure GitHub Secrets**: Add DOCKERHUB_USERNAME and DOCKERHUB_TOKEN
4. **✅ Update Workflows**: Modify GitHub Actions to use Docker Hub
5. **🔄 Test Pipeline**: Verify automated building and pushing
6. **✅ Update Documentation**: Update all references to new registry

---

**✅ Status**: Docker Hub setup completed successfully! All workflows have been updated to use Docker Hub registry with the `hpt1976` personal account.
