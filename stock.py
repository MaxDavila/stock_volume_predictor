"""A simple client to predict AAPL's trading volume."""

import csv
import datetime
import logging

from nupic.data.datasethelpers import findDataset
from nupic.frameworks.opf.metrics import MetricSpec
from nupic.frameworks.opf.modelfactory import ModelFactory
from nupic.frameworks.opf.predictionmetricsmanager import MetricsManager

import model_params

_LOGGER = logging.getLogger(__name__)

_DATA_PATH = "daily_data.csv"

_METRIC_SPECS = (
    MetricSpec(field='Volume', metric='multiStep',
               inferenceElement='multiStepBestPredictions',
               params={'errorMetric': 'aae', 'window': 7000, 'steps': 1}),
)

_NUM_RECORDS = 7000



def createModel():
  return ModelFactory.create(model_params.MODEL_PARAMS)



def runHotgym():
  model = createModel()
  model.enableInference({'predictedField': 'Volume'})
  metricsManager = MetricsManager(_METRIC_SPECS, model.getFieldInfo(),
                                  model.getInferenceType())
  with open (findDataset(_DATA_PATH)) as fin:
    reader = csv.reader(fin)
    headers = reader.next()
    for i, record in enumerate(reader, start=1):
      modelInput = dict(zip(headers, record))
      modelInput["Volume"] = float(modelInput["Volume"])
      # modelInput["timestamp"] = datetime.datetime.strptime(
      #     modelInput["timestamp"], "%m/%d/%y %H:%M")
      result = model.run(modelInput)
      result.metrics = metricsManager.update(result)
      isLast = i == _NUM_RECORDS
      if i % 100 == 0 or isLast:
        print result.metrics
      if isLast:
        break



if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  runHotgym()
