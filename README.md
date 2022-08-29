## Under Re-packaging - Do Not Use This Package Until Completion

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

## (1) Download crms from github and add the PATH to .bashrc
```sh
git clone https://github.com/jangcs/crms.git
```
```sh
cd crms
pip3 install .
```
/// echo "export PATH=\$PATH:$PWD" >> ~/.bashrc
/// source ~/.bashrc

///## (2) Install DVC
///```sh
///pip3 install dvc
///pip3 install dvc[gs]
///[reboot if necessary]
///```

## (3) Install gcloud sdk
* (3.1) Download https://cloud.google.com/sdk/docs/install (Linux 64-bit package)
* (3.2) Extract the downloaded package to ~/google-cloud-sdk
```sh
tar -xf google-cloud-cli-395.0.0-linux-x86_64.tar.gz
```
* (3.3) Add path to .bashrc 
```sh
./google-cloud-sdk/install.sh
```
* (3.4) Setup Google Credential 
    * Download Google Credential file (contact administrator of your Google Cloud Project)
        * Access permission of credential may be one of reading or writing (writing permission is necessary for a full test)
        * In case of reading permission, crms push command is not allowed (crms list/desc/pull commands are allowed) 
    * Set GOOGLE_APPLICATION_CREDENTIALS into ~/.bashrc
```sh
export GOOGLE_APPLICATION_CREDENTIALS=”/path/to/<google-cloud-project-credential>.json”
```
* (3.5) bug fix of protobuf
```sh
pip3 install protobuf==3.20.1
```

## (4) Install required libraries
```sh
pip3 install GitPython
pip3 install firebase_admin
```

## (5) Test crms cli
* SSH key has to be generated for secure connection with github.com    
```
ssh-keygen
ssh-keyscan github.com > ~/.ssh/known_hosts
```
* And, the generated SSH key has to be registered to github.com in order to push a model     
    * Login github.com -> Settings/SSH and GPG keys -> [New SSH Key] Button -> Copy the contents of ~/.ssh/id_rsa.pub to Key box -> [Add SSH Key] Button

* (optional) Set a environment variable (CRMS_META_REPOSITORY) for Google Firestore (Default='croudrobotai')
```sh
export CRMS_META_REPOSITORY=your-google-cloud-project
```
* Add a repository to github (ex. model_test)
* Modify the line in test.sh, 'crms conf git@github.com:IdToBeReplaced/...' to your github account 
```sh
sed -i 's/IdToBeReplaced/<your_github_account>/g' test.sh
```

* Execute test.sh with the name of the added github repository 
```sh
/test.sh model_test
```



