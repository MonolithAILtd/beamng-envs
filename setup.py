from os import path

import setuptools

from beamng_envs import __VERSION__

try:
    this_directory = path.abspath(path.dirname(__file__))
    with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ''

REQS_CORE = ["beamngpy==1.24", "numpy", "gym"]
RES_FULL = ["mlflow", "tqdm"]

setuptools.setup(
    name="beamng_envs",
    version=__VERSION__,
    author_email="",
    description="Simulation environments using BeamNG",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MonolithAILtd/beamng_envs",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
    install_requires=REQS_CORE,
    extras_require={'full': RES_FULL}
)
