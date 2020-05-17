from app.entertainmentcity import ptEntertainmentCity,kaiyuanEntertainmentCity,agEntertainmentCity,kkEntertainmentCity

# from flask_apscheduler import APScheduler
# scheduler = APScheduler()

class EntertainmentCityFactory:

    @staticmethod
    def getEntertainmentCity(code):
        if code =='PT':
            return ptEntertainmentCity.PTEntertainmentCity(code)
        elif code =='KAIYUAN':
            return kaiyuanEntertainmentCity.KAIYUANEntertainmentCity(code)
        elif code =='AG':
            return agEntertainmentCity.AGEntertainmentCity(code)
        elif code == 'MAIN':
            return kkEntertainmentCity.KKEntertainmentCity(code)