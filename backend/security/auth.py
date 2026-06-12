import os
from dotenv import load_dotenv
from fastapi import Header, HTTPException


load_dotenv()

N8N_API_KEY = os.getenv("N8N_API_KEY")


def verify_api_key(x_api_key: str = Header(...)):
    """
    Verifies API key sent by n8n in x-api-key header.
    """

    if not N8N_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="N8N_API_KEY is not configured on the server."
        )

    if x_api_key != N8N_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key."
        )

    return True
