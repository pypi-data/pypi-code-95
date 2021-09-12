__all__ = ['add_download_tool', 'add_convert_tool', 'get_download_tool', 'get_convert_tool', 'print_download_tools', 'print_convert_tools']

download_tools = {}
convert_tools = {}

def add_download_tool(name, obj):
    download_tools[name] = obj

def add_convert_tool(src_name, dst_name, obj):
    name = "%s->%s" % (src_name, dst_name)
    convert_tools[name] = obj

def get_download_tool(name):
    return download_tools[name]

def get_convert_tool(src_name, dst_name):
    name = "%s->%s" %(src_name, dst_name)
    return convert_tools[name]

def print_download_tools():
    print(download_tools)

def print_convert_tools():
    print(convert_tools)