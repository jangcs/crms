#!/bin/bash

echo "* CRMS test program"
echo "---- git repository and dvc repository must be created before crms test runs"

dir=$1

if [ -d $dir ];
then
	echo "* directory(""$dir"") Exists.... Aborting test !!!"
	exit 1
fi

echo "------------------------------------------------------------------------------------------"
echo "* Not exist. Make dir(""$dir"")" 
mkdir $dir

echo "* Change working directory to" $dir
cd $dir
echo "* Working directory is" "`pwd`"

wd="`pwd`"

echo "------------------------------------------------------------------------------------------"
echo "* Copy a model for test(m1.pth)"
cp ../src/crms/other_data/m1.pth $wd


echo "------------------------------------------------------------------------------------------"
echo "* CRMS config"
#../crms conf git@github.com:jangcs/"$dir".git gs://cr-model-test/models/$dir
crms conf git@github.com:jangcs/"$dir".git gs://cr-model/$dir

echo "------------------------------------------------------------------------------------------"
echo "* CRMS init with model name(""$dir"")"
crms init $dir


echo "------------------------------------------------------------------------------------------"
echo "* CRMS add a model file"
crms add m1.pth


echo "------------------------------------------------------------------------------------------"
echo "* CRMS push (version 0.1)"
crms push v0.1 


echo "------------------------------------------------------------------------------------------"
echo "* CRMS list"
crms list

echo "------------------------------------------------------------------------------------------"
echo "* CRMS desc a model"
crms desc $dir



echo "------------------------------------------------------------------------------------------"
echo "* Copy a model2 for test(m2.pth)"
cp ../src/crms/other_data/m2.pth $wd


echo "------------------------------------------------------------------------------------------"
echo "* CRMS add a model file"
crms add m2.pth


echo "------------------------------------------------------------------------------------------"
echo "* CRMS push (version 0.2)"
crms push v0.2 


echo "------------------------------------------------------------------------------------------"
echo "* CRMS list"
crms list

echo "------------------------------------------------------------------------------------------"
echo "* CRMS desc a model"
crms desc $dir
