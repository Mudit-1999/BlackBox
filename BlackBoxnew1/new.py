from flask import *
from forms import *
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,LoginManager,login_user,logout_user,login_required,current_user
from utility import *
import datetime
import time
from flask_mail import *
from random import randint

now = datetime.datetime.now()
app = Flask(__name__)

app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'blackboxbook111@gmail.com',
	MAIL_PASSWORD =  'mudit1234sid'
	)

mail = Mail(app)

movie_display=[]
date_list=[]
timing_list=[]
curr_list=[]
verify=[]

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SECRET_KEY'] = 'my super secret key'.encode('utf8')

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


def __set_sqlite_pragma(db_conn, conn_record):
    cursor = db_conn.cursor()
    cursor.execute('PRAGMA foreign_keys=ON;')
    cursor.close()

class User(UserMixin,db.Model):
	id=db.Column(db.Integer,primary_key=True)
	username=db.Column(db.String(50),unique=True)
	firstname=db.Column(db.String(50))
	lastname=db.Column(db.String(50))
	password=db.Column(db.String(500),nullable=False)
	mobile=db.Column(db.Integer,nullable=False)
	balance=db.Column(db.Float)
	admin=db.Column(db.Boolean)
	all_orders=db.relationship('Order',backref='My_order')

	def __init__(self,firstname,lastname,username,password,mobile):
		self.firstname=firstname
		self.lastname=lastname
		self.username=username
		self.password=password
		self.mobile=mobile	
		self.balance=100
		self.admin=False;


class Movie(UserMixin,db.Model):                    #donno what it does...
	id=db.Column(db.Integer,primary_key=True)
	movie_name=db.Column(db.String(50))
	no_seats=db.Column(db.Integer,nullable=False)
	movie_date=db.Column(db.String(50))
	movie_time=db.Column(db.String(50))
	movie_price=db.Column(db.Integer,nullable=False)
	seats=db.relationship('Seat',cascade="all,delete",backref='Movieshow')
	movie_bookable=db.Column(db.Boolean)

	def __init__(self,movie_name,no_seats,movie_date,movie_time,movie_price):
		self.movie_name=movie_name
		self.no_seats=no_seats
		self.movie_date=movie_date
		self.movie_time=movie_time
		self.movie_price=movie_price
		self.movie_bookable=True

class Seat(UserMixin,db.Model):
	id=db.Column(db.Integer,primary_key=True)
	user_id=db.Column(db.Integer)
	booked=db.Column(db.Boolean)
	seatactual=db.Column(db.Integer)
	movie_id=db.Column(db.Integer,db.ForeignKey('movie.id'))


class Order(UserMixin,db.Model):
	id=db.Column(db.Integer,primary_key=True)
	movie_name=db.Column(db.String(50))
	no_seats=db.Column(db.Integer,nullable=False)
	seat_number=db.Column(db.String(50),nullable=False)
	movie_date=db.Column(db.String(50))
	movie_timing=db.Column(db.String(50))
	movie_price=db.Column(db.Integer,nullable=False)
	net_cost=db.Column(db.Integer,nullable=False)
	booking_date=db.Column(db.String(50),nullable=False)
	booking_time=db.Column(db.String(50),nullable=False)
	cancel=db.Column(db.Boolean)
	user_id=db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

	def __init__(self,movie_name,no_seats,movie_date,movie_time,movie_price,user_id,net_cost,seat_number):
		self.movie_name=movie_name
		self.no_seats=no_seats
		self.movie_date=movie_date
		self.movie_timing=movie_time
		self.movie_price=movie_price
		self.user_id=user_id
		self.net_cost=net_cost
		self.seat_number=seat_number
		self.cancel=False
		self.booking_date=now.strftime("%y-%m-%d")
		self.booking_time=now.strftime("%H:%M")

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route('/')
def index():
	return redirect(url_for('BlackBox'))

@app.route('/BlackBox')
def BlackBox():
	return render_template('layout.html')

@app.route('/BlackBox/register' ,methods= ['POST' , 'GET'])
def register():
	if current_user.get_id() != None:
		return redirect(url_for('BlackBox'))
	form=Register_form(request.form)
	if request.method == 'POST':
		fname=request.form['fname']
		lname=request.form['lname']
		usr=request.form['email']
		pwd=request.form['pwd']
		cpwd=request.form['cpwd']
		mob_no=request.form['mob']

		if form.validate()==True:   
			dup=User.query.filter_by(username=usr).all() 
			if dup !=[]:
				print (dup) 
				flash('E-mail id already register')
				redirect(url_for('register'))
			else:
				pwd=hash_me_out(pwd)
				add_user=User(fname,lname,usr,pwd,mob_no)
				db.session.add(add_user)
				db.session.commit()
				print('Welcome to our BlackBox Family')
				flash('Welcome to our BlackBox Family')
				return redirect(url_for('logintoblackbox'))
		else:
			flash('All fields are required')
			print('All fields are required')
			print(form.errors)
			return render_template('register.html',form=form)

	return render_template('register.html',form=form)

@app.route('/BlackBox/login' ,methods=['POST','GET'])
def logintoblackbox():
	if current_user.get_id() != None:
		return redirect(url_for('BlackBox'))
	if request.method =='POST':
		usr=request.form['usr']
		pwd=request.form['pwd']
		print("hi")
		pwd=hash_me_out(pwd) 
		registered_user = User.query.filter_by(username=usr,password=pwd).first()
		if registered_user is None:
			flash('Invalid Username or Password')
			print('Invalid Username or Password')
			return redirect(url_for('logintoblackbox'))
		else:
			login_user(registered_user)
			return redirect(url_for('BlackBox'))
	return render_template('login.html')

@app.route('/BlackBox/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('BlackBox'))

@app.route('/BlackBox/addmovie',methods=['POST','GET'])
@login_required
def addmovie():#in the admin.html nav bar show admin to add movie also...
	if current_user.admin==False:
		flash('You are not a Admin so fuck off')
		return redirect(url_for('home'))
	if request.method=='POST':
		movie_name=request.form['movie_name']
		no_seats=request.form['no_seats']
		movie_date=request.form['movie_date']
		movie_time=request.form['movie_time']
		movie_price=request.form['movie_price']

		if compare_date(movie_date,movie_time)==False:
			print('Invalid Data')
			flash('Invalid Data')
		else:
			dup=Movie.query.filter_by(movie_name=movie_name,movie_date=movie_date,movie_time=movie_time).all()
			if dup ==[]:
				add_movie=Movie(movie_name,no_seats,movie_date,movie_time,movie_price)
				db.session.add(add_movie)
				db.session.commit()
				no_seats=int(no_seats)
				for i in range(no_seats):
					add_seat=Seat(booked=False,seatactual=i,Movieshow=add_movie)
					db.session.add(add_seat)
					db.session.commit()			
				print('Movie added')
				flash('Movie added')
			else:
				print('Alredy exits')
				flash('Alredy exits')
	return render_template('admin.html')

@app.route('/BlackBox/show')
def show():		
	temp=Movie.query.filter_by(movie_bookable=True).all()
	for i in temp:
		if i.movie_name not in movie_display:
			movie_display.append(i.movie_name)

	for i in movie_display:
		temp=Movie.query.filter_by(movie_name=i,movie_bookable=True).all()
		temp1=set()
		for j in temp:
			temp1.add(str(j.movie_date))
		date_list.append(list(temp1))
	for i in range(0,len(movie_display)):
		temp2=[]
		for j in date_list[i]:
			temp=Movie.query.filter_by(movie_name=movie_display[i],movie_date=j,movie_bookable=True).all()
			temp1=set()
			for k in temp:
				temp1.add(k.movie_time)
			temp2.append(list(temp1))
		timing_list.append(temp2)
	# print('fr',timing_list[0][0])	
	return render_template('show.html',current_user=current_user,movie_display=movie_display,timing_list=timing_list,date_list=date_list)		

@app.route('/BlackBox/show/seats' ,methods=['POST','GET'])
def seats():
	if request.method=='POST':
		value=request.form['show_time']
		value=int(value)
		k=int(value%100)
		j=int((value/100)%100)
		i=int((value/10000)%100)
		movie_name=movie_display[i]
		movie_date=date_list[i][j]
		movie_time=timing_list[i][j][k]
		curr_list.clear()
		curr_list.append(movie_name)
		curr_list.append(movie_date)
		curr_list.append(movie_time)
		print(movie_name,movie_time,movie_date)
		qq= Movie.query.filter_by(movie_name=movie_name, movie_time=movie_time, movie_date=movie_date).first()
		python_var=qq.no_seats
		pp=qq.id
		var1 = (python_var-1)//10 +1
		var2 = (python_var)%10
		print(python_var,var1,var2)
		bookq=[]
		temp=Seat.query.filter_by(movie_id=pp).all()
		for i in temp:
			bookq.append(i.booked)
		return render_template('seats.html',var1=var1,var2=var2,booked=bookq)
	return redirect(url_for('show'))

@app.route('/BlackBox/order' ,methods=['POST','GET'])
def order():
	if current_user.get_id() == None:
		return redirect(url_for('logintoblackbox'))
	if request.method=='POST':
		seat_list=request.form.getlist('seats')
		num_booked=len(seat_list)
		seatstr=''
		price=Movie.query.filter_by(movie_name=curr_list[0], movie_time=curr_list[2], movie_date=curr_list[1]).first().movie_price
		net=price*num_booked
		wallet_balance=User.query.filter_by(id=current_user.get_id()).first().balance
		if net > int(wallet_balance) :
			flash("Not enough Money!!! Transtion Failed")
			print(int(net)-int(wallet_balance))
			return redirect(url_for('wallet'))

		qq=Movie.query.filter_by(movie_name=curr_list[0], movie_time=curr_list[2], movie_date=curr_list[1]).first().id
		for i in seat_list:
			Seat.query.filter_by(seatactual=i,movie_id=qq).update(dict(booked=True,user_id=current_user.get_id()))
			db.session.commit()
			seatstr=seatstr + str(i) + ','

		now = datetime.datetime.now()
		orderadd=Order(curr_list[0],num_booked,curr_list[1],curr_list[2],price,current_user.get_id(),net,seatstr)
		User.query.filter_by(id=current_user.get_id()).update(dict(balance= int (wallet_balance) -int(net) ) )
		db.session.add(orderadd)
		db.session.commit()
		reciver=[]
		reciver.append(User.query.filter_by(id=current_user.get_id()).first().username)
		msg = Message('Hello', sender = 'blackboxbook111gmail.com', recipients = reciver)
		msg.body = "You have successfully booked your ticket"
		mail.send(msg)	
	return redirect(url_for('wallet'))


@app.route('/BlackBox/bookinghistory',methods=['POST' , 'GET'] )
@login_required
def bookinghistory():
	usr_id=current_user.get_id()
	if request.method=='POST':
		value=request.form['refund']
		
		mm=Order.query.filter_by(id=value).first()
		refund=mm.net_cost
		qq=Movie.query.filter_by(movie_name=mm.movie_name,movie_date=mm.movie_date,movie_time=mm.movie_timing).first().id
		wallet_balance=User.query.filter_by(id=current_user.get_id()).first().balance
		seat_list=mm.seat_number.split(',')
		print(len(seat_list)-1)
		print(qq)

		for i in range(0, len(seat_list)-1 ):
			Seat.query.filter_by(user_id=current_user.get_id(),movie_id=qq,seatactual=seat_list[i]).update(dict(booked=False))
			db.session.commit()

		User.query.filter_by(id=current_user.get_id()).update(dict(balance=int(refund) + int (wallet_balance)))
		db.session.commit()
		Order.query.filter_by(id=value).update(dict(cancel=True))
		db.session.commit()
		print(int(refund) + int (wallet_balance))
		return redirect(url_for('bookinghistory'))
	show=Order.query.filter_by(user_id=usr_id).all()
	status=get_status(show)
	return render_template('orderhistory.html',show=show,status=status)

@app.route('/BlackBox/forgotpassword' ,methods=['POST' , 'GET'])
def forgotpassword():
	if current_user.get_id() != None:
		return redirect(url_for('BlackBox'))

	if request.method=='POST':
		usr=request.form['usr']
		print(usr)
		registered_user = User.query.filter_by(username=usr).first()
		if registered_user is None:
			flash('Invalid Username')
			print('Invalid Username ')
			return redirect(url_for('forgotpassword'))
		else:
			reciver=[]
			reciver.append(usr)
			verify.clear()
			verify.append(randint(1000, 9999))
			verify.append(usr)
			msg = Message('Hello', sender = 'blackboxbook111gmail.com', recipients = reciver)
			msg.body = "Your verification code id " + str(verify[0])
			mail.send(msg)	
			return redirect(url_for('reset'))
	return render_template('forgotpass.html')


@app.route('/BlackBox/reset' ,methods=['POST' , 'GET'])
def reset():
	if current_user.get_id() != None:
		return redirect(url_for('BlackBox'))
	if request.method=='POST':
		verifcode=request.form['usr']
		pwd=request.form['pwd']
		pwd=hash_me_out(pwd)
		if int(verifcode)==int(verify[0]): 
			User.query.filter_by(username=verify[1]).update(dict(password=pwd))
			db.session.commit()
			flash('Password Successfully Changed')
			print('Password Successfully Changed')
			return redirect(url_for('logintoblackbox'))
		else:	
			return redirect(url_for('reset'))
	return render_template('reset.html')


@app.route('/BlackBox/deletemovie' ,methods=['POST' , 'GET'])
@login_required
def deletemovie():        #in the admin.html nav bar show admin to add movie also...
	if current_user.admin==False:
		flash('You are not a Admin so fuck off')
		print('You are not a Admin so fuck off')
		return redirect(url_for('home'))
	else:
		me=Movie.query.all()
		for i in me:
			if compare_date(i.movie_date,i.movie_time)==False:
				db.session.delete(i)
				db.session.commit()
		return redirect(url_for('BlackBox'))

@app.route('/BlackBox/wallet' ,methods=['POST' , 'GET'])
@login_required
def wallet():
	wallet_balance=User.query.filter_by(id=current_user.get_id()).first().balance
	print(wallet_balance)
	if request.method=='POST':
		money=request.form['money']
		money=float(wallet_balance) + float(money)
		print(money)
		User.query.filter_by(id=current_user.get_id()).update(dict(balance=money))
		db.session.commit()
		return redirect(url_for('wallet'))
	return render_template('wallet.html',wallet_balance=wallet_balance)
if __name__=='__main__':
   app.run(debug=True)
