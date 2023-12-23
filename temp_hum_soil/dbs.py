import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["user_schedule"]
mycol = mydb["schedules"]

# userInfo = {
#     'email':'',
#     'startTime': '',
#     'endTime': '',
#     'date': ''
# }
def insertSchedule(userInfo):
  mycol.insert_one(userInfo)
  return True

def getSchedulesHTML(email):
    schedule_html = []
    for x in mycol.find({'email':email}): 
        schedule_html.append(f"""<p>Từ <strong>{x['startTime']}</strong> tới <strong>{x['endTime']}</strong></p>""")
    return ''.join(schedule_html)

def getItemByDate(date):
   return mycol.find({'date': date},{'email':1})

def isExistEmail(email):
   data = mycol.find_one({'email': email})
   if data:
      return True
   return False
  
def deleteManyByDate(date):
   print(str(date)+':: deleted')
   mycol.delete_many({'date': date})


def deleteUserInfo(userInfo):
   print('user info deleted')
   mycol.delete_one(userInfo)

