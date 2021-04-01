#!/usr/bin/env python

import json
import logging
import os
import time

import requests
from flask import Flask, request, jsonify
from os import getenv
import sentry_sdk


sentry_sdk.init(getenv('SENTRY_DSN'))


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

COBOT_API_KEY = os.environ.get('COBOT_API_KEY')
COBOT_NER_SERVICE_URL = os.environ.get('COBOT_NER_SERVICE_URL')

if COBOT_API_KEY is None:
    raise RuntimeError('COBOT_API_KEY environment variable is not set')
if COBOT_NER_SERVICE_URL is None:
    raise RuntimeError('COBOT_NER_SERVICE_URL environment variable is not set')

headers = {'Content-Type': 'application/json;charset=utf-8', 'x-api-key': f'{COBOT_API_KEY}'}


@app.route("/entities", methods=['POST'])
def respond():
    st_time = time.time()
    user_utterances = request.json['sentences']

    outputs = []

    for i, uttr in enumerate(user_utterances):
        curr_entities = []  # list of string entities, like `"baseball"`
        curr_labelled_entities = []  # list of dictionaries, like `{'text': 'baseball', 'label': 'sport'}`
        try:
            result = requests.request(url=f'{COBOT_NER_SERVICE_URL}',
                                      headers=headers,
                                      data=json.dumps({'input': uttr}),
                                      method='POST',
                                      timeout=0.6)
        except Exception as e:
            sentry_sdk.capture_exception(e)
            logger.exception(e)
            result = requests.Response()
            result.status_code = 504

        if result.status_code != 200:
            msg = "result status code is not 200: {}. result text: {}; result status: {}".format(result, result.text,
                                                                                                 result.status_code)
            sentry_sdk.capture_message(msg)
            logger.warning(msg)
        else:
            result = result.json()
            # {'response': [{'text': 'baseball', 'label': 'sport'},
            #               {'text': 'sportsman', 'label': 'misc'},
            #               {'text': 'michail jordan', 'label': 'person'},
            #               {'text': 'basketballist', 'label': 'sport'}],
            #  'model_version': 'v1.1'}
            curr_entities = [lab_ent["text"] for lab_ent in result["response"]]
            curr_labelled_entities = result["response"]

        outputs.append({"entities": curr_entities, "labelled_entities": curr_labelled_entities})

    total_time = time.time() - st_time
    logger.info(f'cobot_ner exec time: {total_time:.3f}s')
    return jsonify(outputs)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=3000)
