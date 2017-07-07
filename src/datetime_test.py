from datetime_patcher import datetime_patcher 
import datetime

if __name__ == '__main__':
    with datetime_patcher() as t: #.initialize()
        
        print datetime.datetime.today()
        t.set_time(3600)
        print datetime.datetime.today()
        print datetime.datetime.fromtimestamp(7200)
    
        
    