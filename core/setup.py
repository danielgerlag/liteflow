from setuptools import setup

with open("readme.md", "r") as fh:
    long_description = fh.read()

setup(
    name='liteflow.core',
    version='0.3.1',
    description='Workflow library with pluggable persistence and scale out support',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Daniel Gerlag',
    author_email='daniel@gerlag.ca',
    license='MIT',
    namespace_packages=['liteflow'],
    packages=[
        'liteflow.core',
        'liteflow.core.abstractions',
        'liteflow.core.builders',
        'liteflow.core.models',
        'liteflow.core.primitives',
        'liteflow.core.services'
    ],
    zip_safe=False,
    install_requires=[
        'python-interface>=1.4.0'
    ],
    url="https://github.com/danielgerlag/liteflow",
    keywords="workflow",
    python_requires='>=3.6',
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )
)