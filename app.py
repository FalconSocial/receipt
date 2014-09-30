#!/usr/bin/env python2

import json
import logging
import logging.handlers
import os
import subprocess
from datetime import datetime

from flask import Flask, request

try:
    # Python 3
    from configparser import RawConfigParser
except ImportError:
    # Python 2
    from ConfigParser import RawConfigParser


config = RawConfigParser()
config.readfp(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini')))
scripts_path = config.get('Receipt', 'scripts directory')

log = logging.getLogger('receipt')
log.setLevel(logging.DEBUG)
log_handler = logging.handlers.RotatingFileHandler(
    config.get('Receipt', 'log file'),
    maxBytes=int(config.get('Receipt', 'log size')),
    backupCount=int(config.get('Receipt', 'log backup count'))
)
log_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S'))
log.addHandler(log_handler)


class Receipt:
    def __init__(self, log, payload):
        self.log = log
        self.payload = payload

        self.repository = os.path.basename(self.payload['repository']['url'])
        if self.repository.endswith('.git'):
            self.repository = self.repository[:-4]

        self.repository_directory = os.path.join(scripts_path, self.repository)
        self.branch = os.path.basename(self.payload['ref'])
        self.branch_directory = os.path.join(scripts_path, self.repository, self.branch)

        self.log.info('Received payload for repository "{}", branch "{}"'.format(self.repository, self.branch))

    def runScript(self, path):
        # TODO: Run scripts in parallel
        self.log.debug('Running script: {}'.format(path))
        try:
            start_time = datetime.now()
            process = subprocess.Popen([path, self.repository, self.branch], stdin=subprocess.PIPE)
            process.communicate(input=json.puts(self.payload) + '\n')
            duration = datetime.now() - start_time

            if process.returncode == 0:
                self.log.info('{} executed in {}, exit value: {}'.format(path, duration, process.returncode))
            else:
                self.log.warning('{} executed in {}, exit value: {}'.format(path, duration, process.returncode))
        except OSError as error:
            self.log.warning('{} could not be executed, got the following error: {}'.format(path, error))

    def runScriptsInDirectory(self, directory_path):
        self.log.debug('Running scripts in directory: {}'.format(directory_path))
        for item in os.listdir(directory_path):
            item = os.path.join(directory_path, item)
            if os.path.isfile(item):
                self.runScript(item)

    def execute(self):
        if not os.path.exists(self.repository_directory):
            self.log.warning('Scripts directory does not exist for repository "{}" ({})'.format(self.repository, self.repository_directory))
            return False

        self.runScriptsInDirectory(self.repository_directory)

        if os.path.exists(self.branch_directory):
            self.runScriptsInDirectory(self.branch_directory)


app = Flask(__name__)


@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def index(path):
    payload = request.get_json()

    if payload:
        receipt = Receipt(log, payload)
    else:
        receipt = Receipt(log, json.loads(request.form['payload']))

    receipt.execute()
    return 'Thank you very much!\n'


if __name__ == '__main__':
    app.run(host=config.get('Receipt', 'listen host'), port=int(config.get('Receipt', 'listen port')))
