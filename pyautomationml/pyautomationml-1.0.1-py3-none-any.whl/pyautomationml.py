import os
import sys
import lxml.objectify as ob
import lxml.etree as et


class AmlElement:
    def __init__(self, element, context_global, context_local):
        self.__element__ = element
        self.__context_local__ = context_local
        self.__context_global__ = context_global

    def __getattr__(self, key):
        if key == "fun":
            self.__context_local__.update({"ancestors": self.iterancestors()})
            result = eval(self.text(), self.__context_global__, self.__context_local__)
            self.__context_local__.pop("ancestors")
        else:
            result = self.__dict__.get(key, self.__element__.__getattribute__(key))
            if isinstance(result, ob.ObjectifiedElement):
                result = AmlElement(result, self.__context_global__, self.__context_local__)
        return result

    def __setattr__(self, key, value):
        if key in ("__element__", "__context_local__", "__context_global__"):
            self.__dict__[key] = value
        else:
            self.__element__.__setattr__(key, value)

    def __repr__(self):
        return "<AmlElement object {0} Name={1}>".format(self.__element__.tag, self.__element__.get('Name'))

    def iterancestors(self):
        return [AmlElement(i, self.__context_global__, self.__context_local__) for i in [self.__element__] + list(self.__element__.iterancestors())]

    def iterchildren(self):
        result = self.__element__.iterchildren()
        return [AmlElement(i, self.__context_global__, self.__context_local__) for i in result] if result is not None else None

    def find(self, path):
        result = self.__element__.find(path)
        return AmlElement(result, self.__context_global__, self.__context_local__) if result is not None else None

    def findall(self, path):
        result = self.__element__.findall(path)
        return [AmlElement(i, self.__context_global__, self.__context_local__) for i in result] if result is not None else None

    def get_child_by_name(self, name):
        return self.find(f"./*[@Name='{name}']")

    def text(self):
        return self.__element__.Value.text


class PyAutomationML:
    def __init__(self, source_file):
        self.source_file = source_file
        self.context_local = {}
        self.context_global = {}
        self.root = AmlElement(ob.parse(self.source_file).getroot(), self.context_global, self.context_local)

    def eval(self, verbose=False):
        evaluated = 0
        not_evaluated = 0
        errors = 0

        preamble_file = self.root.find(
            "./InstanceHierarchy//InternalElement[@Name='PythonPreamble']/ExternalInterface/Attribute[@Name='refURI']").text()
        if preamble_file is not None:
            with open(preamble_file) as preamble:
                exec(preamble.read(), self.context_global, self.context_local)

        expression_elements = self.root.findall("./InstanceHierarchy//Attribute[@RefAttributeType='PyAMLLib/PythonExpression']")

        for element in expression_elements:
            try:
                self.context_local.update({"ancestors": element.iterancestors()})
                result = eval(element.text(), self.context_global, self.context_local)
                self.context_local.pop("ancestors")
            except Exception as e:
                errors += 1
                with open(self.source_file) as source:
                    print("Error in line {0} in file {1}\n          {2} \n{3}\n".format(element.sourceline + 1,
                                                                                        self.source_file,
                                                                                        element.text(),
                                                                                        e), file=sys.stderr)
            else:
                if not callable(result):
                    evaluated += 1
                    element.Value._setText(str(result))
                else:
                    not_evaluated += 1

        self.root.__context_local__ = self.context_local
        self.root.__context_global__ = self.context_global

        if verbose:
            print("{0} total PythonExpression{1} found".format(len(expression_elements), "s" if len(expression_elements) > 1 else ""), file=sys.stderr)
            print("{0} PythonExpression{1} successfully instantiated as literals.".format(evaluated, "s" if evaluated > 1 else ""), file=sys.stderr)
            print("{0} PythonExpression{1} could not be instantiated as literal{2} because {3} functions.".format(
                not_evaluated, "s" if not_evaluated > 1 else "", "s" if not_evaluated > 1 else "", "they are" if not_evaluated > 1 else "it is a"), file=sys.stderr)
            if errors:
                print("{0} PythonExpression{1} could not be instantiated as literal{2} because of errors.".format(
                    errors, "s" if errors > 1 else "", "s" if errors > 1 else ""), file=sys.stderr)

    def save(self, filename=None):
        if not filename:
            old_filename, file_extension = os.path.splitext(self.source_file)
            filename = old_filename + "_instantiated" + file_extension
        with open(filename, "wb") as file:
            file.write(et.tostring(self.root.__element__, pretty_print=True))
