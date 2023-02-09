from setuptools import find_packages, setup


install_requires = [
    'dvc==2.15.0',
    'GitPython==3.1.27',
    'firebase-admin==5.2.0',
    'protobuf==3.20.1',
	'requests>=2.28.1',
	'fsspec==2022.2.0'
]

setup(
    name='crms',
    version='2023.02.09',
    description='Cloud Robot Model Sharing Middleware',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='jangcs',
    author_email='jangcs@etri.re.kr',
    url="https://github.com/jangcs/crms",
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    package_data={'crms': ['other_data/*.pth']},
    python_requires='>=3.8',
    install_requires=install_requires,
    entry_points = { 'console_scripts': ['crms=crms.crms:main'],
    },
)

