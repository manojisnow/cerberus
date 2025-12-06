# Cerberus Quick Start Examples

## Example 1: Scan a Local Java Project

```bash
# Navigate to your Cerberus directory
cd /path/to/cerberus

# Build the Docker image
docker build -t cerberus:latest .

# Scan a local Java project (repository mounted to same path)
docker run --rm \
  --tmpfs /tmp:rw,exec,size=4g \
  -v /path/to/java-project:/path/to/java-project:ro \
  -v $(pwd)/reports:/cerberus/reports \
  cerberus:latest /path/to/java-project

# View the HTML report
open reports/cerberus_report_*.html
```

## Example 2: Using the Scan Script

The easiest way to scan a repository:

```bash
# Make the script executable
chmod +x scan-repo.sh

# Scan a repository
./scan-repo.sh /path/to/your/repository

# Reports will be in ./reports directory
```

## Example 3: Scan a Remote Repository

```bash
# Scan a GitHub repository
docker run --rm \
  -v $(pwd)/reports:/cerberus/reports \
  cerberus:latest https://github.com/OWASP/WebGoat --url

# Reports will be in ./reports directory
```

## Example 4: Custom Configuration

Create a custom config file `my-config.yaml`:

```yaml
build:
  enabled: true
  tool: maven

scanners:
  secrets:
    enabled: true
    tools:
      - gitleaks
  
  sast:
    enabled: true
    tools:
      - semgrep
      - spotbugs
  
  dependencies:
    enabled: true
    tools:
      - trivy
  
  iac:
    enabled: true
    tools:
      - trivy
      - checkov

severity:
  fail_on: CRITICAL
  report_threshold: LOW

reporting:
  formats:
    - json
    - html
    - markdown
```

Run with custom config:

```bash
docker run --rm \
  --tmpfs /tmp:rw,exec,size=4g \
  -v /path/to/project:/path/to/project:ro \
  -v $(pwd)/reports:/cerberus/reports \
  -v $(pwd)/my-config.yaml:/cerberus/config.yaml:ro \
  cerberus:latest /path/to/project --config /cerberus/config.yaml
```

## Example 5: CI/CD Integration (GitHub Actions)

Create `.github/workflows/cerberus-scan.yml`:

```yaml
name: Cerberus Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Cerberus
        run: docker build -t cerberus:latest .
        working-directory: ./cerberus
      
      - name: Run Security Scan
        run: |
          docker run --rm \
            --tmpfs /tmp:rw,exec,size=4g \
            -v ${{ github.workspace }}:${{ github.workspace }}:ro \
            -v ${{ github.workspace }}/reports:/cerberus/reports \
            cerberus:latest ${{ github.workspace }}
      
      - name: Upload Reports
        uses: actions/upload-artifact@v4
        with:
          name: security-reports
          path: reports/
```

## Performance Tips

1. **Cache Volumes**: Mount cache directories for faster subsequent scans
   ```bash
   -v ~/.cerberus/cache/trivy:/home/cerberus/.cache/trivy \
   -v ~/.cerberus/cache/semgrep:/home/cerberus/.cache/semgrep
   ```

2. **Tmpfs for /tmp**: Use tmpfs for better performance
   ```bash
   --tmpfs /tmp:rw,exec,size=4g
   ```

3. **Parallel Scanning**: Cerberus runs scanners in parallel automatically

## Report Formats

Cerberus generates three report formats:

- **JSON** (`cerberus_report_*.json`) - Machine-readable, complete data
- **HTML** (`cerberus_report_*.html`) - Beautiful formatted tables, color-coded severity
- **Markdown** (`cerberus_report_*.md`) - GitHub-compatible, readable tables

## Next Steps

1. Review the generated reports
2. Prioritize critical and high severity findings
3. Create tickets for remediation
4. Integrate into your CI/CD pipeline
5. Run regularly (weekly or on every PR)

For more information, see:
- [README.md](../README.md)
- [TOOLS.md](TOOLS.md)
- [TEST_RESULTS.md](TEST_RESULTS.md)
