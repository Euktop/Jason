from setuptools import setup, find_packages

setup(
    name="jason",
    version="0.1.0",
    description="JSON command executor with Clean Architecture",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Ваше Имя",
    author_email="ваш@email.ru",
    url="https://github.com/Euktop/Jason",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)