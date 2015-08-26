import random

alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789.,/!@#$%^&*()_+=-}{[]":;?'
pw_length = 20
my_pw = ''

for i in range(pw_length):
	next_index = random.randrange(len(alphabet))
	if random.randrange(2):
		my_pw = my_pw + alphabet[next_index].upper()
	else:
		my_pw = my_pw + alphabet[next_index]


print my_pw