# MCP Server Debugging Guide

This guide documents common issues encountered with the Redmine MCP Server and their solutions, providing developers with a reference for troubleshooting.

## Table of Contents

1. [Common Issues](#common-issues)
   - [Missing Constructor Parameters](#missing-constructor-parameters)
2. [Troubleshooting Steps](#troubleshooting-steps)
3. [Docker Debugging](#docker-debugging)

## Common Issues

### Missing Constructor Parameters

#### Issue: BaseService.__init__() missing required positional argument: 'config'

**Symptoms:**
- Server fails to start with error: `BaseService.__init__() missing 1 required positional argument: 'config'`
- This typically occurs when instantiating service classes without providing all required parameters

**Root Cause:**
This issue was encountered in the `feature-766-enhance-search-functionality` branch. The `SearchService` class, which inherits from `BaseService`, was being instantiated in the `register_search_tools` method with only the client parameter:

```python
# Incorrect instantiation
self.search_service = SearchService(client)
```

However, the `BaseService` constructor requires three parameters:
```python
def __init__(self, config: Any, client: Any, logger: logging.Logger):
    self.config = config
    self.client = client
    self.logger = logger
```

**Solution:**
Update the service instantiation to include all required parameters:

```python
# Correct instantiation
self.search_service = SearchService(
    config=self.client_manager.config,
    client=client,
    logger=self.logger
)
```

**Prevention:**
- When creating new service classes that inherit from `BaseService`, always ensure they receive all required parameters.
- If you modify the `BaseService` constructor, update all instantiations throughout the codebase.
- Run integration tests before building new images to catch these issues early.

## Troubleshooting Steps

When debugging MCP server issues:

1. **Check Environment Variables**:
   ```bash
   docker exec <container_id> env | grep REDMINE
   ```

2. **Inspect Logs**:
   ```bash
   docker logs <container_id>
   ```

3. **Test Server Initialization**:
   ```bash
   docker exec -it <container_id> python -c "from src.server import run_server; server = run_server(); print('Server initialized successfully!')"
   ```

4. **Debug Specific Components**:
   ```bash
   docker exec -it <container_id> python -c "from src.server import RedmineMCPServer; server = RedmineMCPServer(); print(server)"
   ```

## Docker Debugging

### Creating a Debug Image

If you need to fix an issue in a container:

1. Create a temporary container:
   ```bash
   docker run -d --name temp-fix <problematic_image> sleep 3600
   ```

2. Copy files out for editing:
   ```bash
   docker cp temp-fix:/app/src/path/to/file.py /tmp/file.py
   ```

3. Edit the files locally

4. Copy files back:
   ```bash
   docker cp /tmp/file.py temp-fix:/app/src/path/to/file.py
   ```

5. Create a fixed image:
   ```bash
   docker commit temp-fix <image_name>:fixed
   ```

6. Test the fixed image:
   ```bash
   docker run -e REDMINE_URL=<url> -e REDMINE_API_KEY=<key> <image_name>:fixed
   ```

### Identifying Changes Between Images

To compare differences between image versions:

```bash
docker run --rm <image1> find /app -type f -name "*.py" | sort > image1_files.txt
docker run --rm <image2> find /app -type f -name "*.py" | sort > image2_files.txt
diff image1_files.txt image2_files.txt
```

---

*Last updated: 2025-08-04*
