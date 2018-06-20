from setuptools import setup

with open("readme.md", "r") as fh:
    long_description = fh.read()

setup(
    name='liteflow.providers.azure',
    version='0.2',
    description='Azure queue and distributed lock providers for LiteFlow',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Daniel Gerlag',
    author_email='daniel@gerlag.ca',
    license='MIT',
    namespace_packages=['liteflow'],
    packages=['liteflow.providers.azure'],
    zip_safe=False,
    install_requires=[
        'liteflow.core>=0.2',
        'azure-storage-blob>=1.1.0',
        'azure-storage-queue>=1.1.0',
        'python-interface>=1.4.0'
    ],
    url="https://github.com/danielgerlag/liteflow",
    python_requires='>=3.6',
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )
)