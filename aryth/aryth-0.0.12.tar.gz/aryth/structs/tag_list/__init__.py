class TagList(list):
    def __init__(self, vec, **kwargs):
        super().__init__(vec)
        self.__dict__.update(kwargs)


# tag_list = TagList([1, 2, 3], max=3, min=1)
# print(tag_list.__dict__)
