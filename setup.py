import setuptools

setuptools.setup(
    name="spot",
    version="0.0.1",
    description="spot instance creation helper",
    url="https://github.com/haydenjeune/spot",
    author="Hayden Jeune",
    install_requires=["Click", "tabulate", "boto3", "pyyaml"],
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["spot = spot.main:main"]},
)