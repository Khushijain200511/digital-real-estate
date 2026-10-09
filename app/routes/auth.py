from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from bson import ObjectId
from app.schemas.auth import UserRegister, UserLogin, UserResponse
from app.utils.password import hash_password, verify_password
from app.utils.jwt import create_access_token, verify_access_token
from app.database import user_collection

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@router.post("/register")
async def register(user: UserRegister):
    
    existing = await user_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    
    existing_mobile = await user_collection.find_one({"mobile": user.mobile})
    if existing_mobile:
        raise HTTPException(status_code=400, detail="Mobile already registered")
    
    
    user_dict = user.dict()
    user_dict["password"] = hash_password(user.password)
    user_dict["is_verified"] = False        
    user_dict["created_at"] = datetime.utcnow()
    
    result = await user_collection.insert_one(user_dict)
    
    return {
        "user_id": str(result.inserted_id),      
        "requires_verification": True              
    }


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
   
    user = await user_collection.find_one({"email": form_data.username})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
   
    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
   
    token = create_access_token({
        "sub": str(user["_id"]),
        "email": user["email"],
        "role": user["role"]
    })
    
    return {
        "success": True,
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    }


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = await user_collection.find_one({"_id": ObjectId(payload["sub"])})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user
from fastapi import HTTPException

def require_seller(current_user: dict = Depends(get_current_user)):
    """Only allow sellers to proceed."""
    if current_user.get("role") != "seller":
        raise HTTPException(
            status_code=403,
            detail="Only sellers can perform this action"
        )
    return current_user
from datetime import datetime, timedelta
from app.schemas.auth import (
    UserRegister, UserLogin, UserResponse,
    ForgotPasswordRequest, VerifyResetTokenRequest, ResetPasswordRequest
)
from app.utils.password import hash_password, verify_password, generate_reset_token



@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    
    
    user = await user_collection.find_one({"email": request.email})
    
    
    if not user:
        return {
            "success": True,
            "message": "If this email is registered, a reset link has been sent."
        }
    
    
    token = generate_reset_token()
    expires_at = datetime.utcnow() + timedelta(minutes=15)
    
    
    await user_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "reset_token": token,
            "reset_token_expires": expires_at
        }}
    )
    
   
    reset_link = f"http://localhost:5173/reset-password?token={token}"
    
    print("\n" + "="*60)
    print("🔐 PASSWORD RESET LINK (EMAIL STUB)")
    print("="*60)
    print(f"To: {request.email}")
    print(f"Reset Link: {reset_link}")
    print(f"Token: {token}")
    print(f"Expires: {expires_at}")
    print("="*60 + "\n")
    
    return {
        "success": True,
        "message": "If this email is registered, a reset link has been sent.",
        "dev_token": token 
    }


@router.post("/verify-reset-token")
async def verify_reset_token(request: VerifyResetTokenRequest):
   
    
    user = await user_collection.find_one({"reset_token": request.token})
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")
    
   
    if user.get("reset_token_expires") and user["reset_token_expires"] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token has expired")
    
    return {
        "success": True,
        "message": "Token is valid",
        "email": user["email"]
    }


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
   
    
    user = await user_collection.find_one({"reset_token": request.token})
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")
    
  
    if user.get("reset_token_expires") and user["reset_token_expires"] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token has expired")
    
   
    await user_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"password": hash_password(request.new_password)},
            "$unset": {"reset_token": "", "reset_token_expires": ""}
        }
    )
    
    return {
        "success": True,
        "message": "Password reset successfully. You can now log in."
    }
from app.schemas.auth import (
    UserRegister, UserLogin, UserResponse,
    ForgotPasswordRequest, VerifyResetTokenRequest, ResetPasswordRequest,
    SendOTPRequest, VerifyOTPRequest   
)
from app.utils.otp import create_otp, verify_otp_code   

@router.post("/send-otp")
async def send_otp(request: SendOTPRequest):
   
    otp = await create_otp(request.destination, request.purpose)
    
   
    print("\n" + "="*60)
    print(f"📱 OTP SENT ({request.channel.upper()})")
    print("="*60)
    print(f"To: {request.destination}")
    print(f"Purpose: {request.purpose}")
    print(f"OTP: {otp}")
    print(f"Expires in: 5 minutes")
    print("="*60 + "\n")
    
    response = {
        "message": "OTP sent",
        "expires_in": 300   # 5 minutes in seconds
    }
    
 
    response["dev_otp"] = otp
    
    return response



@router.post("/verify-otp")
async def verify_otp(request: VerifyOTPRequest):
   
    
    is_valid = await verify_otp_code(
        request.destination,
        request.otp,
        request.purpose
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP"
        )
    
  
    if request.purpose == "registration":
       
        user = await user_collection.find_one({
            "$or": [
                {"email": request.destination},
                {"mobile": request.destination}
            ]
        })
        
        if user:
            await user_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"is_verified": True}}
            )
    
    return {
        "verified": True,
        "message": "OTP verified successfully"
    }