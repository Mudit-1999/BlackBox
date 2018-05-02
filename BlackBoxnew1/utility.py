from datetime import *
from hashlib import sha512 as fun


def compare_date(mov_date,mov_time):
	mov_date=datetime.strptime(mov_date, "%Y-%m-%d").date()
	mov_time=datetime.strptime(mov_time, '%H:%M').time()
	now=datetime.now()
	if now.date() > mov_date:
		return False
	elif now.date()==mov_date:
		if now.time() >mov_time:
			return False
	return True

def hash_me_out(pwd):
	pwd=pwd.encode()
	return fun(pwd).hexdigest()	

def get_status(show):
	status=[]
	for i in show:
		if i.cancel==True:
			status.append('CANCELED/REFUND INITIATED')
		elif compare_date(i.movie_date,i.movie_timing) == False:
			status.append('COMPLETED')
		else:
			status.append('UPCOMING')
	return status