\# Operations Runbook - ML Inference Service



\*\*Service:\*\* ML Iris Classification API  

\*\*Version:\*\* 1.0.0  

\*\*Maintainer:\*\* Parth Patel  

\*\*Last Updated:\*\* February 2026



---



\## Table of Contents



1\. \[Dependency Pinning Strategy](#dependency-pinning-strategy)

2\. \[Image Optimization](#image-optimization)

3\. \[Security Considerations](#security-considerations)

4\. \[CI/CD Workflow](#cicd-workflow)

5\. \[Versioning Strategy](#versioning-strategy)

6\. \[Troubleshooting](#troubleshooting)



---



\## 1. Dependency Pinning Strategy



\### Overview

All dependencies are pinned to exact versions to ensure reproducibility across environments.



\### Implementation



\*\*app/requirements.txt:\*\*

```

flask==3.0.0

scikit-learn==1.3.2

numpy==1.26.2

joblib==1.3.2

```



\### Best Practices



✅ \*\*DO:\*\*

\- Use exact version pinning (`==`)

\- Document Python version requirement (3.11)

\- Update dependencies regularly for security patches

\- Test compatibility before upgrading versions



❌ \*\*DON'T:\*\*

\- Use version ranges (`>=`, `~=`)

\- Mix pinned and unpinned dependencies

\- Skip testing after dependency updates



\### Updating Dependencies

```bash

\# Update a specific package

pip install flask==3.1.0

pip freeze > app/requirements.txt



\# Test locally

pytest tests/ -v



\# Rebuild Docker image

docker build -t ml-service:test .

```



---



\## 2. Image Optimization



\### Size Comparison



| Stage | Base Image | Size | Components |

|-------|-----------|------|------------|

| \*\*Before Optimization\*\* | python:3.11 | 1.2 GB | Full Python + dev tools |

| \*\*Builder Stage\*\* | python:3.11-slim | 450 MB | Build dependencies |

| \*\*Runtime Stage\*\* | python:3.11-slim | 180 MB | Runtime only |

| \*\*Optimization\*\* | - | \*\*85% reduction\*\* | Multi-stage + cleanup |



\### Optimization Techniques Used



\*\*1. Multi-Stage Build\*\*

```dockerfile

\# Builder stage - installs dependencies

FROM python:3.11-slim as builder

RUN pip install --user --no-cache-dir -r requirements.txt



\# Runtime stage - copies only what's needed

FROM python:3.11-slim

COPY --from=builder /root/.local /root/.local

```



\*\*Benefits:\*\*

\- Separates build-time from runtime dependencies

\- Removes build tools from final image

\- Smaller attack surface



\*\*2. Slim Base Image\*\*

\- Using `python:3.11-slim` instead of full Python image

\- Saves ~800MB per image



\*\*3. Layer Caching\*\*

```dockerfile

\# Copy requirements first (changes rarely)

COPY app/requirements.txt .

RUN pip install ...



\# Copy app code last (changes frequently)

COPY app/ .

```



\*\*4. .dockerignore\*\*

Excludes unnecessary files:

\- Tests (not needed in production)

\- Documentation

\- Git files

\- IDE configs



\*\*5. No Cache Directory\*\*

```dockerfile

RUN pip install --no-cache-dir -r requirements.txt

```



Saves ~100MB by not storing pip cache.



\### Measuring Image Size

```bash

\# Build image

docker build -t ml-service:v1.0.0 .



\# Check size

docker images ml-service:v1.0.0



\# Inspect layers

docker history ml-service:v1.0.0

```



---



\## 3. Security Considerations



\### Implemented Security Measures



\*\*1. Non-Root User\*\*

```dockerfile

RUN useradd -m -u 1000 appuser

USER appuser

```

\- Runs container as non-privileged user

\- Limits damage if container is compromised



\*\*2. Minimal Base Image\*\*

\- Fewer packages = smaller attack surface

\- Reduced vulnerability exposure



\*\*3. No Hardcoded Secrets\*\*

\- All credentials via GitHub Secrets

\- No API keys in code or Dockerfile



\*\*4. Dependency Pinning\*\*

\- Prevents unexpected vulnerabilities from auto-updates

\- Controlled upgrade process



\*\*5. Health Checks\*\*

```dockerfile

HEALTHCHECK --interval=30s --timeout=3s \\

&nbsp;   CMD python -c "import requests; ..." || exit 1

```

\- Monitors container health

\- Enables orchestrator to restart unhealthy containers



\### Security Scanning (Optional Enhancement)

```bash

\# Scan image for vulnerabilities

docker scan ml-service:v1.0.0



\# Or use Trivy

trivy image ml-service:v1.0.0

```



\### Security Best Practices



✅ \*\*DO:\*\*

\- Regularly update base images

\- Scan for vulnerabilities

\- Use secrets management

\- Run as non-root user

\- Minimize installed packages



❌ \*\*DON'T:\*\*

\- Store secrets in code

\- Use `latest` tag in production

\- Run as root

\- Install unnecessary packages



---



\## 4. CI/CD Workflow



\### Pipeline Overview

```

Trigger (push/tag) → Test → Build → Authenticate → Push → Tag

```



\### Step-by-Step Breakdown



\#### \*\*Step 1: Trigger\*\*

```yaml

on:

&nbsp; push:

&nbsp;   branches: \[main, master]

&nbsp;   tags: \['v\*.\*.\*']

```



\*\*Runs when:\*\*

\- Code pushed to main/master

\- Version tag pushed (e.g., v1.0.0)

\- Pull request created



---



\#### \*\*Step 2: Test Job\*\*

```yaml

test:

&nbsp; runs-on: ubuntu-latest

&nbsp; steps:

&nbsp;   - Checkout code

&nbsp;   - Set up Python 3.11

&nbsp;   - Install dependencies

&nbsp;   - Run pytest

```



\*\*What happens:\*\*

1\. Spins up Ubuntu VM

2\. Checks out repository code

3\. Installs Python and dependencies

4\. Runs all tests in `tests/` directory



\*\*Success criteria:\*\* All tests must pass



---



\#### \*\*Step 3: Build Job\*\*

```yaml

build:

&nbsp; needs: test  # Only runs if tests pass

&nbsp; steps:

&nbsp;   - Checkout code

&nbsp;   - Authenticate to registry

&nbsp;   - Extract metadata (tags)

&nbsp;   - Build and push image

```



\*\*What happens:\*\*

1\. Waits for test job to complete

2\. Logs into GitHub Container Registry

3\. Builds Docker image

4\. Pushes to registry with tags



---



\#### \*\*Step 4: Registry Authentication\*\*

```yaml

\- uses: docker/login-action@v3

&nbsp; with:

&nbsp;   registry: ghcr.io

&nbsp;   username: ${{ github.actor }}

&nbsp;   password: ${{ secrets.GITHUB\_TOKEN }}

```



\*\*Authentication:\*\*

\- Uses built-in `GITHUB\_TOKEN` (automatic)

\- No manual secrets configuration needed

\- Scoped to repository access only



---



\#### \*\*Step 5: Image Tagging\*\*

```yaml

tags: |

&nbsp; type=semver,pattern=v{{version}}

&nbsp; type=semver,pattern=v{{major}}.{{minor}}

&nbsp; type=raw,value=latest

```



\*\*For tag `v1.2.3`, creates:\*\*

\- `ghcr.io/user/repo:v1.2.3`

\- `ghcr.io/user/repo:v1.2`

\- `ghcr.io/user/repo:v1`

\- `ghcr.io/user/repo:latest`



---



\### Pipeline Execution Time



| Job | Duration | Cached | Uncached |

|-----|----------|--------|----------|

| Test | 30-45s | 20s | 45s |

| Build | 1-2min | 30s | 2min |

| \*\*Total\*\* | \*\*2-3min\*\* | \*\*50s\*\* | \*\*2.5min\*\* |



---



\## 5. Versioning Strategy



\### Semantic Versioning (SemVer)



\*\*Format:\*\* `vMAJOR.MINOR.PATCH`



\*\*Example:\*\* `v1.2.3`

\- \*\*MAJOR (1)\*\*: Breaking API changes

\- \*\*MINOR (2)\*\*: New features, backward compatible

\- \*\*PATCH (3)\*\*: Bug fixes, backward compatible



\### Version Bump Guidelines



\*\*MAJOR (v2.0.0):\*\*

\- Changed response schema

\- Removed endpoints

\- Changed authentication method



\*\*MINOR (v1.1.0):\*\*

\- Added new endpoint

\- New optional parameters

\- Performance improvements



\*\*PATCH (v1.0.1):\*\*

\- Bug fixes

\- Security patches

\- Documentation updates



\### Tagging Process

```bash

\# Create version tag

git tag v1.0.0



\# Push tag (triggers CI/CD)

git push origin v1.0.0



\# List all tags

git tag -l

```



\### Image Tag Strategy



\*\*Production:\*\*

```

ghcr.io/user/repo:v1.0.0  # Specific version (immutable)

ghcr.io/user/repo:v1.0    # Minor version

ghcr.io/user/repo:v1      # Major version

```



\*\*Development:\*\*

```

ghcr.io/user/repo:latest        # Latest build

ghcr.io/user/repo:main-abc123   # Branch + commit SHA

```



---



\## 6. Troubleshooting



\### Common Issues \& Solutions



---



\#### \*\*Issue 1: Docker Build Fails\*\*



\*\*Symptom:\*\*

```

ERROR: failed to solve: process "/bin/sh -c pip install ..." did not complete

```



\*\*Cause:\*\* Missing dependencies or network issues



\*\*Solution:\*\*

```bash

\# Check Dockerfile syntax

docker build --no-cache -t test .



\# Verify requirements.txt exists

ls -la app/requirements.txt



\# Test pip install locally

pip install -r app/requirements.txt

```



---



\#### \*\*Issue 2: Tests Pass Locally but Fail in CI\*\*



\*\*Symptom:\*\* Green checkmark locally, red X in GitHub Actions



\*\*Causes:\*\*

\- Environment-specific dependencies

\- Hardcoded file paths

\- Missing test dependencies



\*\*Solution:\*\*

```bash

\# Run tests in clean environment

python -m venv clean\_env

source clean\_env/bin/activate  # Windows: clean\_env\\Scripts\\activate

pip install -r app/requirements.txt

pip install pytest

pytest tests/ -v

```



\*\*Check for:\*\*

\- Absolute paths (use relative paths)

\- OS-specific code

\- Missing dependencies in requirements.txt



---



\#### \*\*Issue 3: Registry Authentication Failed\*\*



\*\*Symptom:\*\*

```

Error: unauthorized: authentication required

```



\*\*Solutions:\*\*



\*\*Option 1: GitHub Container Registry\*\*

```yaml

\# Workflow already has GITHUB\_TOKEN

password: ${{ secrets.GITHUB\_TOKEN }}

```



\*\*Option 2: Manual Login\*\*

```bash

echo $GITHUB\_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

```



\*\*Option 3: Check Package Permissions\*\*

\- Go to repository Settings → Actions → General

\- Enable "Read and write permissions"



---



\#### \*\*Issue 4: Image Too Large\*\*



\*\*Symptom:\*\* Image size > 1GB



\*\*Diagnosis:\*\*

```bash

docker images | grep ml-service

docker history ml-service:latest

```



\*\*Solutions:\*\*

1\. Use multi-stage build

2\. Use `-slim` base image

3\. Add .dockerignore

4\. Use `--no-cache-dir` in pip install

5\. Remove unnecessary files in Dockerfile



---



\#### \*\*Issue 5: Container Exits Immediately\*\*



\*\*Symptom:\*\*

```bash

docker run ml-service:latest

\# Container exits with code 0 or 1

```



\*\*Diagnosis:\*\*

```bash

\# Check logs

docker logs <container-id>



\# Run interactively

docker run -it ml-service:latest /bin/bash

```



\*\*Common causes:\*\*

\- Missing model.pkl

\- Port already in use

\- Python errors at startup



\*\*Solution:\*\*

```dockerfile

\# Add debugging

CMD \["python", "-u", "app.py"]  # -u for unbuffered output

```



---



\#### \*\*Issue 6: Health Check Failing\*\*



\*\*Symptom:\*\* Container marked unhealthy



\*\*Check:\*\*

```bash

docker ps  # Look at STATUS column

docker inspect <container-id> | grep Health

```



\*\*Solutions:\*\*

\- Increase health check timeout

\- Verify /health endpoint works

\- Check if service is actually running

```dockerfile

\# Adjust health check

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s \\

&nbsp;   CMD curl -f http://localhost:5000/health || exit 1

```



---



\#### \*\*Issue 7: Version Tag Not Triggering Build\*\*



\*\*Symptom:\*\* Pushed v1.0.0 tag, no workflow run



\*\*Check:\*\*

```yaml

\# Workflow trigger must include tags

on:

&nbsp; push:

&nbsp;   tags:

&nbsp;     - 'v\*.\*.\*'  # Must match your tag format

```



\*\*Solution:\*\*

```bash

\# Delete and recreate tag

git tag -d v1.0.0

git push origin :refs/tags/v1.0.0



\# Create correctly formatted tag

git tag v1.0.0

git push origin v1.0.0

```



---



\### Getting Help



\*\*Check Logs:\*\*

```bash

\# Local Docker logs

docker logs <container-id>



\# CI/CD logs

GitHub → Actions → Click failed workflow → View logs

```



\*\*Useful Commands:\*\*

```bash

\# Build with verbose output

docker build --progress=plain -t test .



\# Test container interactively

docker run -it --entrypoint /bin/bash ml-service:latest



\# Check running processes in container

docker exec <container-id> ps aux

```



---



\## Appendix: Quick Reference



\### Build Commands

```bash

\# Local build

docker build -t ml-service:local .



\# Run locally

docker run -p 5000:5000 ml-service:local



\# Test

curl http://localhost:5000/health

```



\### CI/CD Commands

```bash

\# Create version tag

git tag v1.0.0

git push origin v1.0.0



\# Check workflow status

\# Go to: github.com/user/repo/actions

```



\### Registry Commands

```bash

\# Pull image

docker pull ghcr.io/parthpatel0226/mlops-milestone2-cicd:v1.0.0



\# List tags

\# Visit: github.com/user/repo/pkgs/container/mlops-milestone2-cicd

```



---



\*\*End of Runbook\*\*

