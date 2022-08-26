#!/usr/bin/env python3

import sys
import os
# import pathlib
import git
from git import Repo
import subprocess
import argparse
import yaml

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

#CRMS_META_REPOSITORY = ''
CRMS_META_REPOSITORY = os.getenv('CRMS_META_REPOSITORY','cloudrobotai')

def append_label_sample(f) :
    f.write('#labels : \n')
    f.write('#  label_key1: lavel_value1\n')
    f.write('#  label_key2: lavel_value2\n')
    f.write('#  resolution: 640x480(sample)\n')

def crms_conf_api(arg_git_remote, arg_dvc_remote) :

    dir_path = os.getcwd()
    #### CRMS Config Directory
    path_crms = os.path.join(dir_path, ".crms")
    if not os.path.exists(path_crms) :
        os.makedirs(path_crms)
        print("The new .crms directory is created !!!")

    git_remote = arg_git_remote
    git_remote_split = git_remote.split(':')
    git_tag = ''
    if len(git_remote_split) > 2 :
        git_tag = git_remote_split[-1]
        del(git_remote_split[-1])
        git_remote = ':'.join(git_remote_split) + '-' + git_tag

    dvc_remote = arg_dvc_remote
    dvc_remote_split = dvc_remote.split(':')
    dvc_tag = ''
    if len(dvc_remote_split) > 2 :
        dvc_tag = dvc_remote_split[-1]
        del(dvc_remote_split[-1])
        dvc_remote = ':'.join(dvc_remote_split) + '-' + dvc_tag

    #### CRMS Config File
    configs = { 'git': {'remote' : git_remote }, 
                'dvc' : {'remote': dvc_remote  },
                'platform': {'architecture':'x86_64',
                             'os': 'linux',
                             'version':'',
                             'device':'cpu'} 
              } 

    path_config = os.path.join(path_crms, "config")
    with open(path_config, 'w') as f:
        yaml.dump(configs, f, sort_keys=False)
        append_label_sample(f)
        
    print("CRMS Configurations are stored into .crms/config !!!")
    
def crms_conf(args):
    crms_conf_api(arg_git_remote = args.git_remote, arg_dvc_remote = args.dvc_remote)
    
def crms_conf_mod_api(arg_git_remote='', arg_dvc_remote=''):

    dir_path = os.getcwd()
    #### CRMS Config Directory
    path_config = os.path.join(dir_path, ".crms", "config")
    if not os.path.exists(path_config) :
        print("CRMS ERROR: crms conf must be called before crms conf_mod")
        sys.exit(-1)

    #### Read CRMS Config File
    with open(path_config) as f:
        configs = yaml.load(f, Loader=yaml.FullLoader)

    if arg_git_remote != None and arg_git_remote != '' :
        configs['git']['remote'] = arg_git_remote
        if 'model' in configs :         # if crms init was called --> model exists
            set_git_remote(arg_git_remote.replace(':','-'))
        else :
            print("git_remote: model is not in config")

    if arg_dvc_remote != None and arg_dvc_remote != '' :
        configs['dvc']['remote'] = arg_dvc_remote
        if 'model' in configs :          # if crms init was called --> model exists   
            set_dvc_remote(arg_dvc_remote.replace(':','-'))
        else :
            print("dvc_remote: model is not in config")


    with open(path_config, 'w') as f:
        yaml.dump(configs, f, sort_keys=False)

        if 'labels' not in configs :
            append_label_sample(f)

    print("CRMS Configurations are modified !!!")


def crms_conf_mod(args):
    
    args_dict = vars(args)
    arg_git_remote = ''
    arg_dvc_remote = ''


    if 'git_remote' in args_dict and args.git_remote != '':
        arg_git_remote = args.git_remote

    if 'dvc_remote' in args_dict and args.dvc_remote != '' :
        arg_dvc_remote = args.dvc_remote

    crms_conf_mod_api(arg_git_remote, arg_dvc_remote)

def set_dvc_remote(dvc_remote):
    #### DVC Remote Add
    p = subprocess.run(["dvc", "remote", "remove",  "storage", "--quiet" ])
    p = subprocess.run(["dvc", "remote", "add",  "-d", "storage", dvc_remote, "--quiet" ])
    # print("Return code : {} = {}".format(type(p.returncode), p.returncode))
    if p.returncode == 0 : # success of subprocess.run
        print("CRMS added DVC remote (" + dvc_remote + ")")
    else: # fail of subprocess.run
        print("CRMS failed to DVC add remote...")
        sys.exit(-1)

def set_git_remote(git_remote):
    dir_path = os.getcwd()
    try :
        repo = Repo(dir_path)
    except git.exc.InvalidGitRepositoryError:
        repo = Repo.init(dir_path)        
        print("CRMS uses Git Local Repository (" + dir_path + ")")        
        print("Git initialized...")
    except git.exc.NoSuchPathError :
        print("Error: git repoistory path could not be accessed by the system.")
        sys.exit(-1)
    except :
        print("Error: Unknown error occured while crms init")
        sys.exit(-1)

    #### git remote add origin ~~~~   # 'git remote add origin ~~ '  must be prepared before 'crms init'
    if len(repo.remotes) > 0 :
        repo.delete_remote('origin')

    origin = repo.create_remote('origin', git_remote)
    print("CRMS added Git remote (" + git_remote + ")")


def crms_init_api(arg_model_name):

    dir_path = os.getcwd()
    #### Checke CRMS Config File Existence
    path_config = os.path.join(dir_path, ".crms", "config")
    if not os.path.exists(path_config) :
        print("CRMS ERROR: crms conf must be called before crms init")
        sys.exit(-1)

    #### Add model_name to crms config file 
    with open(path_config) as f:
        configs = yaml.load(f, Loader=yaml.FullLoader)
        print(configs)

    model_name = arg_model_name
    model_name_split = model_name.split(':')
    last_tag = ''
    if len(model_name_split) > 1 :
        if len(model_name_split) == 2 :
            last_tag = model_name_split[-1]
            del(model_name_split[-1])
            model_name = model_name_split[0]
        else :
            print("CRMS ERROR: model must be a form of <model-name> or <model-name>:<model-tag>")
            sys.exit(-1)

    configs['model'] = {'name': model_name, 'tag':last_tag}
    with open(path_config, 'w') as f:
        yaml.dump(configs, f, sort_keys=False)
        if 'labels' not in configs :
            append_label_sample(f)

    
    #### Git Repository 
    set_git_remote(configs['git']['remote'])

    # try :
    #     repo = Repo(dir_path)  # 'git init '  must be prepared before 'crms init'
    # except git.exc.InvalidGitRepositoryError:
    #     repo = Repo.init(dir_path)        
    #     print("Git initialized...")
    # except git.exc.NoSuchPathError :
    #     print("Error: git repoistory path could not be accessed by the system.")
    #     sys.exit(-1)
    # except :
    #     print("Error: Unknown error occured while crms init")
    #     sys.exit(-1)
    # finally :
    #     print("CRMS uses Git Local Repository (" + dir_path + ")")        

    # #### git remote add origin ~~~~   # 'git remote add origin ~~ '  must be prepared before 'crms init'
    # if len(repo.remotes) > 0 :
    #     repo.delete_remote('origin')

    # origin = repo.create_remote('origin', configs['git']['remote'])


    #### DVC INIT
    p = subprocess.run(["dvc", "init", "--force", "--quiet"])
    # print("Return code : {} = {}".format(type(p.returncode), p.returncode))
    if p.returncode == 0 : # success of subprocess.run
        print("CRMS initialized DVC...")
    else: # fail of subprocess.run
        print("CRMS failed of DVC initialization...")
        sys.exit(-1)

    #### DVC Remote Add
    set_dvc_remote(configs['dvc']['remote'])

#     remotes = repo.remotes # [<git.Remote "origin">, ...]
#     if len(remotes) <= 0 :
#         print("!!!! git remote origin must be added after crms init.")
#         print("!!!! Try: git remote add origin git@github.com:<user_name>/<repository_name.git>")    
# #        sys.exit(-1)
#         pass
#     else:
#         origin = remotes[0]   # <git.Remote "origin">
#         urls = origin.urls    # <generator object Remote.urls at 0x7fa164d235f0>
#         url = next(urls)
#         print("CRMS uses Git Remote (" + url + ")")
#         # with open(path_config, "at+") as f :
#         #     f.write("git_remote : {}\n".format(url))

    if CRMS_META_REPOSITORY != '' :
        firebase_options = {'projectId':CRMS_META_REPOSITORY}
        firebase_app = firebase_admin.initialize_app(options=firebase_options)
        db = firestore.client()
        doc_ref = db.collection('models').document(arg_model_name)   # DocumentReference
        doc_ref.set({'name': model_name, 
                    'git_repository': configs['git']['remote'], 
                    'dvc_repository':configs['dvc']['remote'],
                    'platform': {
                        'architecture' : configs['platform']['architecture'],
                        'os'           : configs['platform']['os'],
                        'version'      : configs['platform']['version'], 
                        'device'       : configs['platform']['device'] 
                    }})

def crms_init(args):
    arg_model_name = args.model_name
    crms_init_api(arg_model_name)

def crms_add_api(arg_model_files):
    # List to be added to Git
    git_add_list = ['.dvcignore', '.dvc/config', '.gitignore', '.crms/config']  # + *.dvc

    # Check model files to be added
    model_files = arg_model_files
    if len(model_files) == 0 :
        print("Error: File list is required to be added.")

    #### Check CRMS Config File Existence
    dir_path = os.getcwd()
    path_config = os.path.join(dir_path, ".crms", "config")
    if not os.path.exists(path_config) :
        print("CRMS ERROR: crms conf must be called before crms init")
        sys.exit(-1)

    #### Add model_name to crms config file 
    with open(path_config) as f:
        configs = yaml.load(f, Loader=yaml.FullLoader)

    if 'model' not in configs :          # if crms init was called --> model exists   
        print("Error: crms init must be called before crms add")

    # open git repo
    dir_path = os.getcwd()
    try :
        repo = Repo(dir_path)  # 'git init'  must be prepared before 'crms init'
    except git.exc.InvalidGitRepositoryError:
        print("Error: Invalid Git Repository. Check crms init was called...")
        sys.exit(-1)
    except git.exc.NoSuchPathError :
        print("Error: git repoistory path could not be access by the system.")
        sys.exit(-1)
    except :
        print("Error: Unknown error occured while crms push")
        sys.exit(-1)

    # dvc add
    p = subprocess.run(["dvc", "add"]  + model_files)
    # print("Return code : {} = {}".format(type(p.returncode), p.returncode))
    if p.returncode == 0 : # success of subprocess.run
        print("CRMS added model files(" + ', '.join(s for s in model_files) + ") to DVC")
    else: # fail of subprocess.run
        print("CRMS failed to add model files...")
        sys.exit(-1)

    # add git_add_list files to git repo index
    for file_name in model_files :
        git_add_list.append( file_name + '.dvc') 

    repo.index.add(git_add_list)
    commitMsg="CRMS model files(" + ', '.join(s for s in model_files) + ") for model(" + configs['model']['name'] + ") are added."
    repo.index.commit(commitMsg)
    print("CRMS added auxiliary files(" + ', '.join(s for s in git_add_list) + ") to GIT")
 
def crms_add(args):
    arg_model_files = args.model_files
    crms_add_api(arg_model_files)


def crms_push_api(arg_version) :

    #### Check CRMS Config File Existence
    dir_path = os.getcwd()
    path_config = os.path.join(dir_path, ".crms", "config")
    if not os.path.exists(path_config) :
        print("CRMS ERROR: crms conf was not called")
        sys.exit(-1)

    #### Add model_name to crms config file 
    with open(path_config) as f:
        configs = yaml.load(f, Loader=yaml.FullLoader)

    if 'model' not in configs :          # if crms init was called --> model exists   
        print("Error: crms init was not called")

    # open git repo
    dir_path = os.getcwd()
    try :
        repo = Repo(dir_path)  # 'git init'  must be prepared before 'crms init'
    except git.exc.InvalidGitRepositoryError:
        print("Error: Invalid Git Repository. Check crms init was called...")
        sys.exit(-1)
    except git.exc.NoSuchPathError :
        print("Error: git repoistory path could not be access by the system.")
        sys.exit(-1)
    except :
        print("Error: Unknown error occured while crms push")
        sys.exit(-1)

    remotes = repo.remotes # [<git.Remote "origin">, ...]
    if len(remotes) <= 0 :
        print("Error: git remote origin must be added before crms push.")
        print("Try: git remote add origin git@github.com:<user_name>/<repository_name.git>")    
        sys.exit(-1)


    tagName = arg_version
    print("Creating TagReference.")
    git.refs.tag.TagReference.create(repo, tagName)

    #origin = repo.remotes.origin
    remote_origin = repo.remotes[0]   # repo.remotes.origin (=origin)
    print("Push to main of remote " + remote_origin.name)

    #origin.push('main')
    print("repo.active_branch.name = " + repo.active_branch.name)
    remote_origin.push(repo.active_branch.name)   # main

    print("Push tag : " + tagName)
    remote_origin.push(tagName)


    # origin = remotes[0]   # <git.Remote "origin">
    # urls = origin.urls    # <generator object Remote.urls at 0x7fa164d235f0>
    # url = next(urls)

    # print("Git Repository URL : " + url)

    # # p = subprocess.run(["dvc", "init"])
    # pass


    #### DVC Push
    p = subprocess.run(["dvc", "push"])
    # print("Return code : {} = {}".format(type(p.returncode), p.returncode))
    if p.returncode == 0 : # success of subprocess.run
        print("CRMS pushes to DVC...")
    else: # fail of subprocess.run
        print("CRMS failed of DVC Push...")
        sys.exit(-1)


    if CRMS_META_REPOSITORY != '' :
        firebase_options = {'projectId':CRMS_META_REPOSITORY}
        firebase_app = firebase_admin.initialize_app(options=firebase_options)
        db = firestore.client()

        last_tag = ''
        if 'tag' in configs['model'] :
            last_tag = configs['model']['tag']

        if last_tag != '' :
            doc_ref = db.collection('models').document(configs['model']['name']+':'+last_tag)   # DocumentReference
        else :
            doc_ref = db.collection('models').document(configs['model']['name'])   # DocumentReference
        doc_ref.update({'latest':tagName, 'versions':firestore.ArrayUnion([tagName])})


    print("CRMS PUSHED....")
    

def crms_push(args):
    arg_version = args.version
    crms_push_api(arg_version)

def crms_pull_api(arg_model_url, arg_version, arg_target=''):
    print("CRMS PULL....")
    
    if arg_target != '' :
        target = arg_target
    else :
        # target = os.path.join( os.getcwd(), args.model_name)
        # target = os.path.join( os.getcwd(), "model_crms")
        target = os.path.join( os.getcwd(), os.path.basename(arg_model_url).split('.')[0] )   # git@github.com:jangcs/KKK.git -> KKK.git -> ['KKK', 'git']
        
    # repo = Repo.clone_from("git@github.com:jangcs/KKK.git", os.getcwd() )
    modified_model_url = arg_model_url.replace('git@github.com:','https://github.com/',1)

    print("crms_pull from "+ modified_model_url)
    repo = Repo.clone_from(modified_model_url, target )

    if arg_version == 'latest' : 
        os.chdir(target)
        p = subprocess.run(["dvc", "pull"])
        if p.returncode == 0 : # success of subprocess.run
            print("CRMS pulled model files from DVC to " + target)
        else: # fail of subprocess.run
            print("CRMS failed to pull model files...")
            sys.exit(-1)
    else :
        past_branch = repo.create_head('crms_target', arg_version)
        repo.heads.crms_target.checkout()

        os.chdir(target)
        p = subprocess.run(["dvc", "pull"])
        if p.returncode == 0 : # success of subprocess.run
            print("CRMS pulled model files from DVC to " + target)
        else: # fail of subprocess.run
            print("CRMS failed to pull model files...")
            sys.exit(-1)

        # repo.heads.master.checkout()
        # repo.delete_head('crms_target')


def crms_pull(args):
    
    if args.target != '' :
        arg_target = args.target
    else :
        # target = os.path.join( os.getcwd(), args.model_name)
        # target = os.path.join( os.getcwd(), "model_crms")
        arg_target = os.path.join( os.getcwd(), os.path.basename(args.model_url).split('.')[0] )   # git@github.com:jangcs/KKK.git -> KKK.git -> ['KKK', 'git']

    arg_model_url = args.model_url
    arg_version = args.version

    crms_pull_api(arg_model_url, arg_version, arg_target)


def crms_desc_api(arg_model_name):
    print("CRMS DESC....")
    
    if CRMS_META_REPOSITORY != '' :
        firebase_options = {'projectId':CRMS_META_REPOSITORY}
        firebase_app = firebase_admin.initialize_app(options=firebase_options)
        db = firestore.client()
        # doc_ref = db.collection('models').document(args.model_name)   # DocumentReference

        doc = db.collection('models').document(arg_model_name).get()   # DocumentReference
        if doc.exists :
            docs = [doc]
        else :
            docs = db.collection('models').where('name', '==', arg_model_name).stream()   # DocumentReference

        for doc in docs:
            print(doc.id)

            d = doc.to_dict()

            print('\tRepository: '+d['git_repository'])


            print('\tVersions')
            versions = d['versions']
            for v in versions :
                print('\t\t' + v)

            latest = d['latest']
            print('\tLatest = ' + latest)
    else :
        print("CRMS_META_REPOSITORY is not defined...")


def crms_desc(args):
    arg_model_name = args.model_name
    crms_desc_api(arg_model_name)
    
def crms_list_api():
    print("CRMS LIST....")
    
    if CRMS_META_REPOSITORY != '' :
        firebase_options = {'projectId':CRMS_META_REPOSITORY}
        firebase_app = firebase_admin.initialize_app(options=firebase_options)
        db = firestore.client()
        # doc_ref = db.collection('models').document(args.model_name)   # DocumentReference

        docs = db.collection('models').list_documents()
        
        for doc in docs:
            print(doc.id)
    else :
        print("CRMS_META_REPOSITORY is not defined...")
   

def crms_list(args):
    crms_list_api()
   

def crms(args):
    if args.cmd == 'conf':
        crms_conf(args)
    elif args.cmd == 'conf_mod' :
        crms_conf_mod(args)
    elif args.cmd == 'init' :
        crms_init(args)
    elif args.cmd == 'add' :
        crms_add(args)
    elif args.cmd == 'push' :
        crms_push(args)
    elif args.cmd == 'pull' :
        crms_pull(args)
    elif args.cmd == 'list' :
        crms_list(args)
    elif args.cmd == 'desc' :
        crms_desc(args)
    else :
        print("Unknown CMD")


def arg_parse() :
    arg_parser = argparse.ArgumentParser(prog="crms", description="Cloud Robot Model Sharing CLI")

    sub_parsers = arg_parser.add_subparsers(dest="cmd", help="sub-command help", required=True)
    
    parser_conf =   sub_parsers.add_parser('conf',  help="CRMS CONFIG : crms conf <git_remote_url> <dvc_remote_url>")
    parser_conf_mod =   sub_parsers.add_parser('conf_mod',  help="CRMS CONFIG MODIFY : crms conf_mod [-g <git_remote_url>] [-d <dvc_remote_url>]" )
    parser_init =   sub_parsers.add_parser('init',  help="CRMS INIT : crms init <model_name>" )
    parser_add  =   sub_parsers.add_parser('add',   help="CRMS ADDS MODEL_FILES: crms add <model_files>...")
    parser_push =   sub_parsers.add_parser('push',  help="CRMS PUSHES MODEL_FILES With VERSION_TAG : crms push <version>")
    parser_pull =   sub_parsers.add_parser('pull',  help="CRMS PULL MODEL With VERSION_TAG : crms pull <model_url> [--version=<latest>|<version_tag>] [--target=<target_dir>] ")
    parser_list =   sub_parsers.add_parser('list',  help="CRMS LIST Models : crms list")
    parser_desc =   sub_parsers.add_parser('desc',  help="CRMS DESCRIBE MODEL Versions : crms desc <model_name> ")

    parser_conf.add_argument("git_remote", type=str,  action="store", help="git_remote_url is required")
    parser_conf.add_argument("dvc_remote", type=str,  action="store", help="dvc_remote_url is required")

    parser_conf_mod.add_argument("-g", "--git_remote", type=str,  default="", action="store", help="--git_remote=<git_remote_url>")
    parser_conf_mod.add_argument("-d", "--dvc_remote", type=str,  default="", action="store", help="--dvc_remote=<dvc_remote_url>")

    parser_init.add_argument("model_name", type=str,  action="store", help="model_name is required")

    parser_add.add_argument("model_files", type=str,  action="store", nargs="*", help="model_files are required")

    parser_push.add_argument("version", type=str,  action="store", help="version is required")

    parser_pull.add_argument("model_url",  action="store", help="model_url is required")
    # parser_pull.add_argument("model_name",  action="store", help="model_name is required")
    parser_pull.add_argument("-v", "--version", type=str,  default="latest", action="store", help="--version=<latest>|<version_tag>")
    parser_pull.add_argument("-t", "--target", type=str,  default="", action="store", help="--target=<target_dir>")

    parser_desc.add_argument("model_name",  action="store", help="model_nameis required")

    args = arg_parser.parse_args()
    return args

def main():
    args = arg_parse()
    print(args)
    # print(dir(args))
    # print(type(args))
    crms(args)

if __name__=='__main__':
    main()

