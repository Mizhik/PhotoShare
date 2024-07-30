from datetime import datetime, timedelta
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from typing import Optional
from jose import JWTError, jwt

from src.configuration.settings import config


class Auth:
    """
    Handles authentication-related operations including password hashing, 
    token creation, and user verification.

    **Attributes:**

    - `pwd_context` (CryptContext): Provides methods for hashing and verifying passwords.
    - `oauth2_scheme` (OAuth2PasswordBearer): OAuth2 scheme for token-based authentication.
    - `SECRET_KEY` (str): Secret key used for encoding JWT tokens.
    - `ALGORITHM` (str): Algorithm used for encoding JWT tokens.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

    SECRET_KEY = config.AUTH_SECRET_KEY
    ALGORITHM = config.AUTH_ALGORITHM

    def verify_password(self, plain_password, hashed_password):
        """
        Verifies if the plain password matches the hashed password.

        **Parameters:**

        - `plain_password` (str): The plain text password to verify.
        - `hashed_password` (str): The hashed password to compare against.

        **Returns:**

        - bool: `True` if the passwords match, `False` otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Hashes a plain text password.

        **Parameters:**

        - `password` (str): The plain text password to hash.

        **Returns:**

        - str: The hashed password.
        """
        return self.pwd_context.hash(password)

    def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        Creates an access token for authentication.

        **Parameters:**

        - `data` (dict): Data to encode in the token.
        - `expires_delta` (Optional[float]): The expiration time in seconds. If `None`, defaults to 15 minutes.

        **Returns:**

        - str: The encoded JWT access token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now() + timedelta(minutes=15)
        to_encode.update(
            {"iat": datetime.now(), "exp": expire, "scope": "access_token"}
        )
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_access_token

    @staticmethod
    def get_current_user_with_token(token: str) -> Optional[str]:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to verify credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        """
        Extracts the current user's email from the token.

        **Parameters:**

        - `token` (str): The JWT token to decode.

        **Returns:**

        - Optional[str]: The email address of the current user if the token is valid; otherwise, `None`.

        **Raises:**

        - HTTPException: If the token is invalid or expired, raises a 401 Unauthorized exception.
        """
        try:
            payload = jwt.decode(
                token,
                config.AUTH_SECRET_KEY,
                algorithms=[config.AUTH_ALGORITHM],
            )
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
            return email
        except JWTError:
            raise credentials_exception

auth_service = Auth()
