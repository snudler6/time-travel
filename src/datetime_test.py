from datetime_patcher import datetime_patcher 
import datetime

if __name__ == '__main__':
    t = datetime_patcher() #.initialize()
    t.start()
    
    print datetime.datetime.today()
    t.set_time(3600)
    print datetime.datetime.today()
    print datetime.datetime.fromtimestamp(7200)
    
        
    