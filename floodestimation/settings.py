import os
from appdirs import AppDirs

APP_NAME = 'fehdata'
APP_AUTHOR = 'OpenHydrology'

OPEN_HYDROLOGY_JSON_URL = \
    'https://github.com/OpenHydrology/StatisticalFloodEstimationTool/blob/master/floodestimation/fehdata.json'
FEH_DATA_URL = 'http://www.ceh.ac.uk/data/nrfa/peak_flow/WINFAP-FEH_v3.3.4.zip'

DATA_FOLDER = AppDirs(APP_NAME, APP_AUTHOR).user_data_dir
DB_FILE_PATH = os.path.join(DATA_FOLDER, 'fehdata.sqlite')
os.makedirs(DATA_FOLDER, exist_ok=True)

CACHE_FOLDER = AppDirs(APP_NAME, APP_AUTHOR).user_cache_dir
os.makedirs(CACHE_FOLDER, exist_ok=True)