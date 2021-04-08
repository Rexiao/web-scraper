import io

from setuptools import find_packages
from setuptools import setup

setup(
    name="src",
    version="1.0.0",
    license="BSD",
    maintainer="Ang Li",
    maintainer_email="nope",
    description="as 2.1.",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask"],
    extras_require={"test": ["pytest", "coverage"]},
)