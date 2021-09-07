import os
import sys
import time
import keyboard

class CreateMenu():
	def __init__(self, title: str, elements: list):
		self.title = title
		self.elements = elements
		self.selected = 0
		self.hotkeys = False

	def load_menu(self):
		print(' ' + self.title)
		for i in range(0, len(self.elements)):
			print("{1} {0} {2}".format(self.elements[i], ">" if self.selected == i else " ", "<" if self.selected == i else " "))

	def wait(self):
		keyboard.add_hotkey('up', self.up)
		keyboard.add_hotkey('down', self.down)
		keyboard.add_hotkey('enter', self.enter)

		keyboard.wait('enter')

	def up(self):
		if self.selected == 0: return

		self.selected -= 1

		os.system('cls')
		self.load_menu()

	def down(self):
		if self.selected == len(self.elements) - 1: return

		self.selected += 1

		os.system('cls')
		self.load_menu()

	def get_selected_item(self):
		return self.selected

	def enter(self):
		os.system('cls')