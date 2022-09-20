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

@app.route('/')
def hello():
    return 'Hello Flask World'

@app.route('/watchdog', methods=['GET','POST'])
def watchdog_method():
    if request.method == 'GET':
        print("Receive a GET Request")
        model_name = request.args.get('model_name')
        res = {'model':model_name}
        print("Response " + str(res))

        if model_name in watchdogs :
            return 'Already monitoring ' + model_name

        watchdog_ = WatchDog(model_name)
        watchdogs[model_name] = watchdog_
        watchdog_.start()

        return jsonify(res)
    if request.method == 'POST':
        print("Receive a POST Request")
        model_name = request.json['model_name']
        res = {'model':model_name}
        return jsonify(res)
    

def append_label_sample(f) :
    f.write('#labels : \n')
    f.write('#  label_key1: lavel_value1\n')
    f.write('#  label_key2: lavel_value2\n')
    f.write('#  resolution: 640x480(sample)\n')

def print_verbose(verbose, msg):
    if verbose :
        print("[WatchDog] " + msg)    


class WatchDog(threading.Thread):
    def __init__(self, model_name):
        threading.Thread.__init__(self) 
        self.model_name = model_name

        firebase_options = {'projectId':os.getenv("CRMS_META_REPOSITORY")}
        self.crms_firebase_app = firebase_admin.initialize_app(options=firebase_options, name="CRMS_WatchDog"+":"+model_name)
        self.db = firestore.client(app=self.crms_firebase_app)

    def run(self):
        self.is_running = True
        self.last_version = ""

        while self.is_running :
            doc = self.db.collection('models').document(self.model_name).get()   # DocumentReference
            if doc.exists :
                d = doc.to_dict()
                d['id']=doc.id
                print_verbose(True, "Model : " + d["id"] + ", Latest Version: "+d['latest'] )
                # When a new version is uploaded
                if self.last_version != "" and self.last_version != d['latest']:
                    descs = crms.crms_desc(self.model_name)
                    for doc in descs: 
                        git_repository_url = doc['git_repository']
                        print_verbose(True, '[CRMS] PULL Model : model = ' +  doc['id'] + ', version = '+doc['latest'])
                        crms.crms_pull(git_repository_url, 'latest', "/models/"+self.model_name, verbose=True)
                        print_verbose(True, "Send Re-deploy request to ComCom Agent(" + os.getenv("COMCOM_AGENT") + ")" )
                self.last_version = d['latest']
            else :
                print_verbose(True, "Model " + self.model_name + " not exists.")
                break

            time.sleep(int(os.getenv("WATCHDOG_PERIOD", 5)))

        del watchdogs[self.model_name]
        print_verbose(True, "Watchdog for " + self.model_name + " stopped.")

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
