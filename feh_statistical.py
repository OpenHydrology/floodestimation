
def channel_width_qmed(width):
      
        qmed = 0.182 * (width ** 1.98)
        return qmed

def area_based_qmed(carea):
        import math
        ae = 1.0 - 0.015 * math.log(carea/0.5)
        
        qmed = 1.172 * (carea ** ae)
        return qmed
        
def qmed_cds1999(carea,saar,farl,sprhost,bfihost):
        import math
        reshost = bfihost +1.3*(sprhost/100.0)-0.987
        ae = 1.0 - 0.015 * math.log(carea/0.5)
        
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