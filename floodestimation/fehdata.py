from urllib.request import urlopen, pathname2url
from appdirs import AppDirs
import os
import shutil
import time, datetime
import json
from zipfile import ZipFile
from floodestimation.catchment import Catchment, AmaxRecord

OPEN_HYDROLOGY_JSON_URL = \
    'https://github.com/OpenHydrology/StatisticalFloodEstimationTool/blob/master/floodestimation/fehdata.json'
FEH_DATA_URL = 'http://www.ceh.ac.uk/data/nrfa/peak_flow/WINFAP-FEH_v3.3.4.zip'
CACHE_FOLDER = AppDirs(__name__, appauthor='OpenHydrology').user_cache_dir
os.makedirs(CACHE_FOLDER, exist_ok=True)
CACHE_ZIP = 'FEH_data.zip'


def retrieve_download_url():
    """
    Retrieves download location for FEH data zip file from hosted json configuration file.
    :return:
    """
    try:
        # Try to obtain the url from the Open Hydrology json config file.
        with urlopen(OPEN_HYDROLOGY_JSON_URL, timeout=10) as f:
            config = json.loads(f.read().decode('utf-8'))
        if config['feh_data_url'].startswith('.'):
            config['feh_data_url'] = 'file:' + pathname2url(os.path.abspath(config['feh_data_url']))
        return config['feh_data_url']
    except:
        # If that fails (for whatever reason) use the fallback constant.
        return FEH_DATA_URL


def download_data():
    """
    Downloads complete station dataset including catchment descriptors and amax records. And saves it into a cache
    folder.
    """
    with urlopen(retrieve_download_url()) as f:
        with open(os.path.join(CACHE_FOLDER, CACHE_ZIP), "wb") as local_file:
            local_file.write(f.read())


def unzip_data():
    with ZipFile(os.path.join(CACHE_FOLDER, CACHE_ZIP), 'r') as zf:
        zf.extractall(path=CACHE_FOLDER)


def clear_cache():
    shutil.rmtree(CACHE_FOLDER)
    os.makedirs(CACHE_FOLDER)


def amax_files():
    return [os.path.join(dp, f) for dp, dn, filenames in os.walk(CACHE_FOLDER)
            for f in filenames if os.path.splitext(f)[1].lower() == '.am']


def cd3_files():
    return [os.path.join(dp, f) for dp, dn, filenames in os.walk(CACHE_FOLDER)
            for f in filenames if os.path.splitext(f)[1].lower() == '.am']

def update_database():
    """

    :return:
    """


class FehFileParser(object):
    """
    Generic parser for FEH file format.

    File consists typically of multiple sections as follows::

        [Section Name]
        field, value
        another field, value 1, value 2
        [End]

    """
    parsed_object = object

    def __init__(self):
        #: Object that will be returned at end of parsing.
        self.object = None

    def parse(self, file_name):
        """
        Parse entire file and return relevant object.

        :param file_name: File path
        :type file_name: str
        :return: Parsed object
        """
        self.object = self.parsed_object()
        with open(file_name) as f:
            in_section = None
            for line in f:
                if line.lower().startswith('[end]'):
                    in_section = None
                elif line.startswith('['):
                    in_section = line.strip().strip('[]').lower().replace(' ', '_')
                elif in_section:
                    try:
                        getattr(self, '_section_' + in_section)(line.strip())
                    except AttributeError:
                        pass  # Skip unsupported section
        return self.object


class AmaxParser(FehFileParser):
    #: Class to be returned by :meth:`parse`. In this case a list of :class:`AmaxRecord` objects.
    parsed_object = list

    def _section_station_number(self, line):
        # Store station number (not used)
        self.station_number = line

    def _section_am_values(self, line):
        # Spit line in columns
        row = [s.strip() for s in line.split(',')]
        # Date in first column
        date = datetime.date(*time.strptime(row[0], "%d %b %Y")[0:3])  # :class:`datetime.date`
        # Flow rate in second column
        flow = float(row[1])
        if flow < 0:
            flow = None
        # Stage in last column
        stage = float(row[2])
        if stage < 0:
            stage = None
        # Create :class:`AmaxRecord` and add to object
        self.object.append(AmaxRecord(date, flow, stage))


class Cd3Parser(FehFileParser):
    parsed_object = Catchment

    def _section_station_number(self, line):
        self.object.id = int(line)

    def _section_cds_details(self, line):
        row = [s.strip() for s in line.split(',')]
        if row[0].lower() == 'name':
            self.object.watercourse = row[1]
        elif row[0].lower() == 'location':
            self.object.location = row[1]
        elif row[0].lower() == 'nominal area':
            self.object.area = float(row[1])
        elif row[0].lower() == 'nominal ngr':
            # (E, N) in meters.
            self.object.coordinate = (100*int(row[1]), 100*int(row[2]))

    def _section_descriptors(self, line):
        row = [s.strip() for s in line.split(',')]
        row[0] = row[0].lower()
        if row[0] not in ['ihdtm ngr', 'centroid ngr']:
            self.object.descriptors[row[0]] = float(row[1])
        else:
            # (E, N) in meters.
            self.object.descriptors[row[0]] = (int(row[2]), int(row[3]))
            # Set country using info provided as part of coordinates.
            country_mapping = {'gb': 'gb',
                               'ireland': 'ni'}
            self.object.country = country_mapping[row[1].lower()]

    def _section_suitability(self, line):
        row = [s.strip().lower() for s in line.split(',')]
        bool_mapping = {'yes': True, 'no': False}
        # E.g. object.suitability_qmed = True
        self.object.__setattr__('suitability_' + row[0], bool_mapping[row[1]])

    def _section_comments(self, line):
        row = [s.strip() for s in line.split(',', 1)]
        # E.g. object.comments = {'station': "Velocity-area station on a straight reach ..."}
        self.object.comments[row[0].lower()] = row[1]
