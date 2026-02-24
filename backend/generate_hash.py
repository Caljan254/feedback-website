from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = input("aaamumo254: ")
print(pwd_context.hash(password))