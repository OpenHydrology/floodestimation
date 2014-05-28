import os, time
import numpy as np

def createDatabase(searchPath,outfile):
  f = open(outfile,'w')
  f.write("VERSION, STATION, NAME, GRID, IHDTM X, IHDTM Y , CENTROID X, CENTROID Y, DTM AREA, ALTBAR, ASPBAR, BFIHOST, DPLBAR, DPSBAR, FARL, FPEXT, LDP, PROPWET, RMED1H, RMED1D, RMED2D, SAAR, SAAR4170, SPRHOST, URBCONC1990, URBEXT1990, URBLOC1990, URBCONC2000, URBEXT2000, URBLOC2000,SUIT QMED, SUIT POOL, QMed\n")

  searchForDirectories(searchPath,f)
  
  f.close()

def searchForDirectories(searchPath,f):
  list = os.listdir(searchPath)
  for item in list:
    currentPath = os.path.join(searchPath,item)
    if os.path.isdir(currentPath):
      print item
      searchForDirectories(currentPath,f)
    elif os.path.isfile(currentPath):
      if item.lower().endswith('cd3'):
        readFile(currentPath,f)
 
def qmedFromAmFile(file):
  amaxSeries = list()
  f = open(file,'r')
  
  lines = f.readlines()
  ams = False
  
  for line in lines:
    if ams == False:
      if line.startswith('[AM Values]'):
        ams=True
    elif ams==True:
      if line.startswith('[END}'):
        pass
      else:
        try:
          flow = float(line.split(',')[1])
          amaxSeries.append(flow)
        except:
          pass
      
  qmed = np.median(amaxSeries)
  
  return qmed
  
def readFile(filePath,f):
            FILE = open(filePath,"r") 
  ## The following lines extract the values from the .cd3 file
            marker = 1         
            linecount = 1
            for line in FILE.read().split('\n'):
               if line[:7] == "VERSION":
                    VERSION=line[8:]
                    
               if marker == 1:
                    STATION = line
                    marker = 0
               if line == "[STATION NUMBER]":
                    marker = 1
                    

               if line[:4] == "NAME":
                    NAME=line[5:]

               if line[:8] == "LOCATION":
                    LOCATION=line[9:]

               if line[:9] == "IHDTM NGR":  ## this captures the x and y co-ordinates in one go (already x,y)
                    GRID=line[10:12]
                    IHDTM_NGR=line[-13:]
                    if IHDTM_NGR[0]== ",":  ## this if removes shorter grid references
                          IHDTM_NGR = list()
                          IHDTM_NGR = line[-12:]

               if line[:12] == "CENTROID NGR":  ## this captures the x and y co-ordinates in one go (already x,y)
                     CENTROID_NGR=line[-13:]
                     if CENTROID_NGR[0] == ",": ## this if removes shorter grid references
                          CENTROID_NGR = list()
                          CENTROID_NGR = line[-12:]

               if line[:8] == "DTM AREA":
                     AREA=line[9:]
                     
               if line[:6] == "ALTBAR":
                     ALTBAR=line[7:]

               if line[:6] == "ASPBAR":
                     ASPBAR=line[7:]
                     
               if line[:6] == "ASPVAR":
                     ASPVAR=line[7:]
                     
               if line[:7] == "BFIHOST":
                     BFIHOST=line[8:]
                     
               if line[:6] == "DPLBAR":
                     DPLBAR=line[7:]
                     
               if line[:6] == "DPSBAR":
                     DPSBAR=line[7:]
                     
               if line[:4] == "FARL":
                     FARL=line[5:]
                     
               if line[:5] == "FPEXT":
                     FPEXT=line[6:]

               if line[:3] == "LDP":
                    LDP=line[4:]                   

               if line[:7] == "PROPWET":
                    PROPWET=line[8:]

               if line[:7] == "RMED-1H":
                    RMED1H=line[8:]
                    
               if line[:7] == "RMED-1D":
                    RMED1D=line[8:]

               if line[:7] == "RMED-2D":
                    RMED2D=line[8:]

               if line[:5] == "SAAR,":
                    SAAR=line[5:]

               if line[:8] == "SAAR4170":
                    SAAR4170=line[9:]

               if line[:7] == "SPRHOST":
                    SPRHOST=line[8:]

               if line[:11] == "URBCONC1990":
                    URBCONC1990=line[12:]

               if line[:10] == "URBEXT1990":
                    URBEXT1990=line[11:]

               if line[:10] == "URBLOC1990":
                    URBLOC1990=line[11:]

               if line[:11] == "URBCONC2000":
                    URBCONC2000=line[12:]

               if line[:10] == "URBEXT2000":
                    URBEXT2000=line[11:]

               if line[:10] == "URBLOC2000":
                    URBLOC2000=line[11:]

               if line[:4] == "QMED":
                    SUIT_QMED=line[5:]

               if line[:7] == "POOLING":
                    SUIT_POOL=line[8:]                 

            #filecount = filecount + 1
            FILE.close()
            
            amFile = filePath[:-3]+'AM'
            
            qmed = qmedFromAmFile(amFile)
           
            #if filename[-3:]  == suffix:
            try:
              f.write(str(VERSION)+","+str(STATION)+","+str(NAME)+","+str(GRID)+","+str(IHDTM_NGR)+","+str(CENTROID_NGR)+","+str(AREA)+","+str(ALTBAR)+","+str(ASPBAR)+","+str(BFIHOST)+","+str(DPLBAR)+","+str(DPSBAR)+","+str(FARL)+","+str(FPEXT)+","+str(LDP)+","+str(PROPWET)+","+str(RMED1H)+","+str(RMED1D)+","+str(RMED2D)+","+str(SAAR)+","+str(SAAR4170)+","+str(SPRHOST)+","+str(URBCONC1990)+","+str(URBEXT1990)+","+str(URBLOC1990)+","+str(URBCONC2000)+","+str(URBEXT2000)+","+str(URBLOC2000)+","+str(SUIT_QMED)+","+str(SUIT_POOL)+","+str(qmed)+'\n')
            except:
              pass


if __name__ == '__main__':
  searchPath = 'C:\\Technical\\Hydrology\\WINFAP\\HiFlows_v3.02'  ## Path that the script will look at
  outfile = 'qmed_db_test.csv'
  createDatabase(searchPath,outfile)

