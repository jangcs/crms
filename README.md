**CRMS CLI Installation**
===
## (0) Preparation
* (0.1) PIP3 must be prepared.
```sh
sudo apt install python3-pip
```
* (0.2) Git must be prepared and configured
```sh
sudo apt install git
git config --global user.name “Your Name”
git config --global user.email your-email@xxx.com
```

## (1) Install gcloud sdk
* (1.1) Download https://cloud.google.com/sdk/docs/install (Linux 64-bit package)
* (1.2) Extract the downloaded package to ~/google-cloud-sdk
```sh
tar -xf google-cloud-cli-395.0.0-linux-x86_64.tar.gz
```
* (1.3) Add path to .bashrc 
```sh
./google-cloud-sdk/install.sh
```
* (1.4) Setup Google Credential 
    * Download Google Credential file (contact administrator of your Google Cloud Project)
        * Access permission of credential may be one of reading or writing (writing permission is necessary for a full test)
        * In case of reading permission, crms push command is not allowed (crms list/desc/pull commands are allowed) 
    * Default credential for the reader of google cloud robot project is cloudrobotai-reader-cred.zip
        * unzip cloudrobotai-reader-cred.zip 
    * Set GOOGLE_APPLICATION_CREDENTIALS into ~/.bashrc
```sh
export GOOGLE_APPLICATION_CREDENTIALS=”/path/to/<google-cloud-project-credential>.json”
```
* (1.5) bug fix of protobuf
```sh
pip3 install protobuf==3.20.1
pip3 install fsspec==2022.2.0
```
* (1.6) dependency fix for fsspec
```sh
pip3 install fsspec==2022.2.0
```
* (1.7) (optional) Set a environment variable (CRMS_META_REPOSITORY) for Google Firestore (Default='croudrobotai')
```sh
export CRMS_META_REPOSITORY=your-google-cloud-project
```

## (2) Install crms from Github or PyPi 
* (2.1) For full test : Download crms from Github and install with pip3
```sh
git clone https://github.com/jangcs/crms.git
cd crms
pip3 install .
```
* If error occurs during installation in /crms
```sh
pip3 install --upgrade pip
[reboot if necessary, and try to install again]
```
* (2.2) For just install (not for test): Install from PyPi
```sh
pip3 install crms
```


## (3) Install DVC for Google Cloud Storage
```sh
pip3 install dvc[gs]
[reboot if necessary]
```

<!--
## (4) Install required libraries
```sh
pip3 install GitPython
pip3 install firebase_admin
```
-->
## (4) Prepare ssh key for github
* (4.1) SSH key has to be generated for secure connection with github.com    
```
ssh-keygen
ssh-keyscan github.com > ~/.ssh/known_hosts
```
* (4.2) And, the generated SSH key has to be registered to github.com in order to push a model     
    * Login github.com -> Settings/SSH and GPG keys -> [New SSH Key] Button -> Copy the contents of ~/.ssh/id_rsa.pub to Key box -> [Add SSH Key] Button


## (5) Test crms cli
* (5.1) Modify the line in test.sh, 'crms conf git@github.com:IdToBeReplaced/...' to your github account 
```sh
sed -i 's/IdToBeReplaced/<your_github_account>/g' test.sh
```
* (5.2) Add a repository to github (ex. model_test)
    * Login github.com -> [New] Button -> Create a New Repository -> Enter a repository name(ex. model_test) -> [Create repository] Button

* (5.3) Execute test.sh with the name of the added github repository 
```sh
/test.sh model_test
```
