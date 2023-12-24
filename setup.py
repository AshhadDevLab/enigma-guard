from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='enigma-guard',
    version='1.0.0',
    author='Ashhad Ahmed',
    author_email='ashhadahmed776@outlook.com',
    description='A versatile encryption and decryption tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/your_username/enigma-guard',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
)
