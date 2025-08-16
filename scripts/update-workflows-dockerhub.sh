#!/bin/bash

# Script to update all GitHub Actions workflows to use Docker Hub instead of GitHub Container Registry
# Usage: ./scripts/update-workflows-dockerhub.sh

set -e

echo "🔄 Updating GitHub Actions workflows to use Docker Hub..."

# Define services and their configurations
declare -A SERVICES=(
    ["payment-service"]="8002"
    ["math-solver-service"]="8003"
    ["content-service"]="8004"
    ["admin-service"]="8005"
    ["frontend"]="3000"
)

# Update each service workflow
for service in "${!SERVICES[@]}"; do
    workflow_file=".github/workflows/${service}.yml"
    port="${SERVICES[$service]}"

    if [ -f "$workflow_file" ]; then
        echo "📝 Updating $workflow_file..."

        # Backup original file
        cp "$workflow_file" "${workflow_file}.backup"

        # Update registry and image name
        sed -i "s|REGISTRY: ghcr.io|REGISTRY: docker.io|g" "$workflow_file"
        sed -i "s|IMAGE_NAME: mathservice/${service}|IMAGE_NAME: hpt1976/${service}|g" "$workflow_file"

        # Add registry namespace if not exists
        if ! grep -q "REGISTRY_NAMESPACE:" "$workflow_file"; then
            sed -i "/REGISTRY: docker.io/a\\  REGISTRY_NAMESPACE: hpt1976" "$workflow_file"
        fi

        # Update Docker login action
        sed -i "s|Log in to Container Registry|Log in to Docker Hub|g" "$workflow_file"
        sed -i "s|registry: \${{ env.REGISTRY }}||g" "$workflow_file"
        sed -i "s|username: \${{ github.actor }}|username: \${{ secrets.DOCKERHUB_USERNAME }}|g" "$workflow_file"
        sed -i "s|password: \${{ secrets.GITHUB_TOKEN }}|password: \${{ secrets.DOCKERHUB_TOKEN }}|g" "$workflow_file"

        # Update metadata extraction
        sed -i "s|images: \${{ env.REGISTRY }}/\${{ env.IMAGE_NAME }}|images: \${{ env.IMAGE_NAME }}|g" "$workflow_file"

        # Update SBOM and Trivy scanner image references
        sed -i "s|image: \${{ env.REGISTRY }}/\${{ env.IMAGE_NAME }}:\${{ github.sha }}|image: \${{ env.IMAGE_NAME }}:\${{ github.sha }}|g" "$workflow_file"
        sed -i "s|image-ref: \${{ env.REGISTRY }}/\${{ env.IMAGE_NAME }}:\${{ github.sha }}|image-ref: \${{ env.IMAGE_NAME }}:\${{ github.sha }}|g" "$workflow_file"

        echo "✅ Updated $service workflow"
    else
        echo "⚠️ Workflow file not found: $workflow_file"
    fi
done

# Update docker-build-all.yml
echo "📝 Updating docker-build-all.yml..."
docker_build_all=".github/workflows/docker-build-all.yml"

if [ -f "$docker_build_all" ]; then
    # Backup original file
    cp "$docker_build_all" "${docker_build_all}.backup"

    # Update registry
    sed -i "s|REGISTRY: ghcr.io|REGISTRY: docker.io|g" "$docker_build_all"

    # Add registry namespace
    if ! grep -q "REGISTRY_NAMESPACE:" "$docker_build_all"; then
        sed -i "/REGISTRY: docker.io/a\\  REGISTRY_NAMESPACE: hpt1976" "$docker_build_all"
    fi

    # Update Docker login
    sed -i "s|Log in to Container Registry|Log in to Docker Hub|g" "$docker_build_all"
    sed -i "s|registry: \${{ env.REGISTRY }}||g" "$docker_build_all"
    sed -i "s|username: \${{ github.actor }}|username: \${{ secrets.DOCKERHUB_USERNAME }}|g" "$docker_build_all"
    sed -i "s|password: \${{ secrets.GITHUB_TOKEN }}|password: \${{ secrets.DOCKERHUB_TOKEN }}|g" "$docker_build_all"

    # Update image names in metadata
    sed -i "s|images: \${{ env.REGISTRY }}/\${{ github.repository }}/\${{ matrix.service.name }}|images: \${{ env.REGISTRY_NAMESPACE }}/\${{ matrix.service.name }}|g" "$docker_build_all"

    # Update SBOM and Trivy references
    sed -i "s|image: \${{ env.REGISTRY }}/\${{ github.repository }}/\${{ matrix.service.name }}:\${{ github.sha }}|image: \${{ env.REGISTRY_NAMESPACE }}/\${{ matrix.service.name }}:\${{ github.sha }}|g" "$docker_build_all"
    sed -i "s|image-ref: \${{ env.REGISTRY }}/\${{ github.repository }}/\${{ matrix.service.name }}:\${{ github.sha }}|image-ref: \${{ env.REGISTRY_NAMESPACE }}/\${{ matrix.service.name }}:\${{ github.sha }}|g" "$docker_build_all"

    echo "✅ Updated docker-build-all.yml"
else
    echo "⚠️ docker-build-all.yml not found"
fi

# Update docker-compose.yml files
echo "📝 Updating docker-compose.yml files..."

if [ -f "docker-compose.yml" ]; then
    cp "docker-compose.yml" "docker-compose.yml.backup"

    # Update image references
    sed -i "s|ghcr.io/hpt-ai/bai_tap/|mathservice/|g" "docker-compose.yml"

    echo "✅ Updated docker-compose.yml"
fi

# Update documentation
echo "📝 Updating documentation..."

# Update README.md
if [ -f "README.md" ]; then
    cp "README.md" "README.md.backup"

    # Update image references in README
    sed -i "s|ghcr.io/hpt-ai/bai_tap/|mathservice/|g" "README.md"
    sed -i "s|GitHub Container Registry|Docker Hub|g" "README.md"

    echo "✅ Updated README.md"
fi

# Create summary
echo ""
echo "🎉 Docker Hub migration completed!"
echo ""
echo "📋 Summary of changes:"
echo "✅ Updated 6 service workflows"
echo "✅ Updated docker-build-all.yml"
echo "✅ Updated docker-compose.yml"
echo "✅ Updated README.md"
echo ""
echo "🔧 Next steps:"
echo "1. Add GitHub Secrets:"
echo "   - DOCKERHUB_USERNAME=mathservice"
echo "   - DOCKERHUB_TOKEN=<your-docker-hub-token>"
echo ""
echo "2. Create Docker Hub organization 'mathservice'"
echo ""
echo "3. Test the workflows:"
echo "   - Run docker-hub-setup.yml workflow"
echo "   - Push code to trigger builds"
echo ""
echo "4. Verify repositories are created on Docker Hub"
echo ""
echo "📁 Backup files created (can be removed after verification):"
for service in "${!SERVICES[@]}"; do
    echo "   - .github/workflows/${service}.yml.backup"
done
echo "   - .github/workflows/docker-build-all.yml.backup"
echo "   - docker-compose.yml.backup"
echo "   - README.md.backup"
