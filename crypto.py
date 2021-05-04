import re
import requests


class Crypto:

	def __init__(self):
		self.response = requests.get('https://www.coingecko.com/en')

	def get_list(self):
		numbers = re.findall(r'[$]\d+.\d+', self.response.text)
		prices = []
		for i in range(len(numbers)):
			if i % 3 == 0:
				prices.append(numbers[i])
		names = re.findall(r'coin-name" data-text=\'\w+', self.response.text)
		for i in range(len(names)):
			names[i] = names[i][22:-1] + names[i][-1]
		return names, prices
