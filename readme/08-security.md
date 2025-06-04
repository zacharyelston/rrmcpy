# Security Considerations

## Credential Management

The Redmine MCP Server requires API credentials to interact with your Redmine instance. These credentials should be managed securely at all times.

### Required Credentials

| Credential | Purpose | Environment Variable |
|------------|---------|----------------------|
| Redmine URL | The URL of your Redmine instance | `REDMINE_URL` |
| API Key | Authentication token for API access | `REDMINE_API_KEY` |

### Best Practices

1. **Environment Variables (Preferred Method)**
   ```bash
   export REDMINE_URL="https://your-redmine-instance.com"
   export REDMINE_API_KEY="your-api-key-here"
   ```

2. **Local Development**
   - Store credentials in a `.env` file
   - Add `.env` to your `.gitignore`
   - Use a tool like `python-dotenv` to load variables:
     ```python
     from dotenv import load_dotenv
     load_dotenv()  # Load variables from .env
     ```

3. **CI/CD Pipelines**
   - Use repository secrets (GitHub Actions, GitLab CI, etc.)
   - Never expose credentials in logs or build artifacts
   - Reference example in `.github/workflows/build-and-test.yml`

4. **Docker Environments**
   - Pass credentials as environment variables:
     ```bash
     docker run -e REDMINE_URL=https://example.com -e REDMINE_API_KEY=your_key your_image
     ```
   - Use Docker secrets or environment files for docker-compose:
     ```yaml
     services:
       redmine-mcp:
         env_file: .env.production
     ```

5. **Production Deployments**
   - Use a secrets management service (AWS Secrets Manager, HashiCorp Vault, etc.)
   - Rotate API keys periodically
   - Use the principle of least privilege for API keys

### Security Warnings

- Never commit API keys to version control
- Never hardcode credentials in source code or configuration files
- Never log credentials in output or debug messages
- Be cautious with API keys in script arguments or command-line parameters

## Network Security

- The MCP server uses HTTPS for all API communication with Redmine
- Verify TLS certificates to prevent man-in-the-middle attacks
- Consider network-level restrictions for production deployments

## Access Control

- Use API keys with appropriate permissions
- Follow the principle of least privilege
- For shared environments, consider using dedicated service accounts
- Review Redmine permissions regularly

Remember that your API key provides access to all resources the associated user can access in Redmine. Treat it with the same care as a password.
