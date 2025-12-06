# Cerberus Security Tools Reference

This document describes each security scanning tool integrated into Cerberus, what it detects, and how it works.

## Secrets Detection

### Gitleaks

**What it detects:**
- Hardcoded API keys
- AWS credentials
- Database passwords
- Private keys
- OAuth tokens
- Generic secrets patterns

**How it works:**
- Scans all files in the repository
- Uses regex patterns and entropy detection
- Checks git history (when scanning git repos)
- Reports file path, line number, and secret type

**Configuration:**
```yaml
scanners:
  secrets:
    enabled: true
    tools:
      - gitleaks
```

---

## Static Application Security Testing (SAST)

### Semgrep

**What it detects:**
- SQL injection vulnerabilities
- Cross-site scripting (XSS)
- Command injection
- Path traversal
- Insecure deserialization
- Hardcoded credentials
- Weak cryptography

**How it works:**
- Uses semantic code analysis
- Pattern matching with context awareness
- Language-agnostic rules
- Supports Java, JavaScript, Python, Go, and more

**Configuration:**
```yaml
scanners:
  sast:
    enabled: true
    tools:
      - semgrep
```

### SpotBugs

**What it detects:**
- Null pointer dereferences
- Infinite loops
- Resource leaks
- Concurrency issues
- Security vulnerabilities (with FindSecBugs)
- Bad practices in Java code

**How it works:**
- Analyzes Java bytecode (JAR/WAR files)
- Uses static analysis patterns
- Includes FindSecBugs plugin for security checks
- Detects bugs that compilers miss

**Configuration:**
```yaml
scanners:
  sast:
    enabled: true
    tools:
      - spotbugs
```

---

## Dependency Vulnerability Scanning

### Trivy

**What it detects:**
- Known CVEs in dependencies
- Vulnerable library versions
- Outdated packages
- License issues
- Misconfigurations

**How it works:**
- Scans package manifests (pom.xml, package.json, etc.)
- Checks against NVD, GitHub Advisory Database
- Analyzes JAR files for embedded dependencies
- Provides fix versions when available

**Configuration:**
```yaml
scanners:
  dependencies:
    enabled: true
    tools:
      - trivy
```

**Report Format:**
Trivy results are displayed in formatted tables showing:
- CVE ID
- Severity (CRITICAL, HIGH, MEDIUM, LOW)
- Package name
- Installed version
- Fixed version
- Vulnerability description

---

## Infrastructure-as-Code (IaC) Scanning

### Trivy (IaC Mode)

**What it detects:**
- Dockerfile misconfigurations
- Kubernetes manifest issues
- Terraform security problems
- CloudFormation issues
- Exposed secrets in IaC files

**How it works:**
- Parses IaC files
- Checks against security best practices
- Validates configurations
- Reports misconfigurations with remediation advice

### Checkov

**What it detects:**
- Dockerfile security issues
- Kubernetes security misconfigurations
- Terraform vulnerabilities
- GitHub Actions security issues
- Missing security controls

**How it works:**
- Policy-as-code scanning
- Checks against CIS benchmarks
- Validates security best practices
- Provides detailed remediation guidance

**Configuration:**
```yaml
scanners:
  iac:
    enabled: true
    tools:
      - trivy
      - checkov
```

**Report Format:**
Checkov results show:
- Check ID
- Check name
- File path
- Passed/Failed status
- Remediation advice

---

## Dockerfile Linting

### Hadolint

**What it detects:**
- Dockerfile best practice violations
- Security issues in Dockerfiles
- Inefficient layer usage
- Missing metadata
- Deprecated instructions

**How it works:**
- Parses Dockerfile syntax
- Checks against best practices
- Validates instruction usage
- Suggests optimizations

**Configuration:**
```yaml
scanners:
  linting:
    enabled: true
    tools:
      - hadolint
```

---

## Severity Levels

All tools report findings with severity levels:

- **CRITICAL**: Immediate action required, exploitable vulnerabilities
- **HIGH**: Important security issues, should be fixed soon
- **MEDIUM**: Moderate risk, fix in next release
- **LOW**: Minor issues, fix when convenient
- **INFO**: Informational findings, best practices

---

## Tool Comparison

| Tool | Type | Language | Speed | Accuracy |
|------|------|----------|-------|----------|
| Gitleaks | Secrets | Any | Fast | High |
| Semgrep | SAST | Multi | Fast | High |
| SpotBugs | SAST | Java | Medium | Very High |
| Trivy | Deps/IaC | Multi | Fast | High |
| Checkov | IaC | Multi | Fast | High |
| Hadolint | Linting | Dockerfile | Very Fast | High |

---

## Removed Tools

The following tools were evaluated but removed:

- **TruffleHog**: Redundant with Gitleaks, had binary update issues
- **OWASP Dependency-Check**: Database initialization issues, Trivy provides better coverage

---

## For More Information

- [EXAMPLES.md](EXAMPLES.md) - Usage examples
- [TEST_RESULTS.md](TEST_RESULTS.md) - Test results and benchmarks
- [README.md](../README.md) - Main documentation
