rm -rf build dist
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/* --verbose

# https://blessingdev.wordpress.com/2019/05/31/pypi%EB%A1%9C-%ED%8C%A8%ED%82%A4%EC%A7%80-%EB%B0%B0%ED%8F%AC%ED%95%98%EA%B8%B0%EB%82%B4%EA%B0%80-%EB%A7%8C%EB%93%A0-%EB%AA%A8%EB%93%88%EB%8F%84-pip%EB%A1%9C-%EB%8B%A4%EC%9A%B4%EB%B0%9B%EC%9D%84/
