import pywinauto
import wmi
import psutil
import pyautogui
import PIL

import keyboard

import win32gui
import win32process # "pip install win32api"
import win32api
import win10toast

import numpy as np
import time
import pprint
import cv2 # "pip install opencv-python"
import pytesseract # google tesseract OCR

import os
import openai

openai.api_key = "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"

pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
pp = pprint.PrettyPrinter(depth=4)
toaster = win10toast.ToastNotifier()


def is_visible_and_active(hwnd):
	if win32gui.IsWindowVisible(hwnd):
		client_rect = win32gui.GetClientRect(hwnd)
		if (client_rect[2] - client_rect[0] > 10) and (client_rect[3] - client_rect[1] > 10):
			return True

def distracted(data):
	if data["process_exe"] == "cmd.exebooga":
		return True
	else:
		return False


def get_full_screenshot_text():
	# note: this function can take upto 5 seconds to run
	img = pyautogui.screenshot()
	img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
	text = pytesseract.image_to_string(img)
	return text

def get_window_screenshot_text(hwnd):
	
	bbox = win32gui.GetWindowRect(hwnd)
	img = PIL.ImageGrab.grab(bbox)
	img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
	# After tests, Tesseract model inference is by far most time-consuming step of this function
	text = pytesseract.image_to_string(img)
	return text

def gpt4(input_text):
	messages = []
	temperature = 1
	top_p = 1
	presence_penalty = 0
	frequency_penalty = 0

	user_message = {"role" : "user", "content" : input_text}
	messages.append(user_message)

	response_received = False
	while( not response_received):
		try:
			result = openai.ChatCompletion.create(
			  model="gpt-4",
			  messages = messages,
			  temperature = temperature,
			  top_p = top_p,
			  presence_penalty = presence_penalty,
			  frequency_penalty = frequency_penalty
			)
			response_received = True
		except Exception as e:
			print(e)
			print("OpenAI API error go brrr..")
			time.sleep(10)

	sys_role = result["choices"][0]["message"]["role"]
	sys_content = result["choices"][0]["message"]["content"]
	return sys_content



def gpt_embedding(text, model="text-embedding-ada-002"):
	# text = text.replace("\n", " ")
	response_received = False
	while( not response_received):
		try:
			result = openai.Embedding.create(input = [text], model=model)
			response_received = True
		except Exception as e:
			print(e)
			print("OpenAI API error go brr...")
			time.sleep(10)
	embedding = np.array(result['data'][0]['embedding'])
	return embedding




# create an ada embedding database

ada_DB_D = 1536
ada_DB_N_max = 1000

ada_DB = np.empty((ada_DB_N_max, ada_DB_D))
text_DB = []

# index to fill next entry in ada_DB and text_DB
DB_i = 0


# while True:
for i in range(10):
	time.sleep(5)

	data = {}
	
	# save current time
	data["time"] = time.time()

	hwnd_fore = win32gui.GetForegroundWindow()
	if is_visible_and_active(hwnd_fore) == False:
		raise Exception("wtf")
	# get title of window
	data["window_text"] = win32gui.GetWindowText(hwnd_fore)
	# get thread and process that "created" the window
	(thread_id, process_id) = win32process.GetWindowThreadProcessId(hwnd_fore)
	data["thread_id"] = thread_id
	data["process_id"] = process_id
	# get name of program that created this process, and some data about that process
	p = psutil.Process(process_id)
	with p.oneshot():
		data["process_name"] = p.name()
		data["process_exe"] = p.exe()
		data["process_status"] = p.status()
		data["process_create_time"] = p.create_time()

	# take screenshot of fullscreen or foreground window, and extract text from that
	# data["full_screenshot_text"] = get_full_screenshot_text()
	print("taking screenshot")
	data["window_screenshot_text"] = get_window_screenshot_text(hwnd_fore)

	# pp.pprint(data)

	# print("calling GPT4 API")
	# gpt4_input = "This is a screenshot of my window converted to text. What am I currently doing?\n\n\"\"\"" + data["window_screenshot_text"] + "\"\"\""
	# result = gpt4(gpt4_input)
	# print(result)
	
	text_DB.append(data["window_screenshot_text"])

	print("calling ada embedding API")
	embed = gpt_embedding(data["window_screenshot_text"])
	# print(embed, len(embed))

	ada_DB[DB_i,:] = embed
	DB_i += 1

	print(ada_DB)

	toaster.show_toast("Screenshot taken", str(i), duration=1)
	
	# if distracted(data) == True:
	# 	toaster.show_toast("Stay focussed.", "You may be getting distracted", duration=10)

while True:
	print("type a question as input: ")
	prompt = input("(User:) ")

	print("\ncalling ada embedding API")
	embed = gpt_embedding(prompt)

	print("finding most similar embeddings")
	sims = np.sum(embed * ada_DB, axis = 1)
	n = 3
	top_n_indices = np.argsort(sims)[-n:]
	
	print("found most similar embeddings. calling GPT4 with your query now")
	gpt4_input = prompt
	gpt4_input += "\n\nI have been regularly taking screenshots of my computer and converting them to text. Here are some that may be most relevant to answering the above question."
	for i in range(n):
		gpt4_input += f"\n\nScreenshot {i}:\n\"\"\""
		gpt4_input += text_DB[top_n_indices[i]]
		gpt4_input += "\n\"\"\""

	gpt4_result = gpt4(gpt4_input)
	print(f"\n(GPT4:) {gpt4_result}")





# LOTS OF UNUSED CODE
# NOT DELETED IN CASE I NEED TO REFER TO IT

# print("aaa")
# recorded = keyboard.record(until='esc')
# print(recorded)
# temp = input("enter")


# # gets all open windows using pywinauto
# windows = pywinauto.Desktop(backend="uia").windows()
# print(windows)
# print([w.window_text() for w in windows])

# # gets all processes using WMI
# f = wmi.WMI()
# print("pid   Process name")
# for process in f.Win32_Process():
# 	print(f"{process.ProcessId:<10} {process.Name}")

# # get current python process, and all its attributes, using psutil
# p = psutil.Process()
# attr_all = list(p.as_dict().keys())
# # ['io_counters', 'environ', 'cpu_percent', 'create_time', 'cpu_affinity', 'memory_full_info', 'memory_info', 'cpu_times', 'exe', 'nice', 'ionice', 'threads', 'username', 'ppid', 'memory_percent', 'num_ctx_switches', 'pid', 'cwd', 'num_threads', 'name', 'status', 'cmdline', 'open_files', 'num_handles', 'memory_maps', 'connections']
# attr_some = ['exe', 'name', 'pid', 'ppid', 'status']
# print(p)
# print(attr_all)

# # get all chrome-associated processes (note these maybe be child or parent, and may or may not have active windows)
# chrome_pids = []
# for proc in psutil.process_iter(attr_some):
#  	if proc.info["name"] == "chrome.exe":
#  		chrome_pids.append(proc.info["pid"])
# print(chrome_pids)

# def callback(hwnd, extra):
# 	if win32gui.IsWindowVisible(hwnd):
# 		window_text = win32gui.GetWindowText(hwnd)
# 		client_rect = win32gui.GetClientRect(hwnd)
# 		if (client_rect[2] - client_rect[0] > 10) and (client_rect[3] - client_rect[1] > 10):
# 			print(f"window text: {window_text}")
# 			print(f"client rect: {client_rect}")
# 			(thread_id, process_id) = win32process.GetWindowThreadProcessId(hwnd)
# 			print(thread_id, process_id)
# 			return (thread_id, process_id)
# Enumerate all active windows that occupy space on screen, and parent processes and threads
# win32gui.EnumWindows(callback, None)

# # given a chrome process id, try to maximise any window it is handling - code might not work
# app = pywinauto.application.Application()
# for pid in chrome_pids:
# 	print(pid)
# 	try:
# 		app1 = app.connect(process=pid)
# 		# app1.maximize()
# 		app1.top_window().set_focus()
# 		print("in focus")
# 	except Exception as e:
# 		print(e)

# p = psutil.Process()
# with p.oneshot():
# 	print(p.name(), p.cpu_times(), p.cpu_percent(), p.create_time(), p.ppid(), p.status())
