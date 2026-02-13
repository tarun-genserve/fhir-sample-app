# Epic FHIR Backend API

A FastAPI application for backend authentication with Epic FHIR using OAuth2 JWT client assertions following the SMART Backend Services specification.

## 📋 Current Status

- ✅ FastAPI server operational on port 8001
- ✅ JWT assertion generation with RS384 signing
- ✅ Environment-based configuration
- ✅ Health check endpoint
- ✅ Authentication endpoint
- ✅ Debug endpoints for troubleshooting
- ⚠️ Epic client registration pending (invalid_client error)

## 📁 Project Structure

```
fhir-sample-app/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app with route registration
│   ├── config.py            # Environment variable configuration (no Pydantic)
│   ├── models.py            # Pydantic response models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py        # GET /health - Health check
│   │   ├── auth.py          # POST /auth/token - Epic token endpoint
│   │   └── debug.py         # Debug endpoints for JWT/key inspection
│   └── services/
│       ├── __init__.py
│       └── epic_auth.py     # JWT builder & Epic OAuth2 logic
├── .keys/                   # Private & public key storage (gitignored)
│   ├── privatekey.pem
│   └── publickey.pem
├── keys/                    # Alternative key location
│   └── private.pem
├── .env                     # Environment variables (gitignored)
├── .env.example             # Template for .env
├── .gitignore
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## 🚀 Setup & Installation

### 1. Create Conda Environment

```bash
conda create -n fhir-app python=3.11 -y
conda activate fhir-app
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `python-dotenv` - Environment variable loader
- `python-jose[cryptography]` - JWT encoding/decoding with RS384
- `requests` - HTTP client for Epic API calls
- `pydantic` - Data validation

### 3. Configure Environment Variables

Your `.env` file should contain:

```env
EPIC_CLIENT_ID=your-epic-client-id
EPIC_CLIENT_ID_NON_PROD=36914b8f-56b7-4212-84d2-a70d48674af9
EPIC_PRIVATE_KEY_PATH=./.keys/privatekey.pem
EPIC_TOKEN_ENDPOINT=https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token
```

**Configuration Details:**
- `EPIC_CLIENT_ID`: Production Epic client ID
- `EPIC_CLIENT_ID_NON_PROD`: Non-production/sandbox client ID (currently in use)
- `EPIC_PRIVATE_KEY_PATH`: Path to RS384 private key (relative or absolute)
- `EPIC_TOKEN_ENDPOINT`: Epic OAuth2 token endpoint (defaults to sandbox)

### 4. Key Management

**Your Keys:**
- Private key: `.keys/privatekey.pem`
- Public key: `.keys/publickey.pem`

**To generate new keys:**
```bash
# Generate private key
openssl genrsa -out .keys/privatekey.pem 2048

# Extract public key
openssl rsa -in .keys/privatekey.pem -pubout -out .keys/publickey.pem
```

## 🏃 Running the Application

### Start Server

```bash
conda activate fhir-app
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Access Points:**
- API Root: http://localhost:8001/
- Interactive Docs: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## 🔌 API Endpoints

### Production Endpoints

#### `GET /health/`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

#### `POST /auth/token`
Obtain OAuth2 access token from Epic using JWT client assertion.

**Response (Success):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "system/*.read"
}
```

**Response (Current - Invalid Client):**
```json
{
  "detail": "Failed to obtain token: Epic returned 400: {'error': 'invalid_client', 'error_description': None}"
}
```

### Debug Endpoints

#### `GET /debug/jwt`
Inspect the JWT assertion being generated.

**Response:**
```json
{
  "jwt_assertion": "eyJhbGciOiJSUzM4NCIsInR5cCI6IkpXVCJ9...",
  "decoded_payload": {
    "iss": "36914b8f-56b7-4212-84d2-a70d48674af9",
    "sub": "36914b8f-56b7-4212-84d2-a70d48674af9",
    "aud": "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token",
    "iat": 1739476234,
    "exp": 1739476534,
    "jti": "36914b8f-56b7-4212-84d2-a70d48674af9-1739476234.123"
  },
  "config": {
    "client_id": "36914b8f-56b7-4212-84d2-a70d48674af9",
    "token_endpoint": "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token",
    "key_path": "./.keys/privatekey.pem"
  }
}
```

#### `GET /debug/public-key`
Retrieve your public key for Epic registration.

**Response:**
```json
{
  "public_key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBg...\n-----END PUBLIC KEY-----",
  "instructions": "Copy the public_key value above and register it with Epic at their FHIR sandbox portal",
  "client_id": "36914b8f-56b7-4212-84d2-a70d48674af9"
}
```

#### `POST /debug/token-request`
View the token request being sent to Epic (without actually sending).

**Response:**
```json
{
  "endpoint": "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token",
  "method": "POST",
  "data": {
    "grant_type": "client_credentials",
    "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
    "client_assertion": "eyJhbGciOiJSUzM4NCIsInR5cCI6IkpXVCJ9.eyJpc3Mi...",
    "scope": "system/*.read"
  },
  "note": "client_assertion is truncated for display"
}
```

## 🔐 Epic FHIR Integration

### OAuth2 Flow (SMART Backend Services)

1. **Build JWT Assertion**
   - Algorithm: RS384
   - Claims: `iss`, `sub`, `aud`, `iat`, `exp`, `jti`
   - Signed with your private key

2. **Request Access Token**
   - Endpoint: `POST https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token`
   - Grant type: `client_credentials`
   - Client assertion type: `urn:ietf:params:oauth:client-assertion-type:jwt-bearer`
   - Scope: `system/*.read`

3. **Use Access Token**
   - Include in FHIR API requests: `Authorization: Bearer <token>`

### Epic Registration Steps

1. **Visit Epic's FHIR Portal**
   - Sandbox: https://fhir.epic.com/

2. **Register Your Application**
   - Application name: "FHIR Sample App"
   - Client ID: `36914b8f-56b7-4212-84d2-a70d48674af9` (or your assigned ID)

3. **Upload Public Key**
   - Get your key: http://localhost:8001/debug/public-key
   - Copy the `public_key` value
   - Paste into Epic's application configuration

4. **Configure Scopes**
   - Request: `system/*.read` (or as needed)

5. **Test Connection**
   - Call: `POST http://localhost:8001/auth/token`
   - Should receive access token instead of `invalid_client`

## 🧪 Testing

### Quick Test Commands

```bash
# Health check
curl http://localhost:8001/health/

# Get public key for Epic registration
curl http://localhost:8001/debug/public-key

# Inspect JWT being generated
curl http://localhost:8001/debug/jwt

# Request Epic token
curl -X POST http://localhost:8001/auth/token
```

### Using Access Token with FHIR API

```bash
# Get access token
TOKEN=$(curl -s -X POST http://localhost:8001/auth/token | jq -r .access_token)

# Query Epic FHIR API
curl -H "Authorization: Bearer $TOKEN" \
     https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Patient/12345
```

## 🐛 Troubleshooting

### Current Known Issue

**Error:** `invalid_client` from Epic
**Cause:** Client ID not registered or public key not uploaded to Epic
**Resolution:** Complete Epic registration steps above

### Common Issues

| Issue | Solution |
|-------|----------|
| `FileNotFoundError: privatekey.pem` | Verify `EPIC_PRIVATE_KEY_PATH` in `.env` points to correct location |
| `PydanticImportError: BaseSettings` | Fixed - using `os.getenv()` instead |
| `Connection refused on port 8001` | Ensure server is running: `uvicorn app.main:app --reload --port 8001` |
| `invalid_client` from Epic | Upload public key and verify client ID at Epic portal |

## 🔒 Security Best Practices

- ✅ `.env` and `.keys/` are gitignored
- ✅ Private keys never committed to version control
- ✅ Environment-based configuration
- ⚠️ Debug endpoints should be disabled in production
- ⚠️ Implement rate limiting for production
- ⚠️ Add request/response logging
- ⚠️ Use secure key storage (e.g., Azure Key Vault) in production

## 🛠️ Development

### Adding New Endpoints

1. Create route file: `app/routes/your_route.py`
2. Define router and endpoints
3. Register in `app/main.py`:
   ```python
   from app.routes import your_route
   app.include_router(your_route.router, prefix="/your-prefix", tags=["tag"])
   ```

### Adding New Services

1. Create service file: `app/services/your_service.py`
2. Implement business logic
3. Import in routes as needed

### Code Structure

```
app/
├── config.py        # Configuration class using os.getenv()
├── models.py        # Pydantic models for request/response validation
├── main.py          # FastAPI app initialization & route registration
├── routes/          # API endpoint definitions
└── services/        # Business logic & external API interactions
```

## 📝 Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EPIC_CLIENT_ID` | No | `""` | Production Epic client ID |
| `EPIC_CLIENT_ID_NON_PROD` | Yes | `""` | Non-production client ID (currently active) |
| `EPIC_PRIVATE_KEY_PATH` | Yes | `""` | Path to RS384 private key file |
| `EPIC_TOKEN_ENDPOINT` | No | Epic sandbox URL | Epic OAuth2 token endpoint |

### Key Files

| File | Purpose | Gitignored |
|------|---------|-----------|
| `.env` | Environment variables | ✅ Yes |
| `.keys/privatekey.pem` | RS384 private key | ✅ Yes |
| `.keys/publickey.pem` | RS384 public key | ✅ Yes |
| `.env.example` | Template for .env | ❌ No |

## 📚 Resources

- [Epic FHIR Documentation](https://fhir.epic.com/)
- [SMART Backend Services Spec](http://hl7.org/fhir/uv/bulkdata/authorization/index.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [JWT.io - Debugger](https://jwt.io/)

## 🎯 Roadmap

- [ ] Complete Epic client registration
- [ ] Add FHIR API query endpoints
- [ ] Implement token caching/refresh
- [ ] Add comprehensive error handling
- [ ] Add request/response logging
- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Add API rate limiting
- [ ] Add health check metrics
- [ ] Production deployment guide

## 📄 License

MIT
