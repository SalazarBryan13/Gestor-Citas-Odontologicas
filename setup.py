from setuptools import setup, find_packages

setup(
    name="gestor-citas",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "python-multipart",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "bcrypt",
        "pytest",
        "httpx",
        "starlette",
        "pydate",
        "flake8",
        "black",
        "jinja2",
        "email-validator"
    ],
    python_requires=">=3.11",
) 