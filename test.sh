#!/bin/bash

echo "* CRMS test program"
echo "---- git repository and dvc repository must be created before crms test runs"

dir=$1

if [ -d $dir ];
then
	echo "* directory(""$dir"") Exists.... Aborting test !!!"
	exit 1
fi

echo "* Not exist. Make dir(""$dir"")" 
mkdir $dir


echo "* Copy a model for test(m1.pth)"
cp m1.pth $dir


echo "* Change working directory to" $dir
cd $dir
echo "* Working directory is" "`pwd`"


echo "* CRMS config"
#../crms conf git@github.com:jangcs/"$dir".git gs://cr-model-test/models/$dir
../crms conf git@github.com:jangcs/"$dir".git gs://cr-model/$dir
#../crms conf https://github.com/jangcs/"$dir".git gs://cr-model-test/$dir

echo "* CRMS init with model name(""$dir"")"
../crms init $dir


echo "* CRMS add a model file"
../crms add m1.pth


echo "* CRMS push (version 0.1)"
../crms push v0.1 


echo "* CRMS list"
../crms list

echo "* CRMS desc a model"
../crms desc $dir


