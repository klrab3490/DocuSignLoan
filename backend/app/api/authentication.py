from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
def login(credentials: dict):
    return {"message": "Login successful", "credentials": credentials}

@router.post("/request-otp")
def request_otp(email: str):
    return {"message": "OTP requested", "email": email}

@router.post("/verify-otp")
def verify_otp(email: str, otp: str):
    return {"message": "OTP verified", "email": email, "otp": otp}

@router.post("/logout")
def logout():
    return {"message": "Logout successful"}

@router.post("/refresh-token")
def refresh_token():
    return {"message": "Token refreshed successfully"}
