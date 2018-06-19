from setuptools import setup

setup(
    name='liteflow.core',
    version='0.2',
    description='Workflow library with pluggable persistence and scale out support',
    author='Daniel Gerlag',
    author_email='daniel@gerlag.ca',
    license='MIT',
    namespace_packages=['liteflow'],
    packages=['liteflow.core'],
    zip_safe=False,
    install_requires=[
        'python-interface>=1.4.0'
    ],
    url="https://github.com/danielgerlag/liteflow",
    keywords="workflow",
    python_requires='>=3.6'
)