'''
@author: Neil Nutt, neilnutt[at]googlemail[dot]com

Functions called by various stages of the program to undertake standard FEH calculations

    Statistical Flood Estimation Tool
    Copyright (C) 2014  Neil Nutt, neilnutt[at]googlemail[dot]com
    https://github.com/OpenHydrology/StatisticalFloodEstimationTool

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

'''
def channel_width_qmed(width):
      
        qmed = 0.182 * (width ** 1.98)
        return qmed

def area_based_qmed(carea):
        from math import log
        ae = 1.0 - 0.015 * log(carea/0.5)
        
        qmed = 1.172 * (carea ** ae)
        return qmed
        
def qmed_cds1999(carea,saar,farl,sprhost,bfihost):
        from math import log
        reshost = bfihost +1.3*(sprhost/100.0)-0.987
        ae = 1.0 - 0.015 * log(carea/0.5)
        
        qmed = 1.172 * (carea ** ae)*((saar/1000.0)**1.560)*(farl**2.642)*((sprhost/100.0)**1.211)*0.0198**reshost
        return qmed
        
def qmed_cds2008(carea,saar,farl,bfihost):
        qmed = 8.3062*(carea**0.8510)*(0.1536**(1000/saar))*(farl**3.4451)*(0.0460**(bfihost**2.0))
        return qmed
        
def calc_asg(d):
      from math import exp
      asg = 0.4598*(exp(-0.02*d))+(1.0-0.4598)*exp(-0.4785*d)
      return asg
      
def distance_decaying_weighting_factor(qmed_error,asg):
    f = qmed_error**asg
    return f

def calc_uef(year):
  from math import atan
  uef =0.7851+0.2124*(atan((year-1967.5)/20.32))
  
  if uef < 1.0:
    uef = 1.0
  
  return uef

def calc_pruaf (urbext,bfihost):
  pruaf = 1 + 0.47 * urbext*(bfihost/(1-bfihost))
  return pruaf

def calc_uaf(urbext,pruaf):
  uaf = ((1+urbext)**0.37)*((pruaf)**2.16)
  return uaf


def calc_feh_hyd_dist(self,station_cds):
            from math import log
            try:          
              a =  3.2*((log(station_cds['dtmarea'])-log(self.subject_carea))/1.28)**2
            except ValueError:
              a = 1.0
            try:
              b = 0.5 *((log(station_cds['saar'])-log(self.subject_saar))/0.37)**2
            except ValueError:
              b = 1.0
            try:
              c = 0.1 *((log(station_cds['farl'])-log(self.subject_farl))/0.05)**2
            except ValueError:
              c = 1.0
            try:
              d = 0.2 *((log(station_cds['fpext'])-log(self.subject_fpext))/0.04)**2  
            except ValueError:
              d = 1.0  
            hy_dist = (a+b+c+d)**0.5
            
            return hy_dist

def fitGLbyLMED(AMAXseries):
    from numpy import min,median,mean
    import math    
    AMAXseries.sort()
    QMin=min(AMAXseries)
    QMed=median(AMAXseries)
    QBar=mean(AMAXseries)
    recordLength=len(AMAXseries)     


    # Fit GL distribution
    b0 = QBar
    b1_list=[0]
    b2_list=[0,0]
    b3_list=[0,0,0]                    
        
    for x in range(1,len(AMAXseries)+1):
         b1_list.append(AMAXseries[x-1] * (x - 1) / (len(AMAXseries) - 1))
    b1 = sum(b1_list) / len(AMAXseries)

    for x in range(2,len(AMAXseries)+1):
         b2_list.append(b1_list[x] * (x - 2) / (len(AMAXseries) - 2))                         
    b2 = sum(b2_list) / len(AMAXseries)
    
    for x in range(3,len(AMAXseries)+1):
         b3_list.append(b2_list[x] * (x - 3) / (len(AMAXseries) - 3))
    b3 = sum(b3_list) / len(AMAXseries)

    l1 = b0
    l2 = 2 * b1 - b0
    l3 = 6 * b2 - 6 * b1 + b0
    l4 = 20 * b3 -30 * b2 + 12 * b1 - b0

    t2 = l2 / l1  ## L-CV or beta
    t3 = l3 / l2  ## L-skewness or -kappa
    t4 = l4 / l2  ## L-Kurtosis

    kappa = -t3
    beta_GL_LMOM = t2
    beta_GL_LMED = t2 * kappa * math.sin( math.pi * kappa ) / ( kappa * math.pi * (kappa + t2 ) - (t2 * math.sin ( math.pi * kappa )))
    location = beta_GL_LMOM / beta_GL_LMED
    
    return QMed,kappa,beta_GL_LMED,location

def calc_weights(hyd_dist,n_records):
    lcvb = 0.0047*((hyd_dist)**0.5)+0.0023/2.0
    lskewb = 0.00219*(1.0-2.718**(-hyd_dist/0.2360))
    
    lcvc = 0.02609/(n_records-1.0)
    lskewc = 0.2743/(n_records-2.0)
    
    lcv_cjbj= (lcvb+lcvc)**-1.0
    lskew_cjbj=(lskewb+lskewc)**-1.0
    
    return lcv_cjbj,lskew_cjbj
  
def calculateGrowthFactor_GL_LMED(beta,kappa,rp):
    if rp<1.0:
      #assume an aep has been provided
      rp = 1.0/rp
    # Calculate flows for return period list and print       
    gf = QMed*(1. +(beta/kappa)*(1.0 - (rp - 1.0)**-kappa))
    return gf