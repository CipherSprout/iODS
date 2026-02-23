from fastapi import Depends, Header, HTTPException, status

from iods.core.config import Settings, get_settings



def get_app_settings() -> Settings:
    return get_settings()



def require_api_key(
    settings: Settings = Depends(get_app_settings),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or missing API key",
        )
