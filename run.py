import linecache
import cmd
import requests
from os import path
from config import URL, USER, PASS, BASE_PATH

requests.packages.urllib3.disable_warnings()

CLIENTID = 'pydeb'

class DbgShell(cmd.Cmd):
	"""DW debugger class"""

	intro = 'Welcome to DW debugger.   Type help or ? to list commands.\n'
	prompt = '(dw) '
	last_location = None

	def do_connect(self, args):
		'Connect to a specific instance: CONNECT <DOMAIN> <USER> <PASS>'
		print(requests.post(URL + 'client', headers={'x-dw-client-id': CLIENTID}, auth=(USER, PASS), verify=False))
		print(args)

	def do_bp(self, args):
		'Set breakpoint. BP <file> <line>'

		if not args:
			self.do_sb(args)
			return

		args = args.split()

		if args[0] in ('h', 'here'):
			payload = {'breakpoints': [{'line_number': self.last_location['line_number'], 'script_path': self.last_location['script_path']}]}
		else:
			payload = {'breakpoints': [{'line_number': int(args[1]), 'script_path': args[0]}]}
		print(payload)
		response = requests.post(URL + 'breakpoints', headers={'x-dw-client-id': CLIENTID}, auth=(USER, PASS), verify=False, json=payload)
		if response.status_code == requests.codes.ok:
			print('OK')
		else:
			print(response.text)

	def do_sb(self, args):
		'Show breakpoints'
		response = requests.get(URL + 'breakpoints', headers={'x-dw-client-id': CLIENTID}, auth=(USER, PASS), verify=False)

		data = response.json()

		if 'breakpoints' not in data:
			print ('No breakpoints active')
			return

		for bp in data['breakpoints']:
			print ('{}: {}:{}'.format(bp['id'], bp['script_path'], bp['line_number']))

	def do_db(self, args):
		'Delete breakpoint: db <id>'

		response = requests.delete(URL + 'breakpoints/' + args, headers={'x-dw-client-id': CLIENTID}, auth=(USER, PASS), verify=False)
		print(response.json())

	def do_t(self, args):
		'Show thread status'

		response = requests.get(URL + 'threads', headers={'x-dw-client-id': CLIENTID}, auth=(USER, PASS), verify=False)
		data = response.json()

		if 'script_threads' not in data:
			return

		for st in data['script_threads']:
			print ('{}: {}'.format(st['id'], st['status']))

			if st['status'] == 'halted':
				loc = st['call_stack'][0]['location']
				print('    {}  // {}:{}'.format(loc['function_name'], loc['script_path'], loc['line_number']))

	def do_use(self, args):
		'Set thread ID to use: USE <id>'

		self.thread_id = args

	def do_v(self, args):
		'Show local variables'

		try:
			frame = int(args)
		except:
			frame = 0

		response = requests.get(URL + 'threads/{}/frames/{}/members'.format(self.thread_id, frame), headers={'x-dw-client-id': CLIENTID}, auth=(USER, PASS), verify=False)
		data = response.json()

		for var in data['object_members']:
			print('{}: {} (Type: {})'.format(var['name'], var['value'], var['type']))

	def do_st(self, args):
		'Print stack trace for the thread'

		response = requests.get(URL + 'threads/' + self.thread_id, headers={'x-dw-client-id': CLIENTID}, auth=(USER, PASS), verify=False)

		data = response.json()

		self.last_location = data['call_stack'][0]['location']

		for st in data['call_stack']:
			print('{}: {} ({}:{})'.format(st['index'], st['location']['function_name'], st['location']['script_path'], st['location']['line_number']))

		print()
		print_source(self.last_location, 3, 3);

	def do_s(self, args):
		'Step into'

		response = requests.post(URL + 'threads/{}/into'.format(self.thread_id), headers={'x-dw-client-id': CLIENTID}, auth=(USER, PASS), verify=False)
		self.do_st(None)

	def do_so(self, args):
		'Step over'

		response = requests.post(URL + 'threads/{}/over'.format(self.thread_id), headers={'x-dw-client-id': CLIENTID}, auth=(USER, PASS), verify=False)
		self.do_st(None)

	def do_q(self, arg):
		'Exit'
		return True

def print_source(loc, pre, post):
	start = max(loc['line_number'] - pre, 0)
	fn = path.join(BASE_PATH, loc['script_path'][1:])

	for i in range(start, loc['line_number']):
		print('  {}'.format(linecache.getline(fn, i)))

	print('> {}'.format(linecache.getline(fn, loc['line_number'])))

	for i in range(loc['line_number'] + 1, loc['line_number'] + post):
		print('  {}'.format(linecache.getline(fn, i)))

def parse(arg):
	'Convert a series of zero or more numbers to an argument tuple'
	return tuple(map(int, arg.split()))

if __name__ == '__main__':
	try:
		DbgShell().cmdloop()
	finally:
		print(requests.delete(URL + 'client', headers={'x-dw-client-id': CLIENTID}, auth=(USER, PASS), verify=False))

