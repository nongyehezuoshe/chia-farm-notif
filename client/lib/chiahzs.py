import time,json,os,sys,requests
# from bech32m_chia import bech32m
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


cwd=os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
os.chdir(cwd)
options=json.loads(open(os.path.join(cwd,"config/options.json"),"rb").read())

def log_show(line,text):
	# tool_print(str(sys._getframe().f_lineno)+" "+"show","message")
	print("\033[7m"+time.strftime("%H:%M:%S ", time.localtime())+str(line)+": "+"\033[0m",text)

def opt_get(type):
	return options.get(type, {}).get("value", False)