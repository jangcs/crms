#!/usr/bin/env python3

import sys
import os
import git
from git import Repo
import subprocess
import argparse
import yaml
import dotenv 

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import crms
import threading, time

from flask import Flask, jsonify, request, render_template


#CRMS_META_REPOSITORY = ''
#CRMS_META_REPOSITORY = os.getenv('CRMS_META_REPOSITORY','cloudrobotai')

dotenv.load_dotenv()

firebase_options = {'projectId':os.getenv("CRMS_META_REPOSITORY")}
crms_firebase_app = firebase_admin.initialize_app(options=firebase_options, name="CRMS_WatchDog")

app = Flask(__name__)
host_addr = "0.0.0.0"
host_port = 5000

watchdogs = {}

CRMS_MODELS_DIR="/crms-models"

@app.route('/')
def hello():
    deployed_models = {}

    modules = os.listdir(CRMS_MODELS_DIR)
    modules.sort()

    for d in modules :
        deployed_models[d] = []

        models = os.listdir(os.path.join(CRMS_MODELS_DIR, d))
        for m in models :
            deployed_models[d].append(m)

    registered_models = crms.crms_list()
    registered_models.sort()

    # for model in deployed_models :
    #     if model in registered_models :
    #         registered_models.remove(model)

    # res = {'crms cached models': models}
    # return jsonify(res)
    return render_template("index.html", deployed_models=deployed_models, registered_models=registered_models)


@app.route('/list', methods=['GET'])
def list_method():
    res = {}
    model_list = crms.crms_list()

    for model_name in model_list :
        model_desc = crms.crms_desc(model_name)
        res[model_name] = model_desc[0]

    # print("Response " + str(res))

    return jsonify(res)

@app.route('/watchdog', methods=['GET','POST'])
def watchdog_method():
    if request.method == 'GET':
        print("Receive a GET Request for Watchdog")
        module_name = request.args.get('module_name').strip()
        model_name = request.args.get('model_name').strip()
        model_version = request.args.get('model_version').strip()

        if (module_name, model_name) in watchdogs :
            return 'Already monitoring ' + model_name + " in module(" + module_name + ")"

        if not os.path.isdir( os.path.join(CRMS_MODELS_DIR, module_name, model_name) ) :
            return 'Model(' +  model_name + ') has not been deployed yet. Deploy the model first !!!'            

        watchdog_ = WatchDog(module_name, model_name, model_version)
        watchdogs[(module_name, model_name)] = watchdog_
        watchdog_.start()

        res = {'status': 'Success','model':model_name, 'version':model_version, 'latest':watchdog_.latest_version if watchdog_.latest_version != "" else "not exist"}
        print("Response " + str(res))

        return jsonify(res)
    # if request.method == 'POST':
    #     print("Receive a POST Request for Watchdog")
    #     model_name = request.json['model_name']

    #     if model_name in watchdogs :
    #         return 'Already monitoring ' + model_name

    #     if not os.path.isdir(CRMS_MODELS_DIR+"/"+model_name) :
    #         return 'Model(' +  model_name + ') has not been deployed yet. Deploy the model first !!!'             

    #     watchdog_ = WatchDog(model_name)
    #     watchdogs[model_name] = watchdog_
    #     watchdog_.start()

    #     res = {'model':model_name, 'latest':watchdog_.latest_version if watchdog_.latest_version != "" else "not exist"}
    #     print("Response " + str(res))

    #     return jsonify(res)

@app.route('/deploy', methods=['GET','POST'])
def deploy_method():
    if request.method == 'GET':
        print("Receive a GET Request to Deploy")
        module_name = request.args.get('module_name').strip()
        model_name = request.args.get('model_name').strip()
        model_version = request.args.get('model_version').strip()

        if (module_name, model_name) in watchdogs :
            return 'Already deployed : ' + model_name + " to module(" + module_name + ")"

        watchdog_ = WatchDog(module_name, model_name, model_version)
        deploy_ok = watchdog_.deploy()
        if deploy_ok != True :
            watchdog_.db.close()
            del watchdog_
            res = {'status': 'Failed' }
            return jsonify(res)

        watchdogs[(module_name,model_name)] = watchdog_
        watchdog_.start()

        res = {'status': 'Success', 'model':model_name, 'version':model_version, 'latest':watchdog_.latest_version if watchdog_.latest_version != "" else "not exist"}
        print("Response " + str(res))

        return jsonify(res)
    # if request.method == 'POST':
    #     print("Receive a POST Request to Deploy")
    #     model_name = request.json['model_name']

    #     if model_name in watchdogs :
    #         return 'Already deployed : ' + model_name

    #     watchdog_ = WatchDog(model_name)
    #     watchdog_.deploy()
    #     watchdogs[model_name] = watchdog_
    #     watchdog_.start()

    #     res = {'model':model_name, 'latest':watchdog_.latest_version if watchdog_.latest_version != "" else "not exist"}
    #     print("Response " + str(res))

    #     return jsonify(res)


def print_verbose(verbose, msg):
    if verbose :
        print("[WatchDog] " + msg)    


class WatchDog(threading.Thread):
    def __init__(self, module_name, model_name, model_version):
        threading.Thread.__init__(self) 
        self.module_name = module_name
        self.model_name = model_name
        self.model_version = model_version

        self.latest_version = ""
        
        if not os.path.exists(CRMS_MODELS_DIR+"/"+self.module_name) :
            os.makedirs(CRMS_MODELS_DIR+"/"+self.module_name)
            print_verbose(True, 'Cache directory for the module(' +  self.module_name + ') was created.')

        firebase_options = {'projectId':os.getenv("CRMS_META_REPOSITORY")}
        
        # self.crms_firebase_app = firebase_admin.initialize_app(options=firebase_options, name="CRMS_WatchDog"+":"+module_name+"."+model_name)
        self.crms_firebase_app = crms_firebase_app

        self.db = firestore.client(app=self.crms_firebase_app)

        doc = self.db.collection('models').document(self.model_name).get()   # DocumentReference
        if doc.exists :
            d = doc.to_dict()
            d['id']=doc.id
            self.latest_version = d['latest']
            print_verbose(True, "Model : " + d["id"] + ", Latest Version: "+d['latest'] )
        else :
            print_verbose(True, "Model " + self.model_name + " not exists.")


    def run(self):
        self.is_running = True

        while self.is_running :
            doc = self.db.collection('models').document(self.model_name).get()   # DocumentReference
            if doc.exists :
                d = doc.to_dict()
                d['id']=doc.id
                print_verbose(True, "Module : " + self.module_name +", Model : " + d["id"] + ", Latest Version: "+d['latest'] )
                # When a new version is uploaded
                if self.latest_version != "" and self.latest_version != d['latest']:
                    descs = crms.crms_desc(self.model_name)
                    for doc in descs: 
                        git_repository_url = doc['git_repository']
                        print_verbose(True, 'PULL Model : model = ' +  doc['id'] + ', version = '+doc['latest'])
                        crms.crms_pull(git_repository_url, 'latest', CRMS_MODELS_DIR+"/"+self.module_name+"/"+self.model_name, verbose=True)
                        print_verbose(True, "Send Re-deploy request to ComCom Agent(" + os.getenv("COMCOM_AGENT") + ")" )
                self.latest_version = d['latest']
            else :
                print_verbose(True, "Model " + self.model_name + " not exists.")
                break

            time.sleep(int(os.getenv("WATCHDOG_PERIOD", 5)))

        del watchdogs[self.model_name]
        print_verbose(True, "Watchdog for " + self.model_name + " stopped.")

    def deploy(self):
            doc = self.db.collection('models').document(self.model_name).get()   # DocumentReference
            if doc.exists :
                d = doc.to_dict()
                d['id']=doc.id
                print_verbose(True, "Model : " + d["id"] + ", Latest Version: "+d['latest'] )
                # When a new version is uploaded
                descs = crms.crms_desc(self.model_name)
                for doc in descs: 
                    git_repository_url = doc['git_repository']
                    print_verbose(True, 'PULL Model : model = ' +  doc['id'] + ', version = '+doc['latest'])
                    # crms.crms_pull(git_repository_url, 'latest', CRMS_MODELS_DIR+"/"+self.model_name, verbose=True)
                    try : 
                        crms.crms_pull(git_repository_url, self.model_version, CRMS_MODELS_DIR+"/"+self.module_name+"/"+self.model_name, verbose=True)
                    except : 
                        return False

                self.latest_version = d['latest']
            else :
                print_verbose(True, "Model " + self.model_name + " not exists.")
                return False

            return True

    def stop(self):
        self.is_running = False


if __name__=='__main__':
    
    # watchdog = WatchDog(os.getenv("MODEL_NAME"))
    # watchdog.start()
    app.run(host=host_addr, port=host_port)

    # watchdog.stop()
    for w in watchdogs.values() :
        w.stop()
    time.sleep(int(os.getenv("WATCHDOG_PERIOD", 5)))
