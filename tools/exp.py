# !/usr/bin/python
# coding: UTF-8

import random
import shanten
from agari import *

class Exp() :
	def __init__(self, jun, rest, junme) :
		self.jun = jun
		self.rest = rest
		
		self.ba = [0, 0, 0, 0, 0]
		self.jokyo_yaku = [1 if i <= 1 else 0 for i in range(55)]
		
		self.exp = self.calc_exp_at_noten(junme)
		
		self.tejun = []
		
	def calc_exp_at_tempai(self, junme) :
		exp = [0 for i in range(34)]
		
		for i in shanten.get_muko(self.jun, 0) :
			self.jun[i] -= 1
			
			prob = []
			n_yuko = sum([self.rest[j] for j in shanten.get_yuko(self.jun, self.rest, 0)])
			
			for j in range(junme, 18) :
				prob.append((1 - sum(prob)) * n_yuko / (122 - j))
			
			for j in shanten.get_yuko(self.jun, self.rest, 0) :
				self.jun[j] += 1
				exp[i] += sum(prob) * self.rest[j] / n_yuko * Agari(self.jun, [], self.ba, self.jokyo_yaku).get_ten(j)[0]
				self.jun[j] -= 1	
					
			self.jun[i] += 1
		
		return exp
		
	def calc_exp_at_noten(self, junme) :
		exp = [0 for i in range(34)]
		
		if shanten.calc_shanten(self.jun) == 0 :
			return self.calc_exp_at_tempai(junme)
		
		for i in shanten.get_muko(self.jun, 0) :
			self.jun[i] -= 1
			
			prob = []
			n_yuko = sum([self.rest[j] for j in shanten.get_yuko(self.jun, self.rest, 0)])
		
			for j in range(junme, 18) :
				prob.append((1 - sum(prob)) * n_yuko / (122 - j))
				
			for j in shanten.get_yuko(self.jun, self.rest, 0) :
				self.jun[j] += 1
				# restを1引かないと二度受けが上手くいかない 
				self.rest[j] -= 1
				for k in range(junme, 18) :
					exp[i] += (1 - sum(prob[0:k-junme])) * (self.rest[j] + 1) / (122 - k) * max(self.calc_exp_at_noten(k + 1))
				self.rest[j] += 1
				self.jun[j] -= 1	
					
			self.jun[i] += 1
		
		return exp
			
		