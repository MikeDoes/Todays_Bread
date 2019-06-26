
# coding: utf-8

# # Today's Bread
# ## A Minimalist Daily Planner by Michael M
# ### Other names include: Boop bidu pidu

from datetime import date, datetime, timedelta
import json
from werkzeug import secure_filename

class User:
    def __init__ (self):
        self.agenda={}
        self.initAgenda()

    def initAgenda(self):
        for i in range(0,300):
            self.agenda[str(datetime.now().date()+timedelta(days=i))]=DailyPlan(datetime.now().date()+timedelta(days=i))
            self.agenda[str(datetime.now().date()+timedelta(days=i))].addProject('Maintenance')


class DailyPlan:
    #We do not pass any basic variables to keep stuff nice and simple
    def __init__(self,date):
        self.date={'today':date,'yesterday':date-timedelta(days=1),'tomorrow':date+timedelta(days=1)}
        self.projects={}
        self.reachOut={}
        self.waitingOn={}
        self.totalTime=0
        self.quote=''
    
    def addProject(self,title):
        self.projects[len(self.projects)]=Project(title)
        #Indexing will start at 0, but UX will always add the + 1

    def calculateTime(self):
        self.totalTime=0
        for project in self.projects:
            self.totalTime=self.totalTime+self.projects[project].time
        return self.totalTime

    def __str__(self):
        print(self.quote+ '\n')
        for project in self.projects:
            print(self.projects[project])
        print(f'Reach out to:\n{self.reachOut}')
        print(f'Waiting on:\n{self.waitingOn}')
        
        print(f'\nToday\'s date: {self.date}')
        print(f'Total Time: {self.totalTime}')
        return ''
    
    def downloadAgenda(self):
        with open('jsonfiles/'+str(self.date['today'])+'.json', 'w', newline='') as jsonfile:
            data={
                'projects':{},
                'reachOut':self.reachOut,
                'waitingOn':self.waitingOn
            }
            for project in self.projects:
                data['projects'][str(self.projects[project].title)]={}
                print(str(self.projects[project].title))
                for task in self.projects[project].tasks:
                    data['projects'][str(self.projects[project].title)][str(self.projects[project].tasks[task].description)]=str(self.projects[project].tasks[task].time)

            json.dump(data, jsonfile)
            return jsonfile

    def uploadAgenda(self,f):
        with open(f) as jsonfile:
            self.projects={}
            data = json.load(jsonfile)
            self.reachOut=data['reachOut']
            self.waitingOn=data['waitingOn']
            i=0
            for project in data['projects']:
                self.addProject(str(project))
                for task in data['projects'][str(project)]:
                    self.projects[i].addTask(str(task),int(data['projects'][project][task]))
                i=i+1
                print(str(project))
        
        return ''
    
    def removeProject(self, number):
        del self.projects[number]
        newDic={}
        j=0
        for project in self.projects:
            newDic[j]=self.projects[project]
            j=j+1
        self.projects=newDic

class Project:
    #Project is an object but tasks are dictionary entries
    def __init__(self,title):
        self.title=title
        self.tasks={}
        self.time=0
        self.id=hash(title+'00')
    
    def strTime(self):
        #Jinja templates could not use the 'round()' function so we have to append the string to the object. We should try cleaning this by not having it duplicated in the object below
        if (self.time%60<10):
            taskMinutes='0'+str(round(self.time%60,0))
        else:
            taskMinutes=str(round(self.time%60,0))
        #self.strTime=str(int(round((self.time-self.time%60)/60,0)))+':'+taskMinutes
    
    def addTask(self,description='', time=0):
        self.tasks[len(self.tasks)]=Tasks(description,time)
        self.time=0
        for task in self.tasks:
            self.time=self.time+self.tasks[task].time
        self.strTime()
        
    def removeTask(self, number):
        del self.tasks[number]
        newDic={}
        j=0
        for task in self.tasks:
            newDic[j]=self.tasks[task]
            j=j+1
        self.tasks=newDic
    
    def __str__(self):
        sentenceRender=''
        sentenceRender=sentenceRender+str(self.title)+' '+str(int(round((self.time-self.time%60)/60,0)))+':'+str(round(self.time%60,0))+'\n'
        for task in self.tasks:
            if self.tasks[task].done==1:
                box='☑ '
            else:
                box='☐ '
                
            sentenceRender=sentenceRender+box+str(task+1)+'. '+str(self.tasks[task].description)+' '+str(self.tasks[task].time) + '\n'
        return sentenceRender

class Tasks:
    def __init__(self, description, time):
        self.description=description
        self.time=time
        self.done=0
        self.strTime=''
        self.strTimeFetch()

    def strTimeFetch(self):
        #Jinja templates could not use the 'round()' function so we have to append the string to the object
        self.strTime=''
        if (self.time%60<10):
            taskMinutes='0'+str(round(self.time%60,0))
        else:
            taskMinutes=str(round(self.time%60,0))
        self.strTime=str(int(round((self.time-self.time%60)/60,0)))+':'+taskMinutes

TodaysBread=DailyPlan(datetime.now().date())
userBase={}
userBase['Michael']=User()



from flask import Flask, render_template,request, send_file, redirect
app = Flask(__name__,static_url_path='/static/')

@app.route('/',methods=['GET'])
def today():
    today=datetime.now().date()
    return redirect('/'+str(today))

@app.route('/<date>/', methods=['GET', 'POST'])
def loadAgenda(date,user='Michael'):
    if request.method == 'GET':
        try:
            today=datetime.now().date()
            print(today)
            return render_template('register.html',dailyplan=userBase[user].agenda[date],today=today)
        except:
            return f'No agenda for mentioned date {date}' 
    if request.method == 'POST':
        #Update State of the objects
        data = request.form
        #We could parse the project before hand to avoid repeitive coding. #Todo
        if data['goal']=='completion':
            userBase[user].agenda[date].projects[int(data['taskId'].split('-')[0])].tasks[int(data['taskId'].split('-')[1])].done=int(data['taskDone'])
        elif data['goal']=='addTask':
            userBase[user].agenda[date].projects[int(data['taskId'].split('-')[0])].addTask('Walk and Feed Coco',60)
        elif data['goal']=='updateTask':
            userBase[user].agenda[date].projects[int(data['taskId'].split('-')[0])].tasks[int(data['taskId'].split('-')[1])].description=data['newText']
        elif data['goal']=='removeTask':
            userBase[user].agenda[date].projects[int(data['taskId'].split('-')[0])].removeTask(int(data['taskId'].split('-')[1]))
        elif data['goal']=='changeTime':
            print(data['time'])
            userBase[user].agenda[date].projects[int(data['taskId'].split('-')[0])].tasks[int(data['taskId'].split('-')[1])].time=int(data['time'].split(':')[0].replace(':',''))*60+(int(data['time'].split(':')[1].replace(':','')))
            userBase[user].agenda[date].projects[int(data['taskId'].split('-')[0])].tasks[int(data['taskId'].split('-')[1])].strTimeFetch()
        elif data['goal']=='addProject':
            userBase[user].agenda[date].addProject('New Project')

        elif data['goal']=='removeProject':
            userBase[user].agenda[date].removeProject(int(data['projectId']))

        elif data['goal']=='updateProject':
            userBase[user].agenda[date].projects[int(data['taskId'])].title=data['newText']
        elif data['goal']=='addWaitingOn':
            userBase[user].agenda[date].waitingOn['New Person'+ str(len(userBase[user].agenda[date].waitingOn))]='Waiting for contract'
        elif data['goal']=='removeWaitingOn':
            del userBase[user].agenda[date].waitingOn[data['personId']]        
        elif data['goal']=='updateWaitingOnPeople':
            description=userBase[user].agenda[date].waitingOn[data['originalValue']]
            del userBase[user].agenda[date].waitingOn[data['originalValue']]
            userBase[user].agenda[date].waitingOn[data['newText']]=description
        elif data['goal']=='updateWaitingOnDescription':
            for people in userBase[user].agenda[date].waitingOn:
                if userBase[user].agenda[date].waitingOn[people]==data['originalValue']:
                    userBase[user].agenda[date].waitingOn[people]=data['newText']
        elif data['goal']=='addReachOut':
            userBase[user].agenda[date].reachOut['New Person'+str(len(userBase[user].agenda[date].reachOut))]='Follow Up'
        elif data['goal']=='removeReachOut':
            del userBase[user].agenda[date].reachOut[data['personId']]
        elif data['goal']=='updateReachOutPeople':
            description=userBase[user].agenda[date].reachOut[data['originalValue']]
            del userBase[user].agenda[date].reachOut[data['originalValue']]
            userBase[user].agenda[date].reachOut[data['newText']]=description
        elif data['goal']=='updateReachOutDescription':
            for people in userBase[user].agenda[date].reachOut:
                if userBase[user].agenda[date].reachOut[people]==data['originalValue']:
                    userBase[user].agenda[date].reachOut[people]=data['newText']


        return render_template('register.html',dailyplan=userBase[user].agenda[date])

@app.route('/<date>/download', methods=['GET', 'POST'])
def downloadAgenda(date,user='Michael'):
    csvfile=userBase[user].agenda[date].downloadAgenda()
    return send_file('jsonfiles/'+str(date)+'.json', as_attachment=True)

@app.route('/<date>/upload', methods=['GET', 'POST'])
def uploadAgenda(date,user='Michael'):
    if request.method == 'POST':
        f = request.files['file']
        f.save('jsonfiles/'+ secure_filename(str(date)+'.json'))
        userBase[user].agenda[date].uploadAgenda('jsonfiles/'+ str(date)+'.json')
    return render_template('register.html',dailyplan=userBase[user].agenda[date])
    
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)

