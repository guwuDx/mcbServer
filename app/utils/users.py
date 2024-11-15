from passlib.context import CryptContext

pswd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str: # Hash the password
    return pswd_context.hash(password)

def verify_password(password: str, hash: str) -> bool: # Verify the password
    return pswd_context.verify(password, hash)