import checkpy.tests as t
import checkpy.lib as lib
import checkpy.assertlib as asserts

def sandbox():
	lib.require("sandbox.py")
	lib.require("sandboxTest.py", "https://raw.githubusercontent.com/Jelleas/tests/master/tests/someTest.py")

@t.test(0)
def exactlyFoo(test):
	def testMethod():
		output = lib.outputOf(test.fileName, overwriteAttributes = [("__name__", "__main__")])
		return asserts.exact(output.strip(), "foo")

	test.test = testMethod
	test.description = lambda : "prints exactly: foo"

@t.test(10)
def requiredFilesExist(test):
	test.test = lambda : asserts.fileExists("sandbox.py") and asserts.fileExists("sandboxTest.py")
	test.description = lambda : "sandbox.py and sandboxTest.py exist"