from ascript.ios.developer.api import  api_module


def module_get(args):
    name = args['name']
    api_module.api_module_files(args)
    pass