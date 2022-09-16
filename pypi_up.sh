#!/usr/bin/env bash

rm -rf build dist
python3 setup.py sdist bdist_wheel

twine="`pip3 list | grep twine`"
if [[ -z ${twine} ]];then
	pip3 install twine
fi

python3 -m twine upload dist/* --verbose
