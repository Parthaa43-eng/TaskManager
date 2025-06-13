from flask import Flask , render_template , request , redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///TaskSchedular.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class TaskSchedular(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(1000), nullable=True)

    # NEW COLUMNS
    scheduled_time = db.Column(db.DateTime, nullable=False)       # Task perform karne ka time
    remind_before = db.Column(db.Integer, default=10)             # Kitne min pehle notify karna hai
    user_email = db.Column(db.String(200), nullable=False) 
    is_completed = db.Column(db.Boolean, default=False)           # Mark as done or not
    status = db.Column(db.String(20), default="Pending")          # Can be: Pending, Done, Cancelled, etc.
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

#Index route
@app.route("/")
def home():
    allTasks = TaskSchedular.query.order_by(TaskSchedular.scheduled_time).all() # DOes here this mean we are fetching all entries with respect to all tasks sceduled time ?
    
    return render_template("allTasks.html" , tasks = allTasks)

#Route to add task

@app.route("/add" , methods = ["GET" , "POST"])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description') # Plaese tell me why we use here .get() method and not dorectly request.form['description'] ?
        scheduled_time_str = request.form['scheduled_time']  # string from form
        remind_before = int(request.form['remind_before'])
        user_email = request.form['user_email']
        scheduled_time = datetime.strptime(scheduled_time_str, "%Y-%m-%dT%H:%M")

        task =TaskSchedular (
            title = title,
            description = description,
            scheduled_time=scheduled_time,
            remind_before=remind_before,
            user_email=user_email
        )

        db.session.add(task)
        db.session.commit()

        return redirect("/")
    
    return render_template('addTask.html')


#Delete route
@app.route("/delete/<int:sno>")
def deleteTask(sno):
    task = TaskSchedular.query.get(sno)
    db.session.delete(task)
    db.session.commit()
    return redirect("/")

#Complete Route
@app.route("/complete/<int:sno>")
def isComplete(sno):
    task = TaskSchedular.query.get(sno)
    if task.is_completed == False:
        task.is_completed = True
        task.status = "Done"
        db.session.commit()
        return redirect("/")
    
    if task.is_completed == True:
        task.is_completed = False
        task.status = "Pending"
        db.session.commit()
        return redirect("/")

    


#Update route
@app.route("/update/<int:sno>" , methods = ['POST' , 'GET'])
def updateTask(sno):
    task = TaskSchedular.query.get(sno)

    if request.method == "POST":
        task.title = request.form['title']
        task.description = request.form.get('description')
        scheduled_time_str = request.form['scheduled_time']
        task.scheduled_time = datetime.strptime(scheduled_time_str, "%Y-%m-%dT%H:%M")
        task.remind_before = int(request.form['remind_before'])
        task.user_email = request.form['user_email']

        db.session.commit()
        return redirect("/")
    
    return render_template("update.html" , task = task)
if __name__ == '__main__':
    app.run(debug= True , port = 8080)
