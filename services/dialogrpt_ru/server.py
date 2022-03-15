import logging
import time
import os

import sentry_sdk
import torch
from flask import Flask, request, jsonify
from sentry_sdk.integrations.flask import FlaskIntegration

from main import Option
from model import Scorer


sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), integrations=[FlaskIntegration()])

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

PRETRAINED_MODEL_FNAME = os.environ.get(
    "PRETRAINED_MODEL_FNAME", "dialogrpt_ru_ckpt_v0.pth"
)
logger.info(f"PRETRAINED_MODEL_FNAME = {PRETRAINED_MODEL_FNAME}")

cuda = torch.cuda.is_available()
if cuda:
    torch.cuda.set_device(0)
    device = "cuda"
else:
    device = "cpu"

logger.info(f"dialogrpt is set to run on {device}")

params = {
    "path_load": f"/data/{PRETRAINED_MODEL_FNAME}",
    "data": "./bla",
    "batch": 256,
    "vali_size": 1024,
    "vali_print": 10,
    "lr": 3e-5,
    "cpu": False,
    "max_seq_len": 50,
    "mismatch": False,
    "min_score_gap": 10,
    "min_rank_gap": 10,
    "max_hr_gap": 1,
}

try:
    opt = Option(params)
    model = Scorer(opt)
    model.load(f"/data/{PRETRAINED_MODEL_FNAME}")
    model.predict(cxt="привет!", hyps=["привет. как дела?"])

    logger.info("dialogrpt model is ready")
except Exception as e:
    sentry_sdk.capture_exception(e)
    logger.exception(e)
    raise e

app = Flask(__name__)
logging.getLogger("werkzeug").setLevel("WARNING")


@app.route("/respond", methods=["POST"])
def respond():
    st_time = time.time()

    dialog_contexts = request.json.get("dialog_contexts", [])
    hypotheses = request.json.get("hypothesis", [[]])

    try:
        result_values = []
        for cxt, hyps in zip(dialog_contexts, hypotheses):
            prediction = model.predict(cxt=cxt, hyps=hyps)
            # prediction is a list of float values
            result_values.append(prediction)
    except Exception as exc:
        logger.exception(exc)
        sentry_sdk.capture_exception(exc)
        result_values = [[0. for _ in hyps] for hyps in hypotheses]

    total_time = time.time() - st_time
    logger.info(f"dialogrpt exec time: {total_time:.3f}s")

    return jsonify({"scores": result_values})
