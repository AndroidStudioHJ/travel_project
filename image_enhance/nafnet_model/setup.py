from setuptools import setup, find_packages

setup(
    name="basicsr",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'torch',
        'torchvision',
        'numpy',
        'opencv-python',
        'scipy',
        'tqdm',
        'lmdb',
        'pyyaml',
    ],
) 