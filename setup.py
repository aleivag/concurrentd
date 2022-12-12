from distutils.core import setup
from pathlib import Path

REQ = Path(__file__).absolute().parent / "requirements.txt"
setup(
    name="concurrentd",
    version="0.1",
    description="sandbox python methods in linux with magic",
    author="Alvaro Leiva Geisse",
    author_email="aleivag@gmail.com",
    url="",
    packages=["concurrentd"],
    install_requires=[f.strip() for f in (REQ.read_text().splitlines())],
)
