
class CommonMethods:

    def get_reference(self, referencepath, open_api_doc):
        """
        The method get_reference gets the values associated to a given path.
        For example, the reference is something of format like #/compnents/schemas/schemaname
        :param open_api_doc:
        :param referencepath:
        :return:
        """
        try:
            open_doc_stack = open_api_doc.items()
            reference_path_list = []
            ##break the reference path to multiple elements
            if str(referencepath).startswith("#/"):
                referencepath=referencepath.replace("#/","")
            if referencepath.__contains__("/"):
                reference_path_list = referencepath.split("/")
            else:
                reference_path_list.append(referencepath)

            ##TODO Just a temporary looper, need to check the DFS for wider coverage
            #Now iterate through the reference path
            for key in reference_path_list:
                if key in open_api_doc.keys():
                    open_api_doc=open_api_doc[key]
                else:
                    return None
            return open_api_doc

        except Exception as e:
            print()

    def check_references(self,endpoint_content, open_api_doc):
        """

        :param url_path:
        :param open_api_doc:
        :return:
        """
        try:
            for key,value in endpoint_content.items():
                if isinstance(value,dict):
                    endpoint_content[key] = self.check_references(value,open_api_doc)
                if isinstance(value, list):
                    for iteration_number in range(len(value)):
                        value[iteration_number] = self.check_references(value[iteration_number], open_api_doc)

                elif key== "$ref":
                    reference_element =self.get_reference(value,open_api_doc)
                    endpoint_content[key] = self.check_references(reference_element, open_api_doc)
            return endpoint_content
        except Exception as e:
            print()