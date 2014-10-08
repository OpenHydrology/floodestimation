# Copyright (c) 2014  Neil Nutt <neilnutt[at]googlemail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from floodestimation.entities import Catchment, Descriptors
from configobj import ConfigObj
import os.path
from os import environ,rename,unlink
import shutil
from time import ctime

'''
EXAMPLE USAGE:

from floodestimation.entities import Catchment, Descriptors
import project_file
import gui_data

catchment = Catchment("River Town", "River Burn")
catchment.descriptors = Descriptors(dtm_area=10, bfihost=0.50, sprhost=50, saar=1000, farl=1, urbext=0)
catchment.channel_width=2.0


filename = "C:/Temp/rtown study.zip"

gui_data_obj = gui_data.Store() # A gui_data_obj will hold all modeller notes and decisions etc
# The following would be set by the gui
gui_data_obj.catchment_description = 'A ficticious catchment far far away.'
gui_data_obj.cds_comments['saar']='Manually adjusted using gauge data.'
gui_data_obj.cds_comments['dtm_area']='Based on a wild guess.'

project_file.save_project(catchment,filename,gui_data_obj)
loaded_catchment,gui_data_obj = project_file.load_project(filename)
'''


def save_project(catchment_obj,project_filename,gui_data_obj=None):
  '''
  Saves the contents of the catchment object and gui object to a project archive
  :param catchment,filename,gui_data_obj
  :type catchment object,string,gui data object
  :return: None
  :rtype: None  
  '''
 
  fname = os.path.basename(project_filename).split('.')[0]
  tempdir = project_filename.split('.')[0]
  
  if os.path.isdir(tempdir) is False:
    os.makedirs(tempdir)
  else:
    print("Temp directory exists, exiting")
    exit()
  
  config = ConfigObj()
  config.filename = os.path.join(tempdir,fname+".ini")
  
  config['Version'] = '0.0.1'
  config['Date saved'] = ctime()
  config['User']= environ['USERNAME']
  config['Catchment_name'] = catchment_obj
  
  config['File paths']={}
  config['File paths']['ini_file'] = fname+".ini"
  cdsFile = os.path.join(tempdir,fname+".cds")
  config['File paths']['cds_file'] = fname+".cds"
  write_cds_file(catchment_obj,cdsFile,gui_data_obj)
  
  if len(catchment_obj.amax_records) !=0:
    amFile = os.path.join(tempdir,fname+".am")
    config['File paths']['am_file'] = fname+".am"
    write_am_file(catchment_obj,amFile)
  else:
    config['File paths']['am_file']=None
  
  config['File paths']['pot_file'] = None
  config['File paths']['analysis_report']=None
  config['File paths']['checksum'] = None
  
  config['Supplementary information']={}
  config['Supplementary information']['channel_width'] = catchment_obj.channel_width
  
  if gui_data_obj is not None:
    config['Supplementary information']['catchment_description']=''
    config['Supplementary information']['purpose']=''
    config['Supplementary information']['authors_notes']=''
    config['Supplementary information']['author_signature']=''
    config['Supplementary information']['checkers_notes']=''
    config['Supplementary information']['checker_signature']=''
  
  
    config['Analysis']={}
    config['Analysis']['qmed']={}
    config['Analysis']['qmed']['comment']=None
    config['Analysis']['qmed']['user_supplied_qmed'] = None
    config['Analysis']['qmed']['estimate_method']='default'
    config['Analysis']['qmed']['donor_method']='default'
    config['Analysis']['qmed']['donor']=[1001,1002]
    config['Analysis']['qmed']['adjust for urbanisation']=True
    config['Analysis']['qmed']['urban_method']='default'
    
    config['Analysis']['fgc']={}
    config['Analysis']['fgc']['comment']=''
    config['Analysis']['fgc']['adopted']='fgc1'
    config['Analysis']['fgc']['fgc1']={}
    config['Analysis']['fgc']['fgc1']['comment']=''
    config['Analysis']['fgc']['fgc1']['method']='pooling'
    config['Analysis']['fgc']['fgc1']['pooling_group']=[1001,1002]
    config['Analysis']['fgc']['fgc1']['weighting_method']='default'
    config['Analysis']['fgc']['fgc2']={}
    config['Analysis']['fgc']['fgc2']['comment']=''
    config['Analysis']['fgc']['fgc2']['method']='fssr14'
    config['Analysis']['fgc']['fgc2']['hydrological_region']=1

  config.write()
  
  if os.path.isfile(project_filename):
    os.unlink(project_filename)
  shutil.make_archive(tempdir,"zip",tempdir)
  shutil.rmtree(tempdir)
  if tempdir+'.zip' != project_filename:
    os.rename(tempdir+'.zip', project_filename)

def write_cds_file(catchment_obj,fname,gui_data_obj):
  '''
  '''
  
  config = ConfigObj()
  config.filename = fname
  
  descriptors = catchment_obj.descriptors
  
  config['Catchment']=catchment_obj
  config['CDS']={}
  config['CDS']['ihdtm_ngr']=descriptors.ihdtm_ngr
  config['CDS']['centroid_ngr']=descriptors.centroid_ngr
  config['CDS']['dtm_area']=descriptors.dtm_area
  config['CDS']['altbar']=descriptors.altbar
  config['CDS']['aspbar']=descriptors.aspbar
  config['CDS']['aspvar']=descriptors.aspvar
  config['CDS']['bfihost']=descriptors.bfihost
  config['CDS']['dplbar']=descriptors.dplbar
  config['CDS']['dpsbar']=descriptors.dpsbar
  config['CDS']['farl']=descriptors.farl
  config['CDS']['fpext']=descriptors.fpext
  config['CDS']['ldp']=descriptors.ldp
  config['CDS']['propwet']=descriptors.propwet
  
  config['CDS']['rmed_1h']=descriptors.rmed_1h
  config['CDS']['rmed_1d']=descriptors.rmed_1d
  config['CDS']['rmed_2d']=descriptors.rmed_2d
  config['CDS']['saar']=descriptors.saar
  config['CDS']['saar4170']=descriptors.saar4170

  config['CDS']['sprhost']=descriptors.sprhost
  config['CDS']['urbconc1990']=descriptors.urbconc1990
  config['CDS']['urbext1990']=descriptors.urbext1990
  config['CDS']['urbloc1990']=descriptors.urbloc1990
  config['CDS']['urbconc2000']=descriptors.urbconc2000
  config['CDS']['urbext2000']=descriptors.urbext2000
  config['CDS']['urbloc2000']=descriptors.urbloc2000
  config['CDS']['urbext']=descriptors.urbext
  
  if gui_data_obj is not None:
    config['Cds comments']={}
    for handle in gui_data_obj.cds_comments:
      config['Cds comments'][handle]=gui_data_obj.cds_comments[handle]
  
  config.write()
  
  
  
def write_am_file(catchment_obj,fname):
  f = open.fname()
  
  for entry in catchment_obj.amax_records:
    print(entry)
    f.write(entry)
  


def load_project(filename):
  '''
  Loads the contents of a project archive to a catchment object and gui object
  :param filename
  :type string
  :return: catchment,gui_data_object
  :rtype: catchment object, gui data object  
  '''
  from floodestimation import parsers
  
  temp_dir = os.path.join(os.path.dirname(filename),os.path.basename(filename.split('.')[0]))
  header_fname = os.path.join(temp_dir,os.path.basename(filename.split('.')[0]))
  shutil.unpack_archive(filename, temp_dir, "zip")

  inifname = header_fname+".ini"

  inif = ConfigObj(inifname)
  cdsfname = os.path.join(temp_dir,inif['File paths']['cds_file'])
  
  catchment = Catchment()
  catchment,gui_data_obj = parsers.cdsParser(catchment,cdsfname)
  
  '''
  if gui_data_obj is not None:
    gui_data_obj.catchment_description =inif['Supplementary information']['catchment_description']
    gui_data_obj.purpose =inif['Supplementary information']['purpose']
    gui_data_obj.authors_notes =inif['Supplementary information']['authors_notes']
    gui_data_obj.author_signature =inif['Supplementary information']['author_signature']
    gui_data_obj.checkers_notes =inif['Supplementary information']['checkers_notes']
    gui_data_obj.checker_signature =inif['Supplementary information']['checker_signature']
  '''
        
  catchment.channel_width = inif['Supplementary information']['channel_width']
    
  shutil.rmtree(temp_dir)
  
  return catchment,gui_data_obj

