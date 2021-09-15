import tempfile
from os import path

from androguard.core.bytecodes.axml import AXMLPrinter
from lxml import etree

from .utils import extract_zip_file


class AndroidManifest:
	ANDROID_NAMESPACE = '{http://schemas.android.com/apk/res/android}'

	@staticmethod
	def from_apk(apk_path):
		with tempfile.TemporaryDirectory() as tmp_dir_path:
			extract_zip_file(apk_path, tmp_dir_path)
			manifest_path = path.join(tmp_dir_path, 'AndroidManifest.xml')
			manifest = AndroidManifest(manifest_path)
			return manifest

	def __init__(self, file_path):
		with open(file_path, "rb") as fp:
			axml = AXMLPrinter(fp.read())
			# Get the lxml.etree.Element from the AXMLPrinter:
			self.root = axml.get_xml_obj()

	def __str__(self):
		s = etree.tostring(self.root).decode('utf8')
		return s

	def get_package_name(self):
		return self.root.attrib['package']

	def get_package_version(self):
		return self.root.attrib[AndroidManifest.ANDROID_NAMESPACE + 'versionName']

	def get_main_activity(self):
		package_name = self.get_package_name()
		for application in self.root.iter('application'):
			for activity in application.iter('activity'):
				activity_name = activity.get(AndroidManifest.ANDROID_NAMESPACE + 'name')
				# add package name
				if activity_name[0] == '.':
					activity_name = package_name + activity_name
				# find mainActivity
				for inter in activity.iter('intent-filter'):
					for action in inter.iter('action'):
						if action.get(AndroidManifest.ANDROID_NAMESPACE +
						              'name') == 'android.intent.action.MAIN':
							for cate in inter.iter('category'):
								if cate.get(AndroidManifest.ANDROID_NAMESPACE +
								            'name') == 'android.intent.category.LAUNCHER':
									return activity_name
		return None
