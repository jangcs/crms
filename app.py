#!/usr/bin/env python3

import sys
import os
import git
from git import Repo
import subprocess
import argparse
import yaml

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import crms
import threading, time

from flask import Flask


#CRMS_META_REPOSITORY = ''
CRMS_META_REPOSITORY = os.getenv('CRMS_META_REPOSITORY','cloudrobotai')
crms_firebase_app = None

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello Flask World'

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

        firebase_options = {'projectId':CRMS_META_REPOSITORY}
        self.crms_firebase_app = firebase_admin.initialize_app(options=firebase_options, name="CRMS_WatchDog")
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
                        crms.crms_pull(git_repository_url, 'latest', verbose=True)
                self.last_version = d['latest']
            else :
                print_verbose(True, "")

            time.sleep(5)

    def stop(self):
        self.is_running = False


if __name__=='__main__':
    
    watchdog = WatchDog('model_v5')
    watchdog.start()
    app.run()
    watchdog.stop()
