
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