#!/bin/bash
# Test script to verify all security tools are installed in Docker image

echo "Testing Cerberus Docker Image - Tool Verification"
echo "=================================================="
echo ""

# Test each tool
echo "1. Testing Trivy..."
docker run --rm cerberus:latest sh -c "trivy --version" && echo "✅ Trivy OK" || echo "❌ Trivy FAILED"

echo ""
echo "2. Testing Grype..."
docker run --rm cerberus:latest sh -c "grype version" && echo "✅ Grype OK" || echo "❌ Grype FAILED"

echo ""
echo "3. Testing Gitleaks..."
docker run --rm cerberus:latest sh -c "gitleaks version" && echo "✅ Gitleaks OK" || echo "❌ Gitleaks FAILED"

echo ""
echo "4. Testing TruffleHog..."
docker run --rm cerberus:latest sh -c "trufflehog --version" && echo "✅ TruffleHog OK" || echo "❌ TruffleHog FAILED"

echo ""
echo "5. Testing Semgrep..."
docker run --rm cerberus:latest sh -c "semgrep --version" && echo "✅ Semgrep OK" || echo "❌ Semgrep FAILED"

echo ""
echo "6. Testing Hadolint..."
docker run --rm cerberus:latest sh -c "hadolint --version" && echo "✅ Hadolint OK" || echo "❌ Hadolint FAILED"

echo ""
echo "7. Testing Checkov..."
docker run --rm cerberus:latest sh -c "checkov --version" && echo "✅ Checkov OK" || echo "❌ Checkov FAILED"

echo ""
echo "8. Testing Kubescape..."
docker run --rm cerberus:latest sh -c "kubescape version" && echo "✅ Kubescape OK" || echo "❌ Kubescape FAILED"

echo ""
echo "9. Testing Kubeaudit..."
docker run --rm cerberus:latest sh -c "kubeaudit version" && echo "✅ Kubeaudit OK" || echo "❌ Kubeaudit FAILED"

echo ""
echo "10. Testing Helm..."
docker run --rm cerberus:latest sh -c "helm version" && echo "✅ Helm OK" || echo "❌ Helm FAILED"

echo ""
echo "11. Testing OWASP Dependency-Check..."
docker run --rm cerberus:latest sh -c "dependency-check --version" && echo "✅ OWASP DC OK" || echo "❌ OWASP DC FAILED"

echo ""
echo "12. Testing Maven..."
docker run --rm cerberus:latest sh -c "mvn --version" && echo "✅ Maven OK" || echo "❌ Maven FAILED"

echo ""
echo "=================================================="
echo "Tool verification complete!"
