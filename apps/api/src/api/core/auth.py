from fastapi import Header, HTTPException

# Simulate catalog
TENANTS = {"tenant_alpha": "key_123", "tenant_beta": "key_456"}


async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key not in TENANTS.values():
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return [k for k, v in TENANTS.items() if v == x_api_key][0]
