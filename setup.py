from setuptools import find_packages, setup


install_requires = [
    'dvc==2.15.0',
    'GitPython==3.1.27',
    'firebase-admin==5.2.0',
    'protobuf==3.20.1'
]

setup(
    name='crms',
    version='1.0',
    description='Cloud Robot Model Sharing Middleware',
    author='jangcs',
    author_email='jangcs@etri.re.kr',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    package_data={'crms': ['other_data/*.pth']},
    python_requires='>=3.8',
    install_requires=install_requires,
    entry_points = { 'console_scripts': ['crms=crms.crms:main'],
    },
)
### [출처] python package 만들어서 사용하기 (1)|작성자 키리
### https://blog.naver.com/lccandol/222651163325


