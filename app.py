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

from flask import Flask, jsonify, request



#CRMS_META_REPOSITORY = ''
#CRMS_META_REPOSITORY = os.getenv('CRMS_META_REPOSITORY','cloudrobotai')

dotenv.load_dotenv()

crms_firebase_app = None

app = Flask(__name__)
host_addr = "0.0.0.0"
host_port = 5000

watchdogs = {}

CRMS_MODELS_DIR="/models"

@app.route('/')
def hello():
    models = os.listdir(CRMS_MODELS_DIR)
    models.sort()
    res = {'crms cached models': models}
    return jsonify(res)

@app.route('/watchdog', methods=['GET','POST'])
def watchdog_method():
    if request.method == 'GET':
        print("Receive a GET Request for Watchdog")
        model_name = request.args.get('model_name')

        if model_name in watchdogs :
            return 'Already monitoring ' + model_name

        if not os.path.isdir(CRMS_MODELS_DIR+"/"+model_name) :
            return 'Model(' +  model_name + ') has not been deployed yet. Deploy the model first !!!'            

        watchdog_ = WatchDog(model_name)
        watchdogs[model_name] = watchdog_
        watchdog_.start()

        res = {'model':model_name, 'latest':watchdog_.latest_version if watchdog_.latest_version != "" else "not exist"}
        print("Response " + str(res))

        return jsonify(res)
    if request.method == 'POST':
        print("Receive a POST Request for Watchdog")
        model_name = request.json['model_name']

        if model_name in watchdogs :
            return 'Already monitoring ' + model_name

        if not os.path.isdir(CRMS_MODELS_DIR+"/"+model_name) :
            return 'Model(' +  model_name + ') has not been deployed yet. Deploy the model first !!!'             

        watchdog_ = WatchDog(model_name)
        watchdogs[model_name] = watchdog_
        watchdog_.start()

        res = {'model':model_name, 'latest':watchdog_.latest_version if watchdog_.latest_version != "" else "not exist"}
        print("Response " + str(res))

        return jsonify(res)

@app.route('/deploy', methods=['GET','POST'])
def deploy_method():
    if request.method == 'GET':
        print("Receive a GET Request to Deploy")
        model_name = request.args.get('model_name')

        if model_name in watchdogs :
            return 'Already deployed : ' + model_name

        watchdog_ = WatchDog(model_name)
        watchdog_.deploy()
        watchdogs[model_name] = watchdog_
        watchdog_.start()

        res = {'model':model_name, 'latest':watchdog_.latest_version if watchdog_.latest_version != "" else "not exist"}
        print("Response " + str(res))

        return jsonify(res)
    if request.method == 'POST':
        print("Receive a POST Request to Deploy")
        model_name = request.json['model_name']

        if model_name in watchdogs :
            return 'Already deployed : ' + model_name

        watchdog_ = WatchDog(model_name)
        watchdog_.deploy()
        watchdogs[model_name] = watchdog_
        watchdog_.start()

        res = {'model':model_name, 'latest':watchdog_.latest_version if watchdog_.latest_version != "" else "not exist"}
        print("Response " + str(res))

        return jsonify(res)


def print_verbose(verbose, msg):
    if verbose :
        print("[WatchDog] " + msg)    


class WatchDog(threading.Thread):
    def __init__(self, model_name):
        threading.Thread.__init__(self) 
        self.model_name = model_name
        self.latest_version = ""
        
        firebase_options = {'projectId':os.getenv("CRMS_META_REPOSITORY")}
        self.crms_firebase_app = firebase_admin.initialize_app(options=firebase_options, name="CRMS_WatchDog"+":"+model_name)
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
                print_verbose(True, "Model : " + d["id"] + ", Latest Version: "+d['latest'] )
                # When a new version is uploaded
                if self.latest_version != "" and self.latest_version != d['latest']:
                    descs = crms.crms_desc(self.model_name)
                    for doc in descs: 
                        git_repository_url = doc['git_repository']
                        print_verbose(True, 'PULL Model : model = ' +  doc['id'] + ', version = '+doc['latest'])
                        crms.crms_pull(git_repository_url, 'latest', CRMS_MODELS_DIR+"/"+self.model_name, verbose=True)
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
                    crms.crms_pull(git_repository_url, 'latest', CRMS_MODELS_DIR+"/"+self.model_name, verbose=True)

                self.latest_version = d['latest']
            else :
                print_verbose(True, "Model " + self.model_name + " not exists.")

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
