import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    author='John Jung',
    author_email='jej@uchicago.edu',
    description='Scripts to validate digital collections before converting them to OCFL',
    install_requires=[
        'cryptography==3.2',
        'docopt',
        'lxml',
        'paramiko',
        'Pillow'
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    name='Digital Collection Validators',
    packages=setuptools.find_packages(),
    url='https://github.com/johnjung/digital_collection_validators',
    version='0.0.1'
)
