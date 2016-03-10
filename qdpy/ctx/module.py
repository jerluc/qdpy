import json

class AppendingDict(dict):
    def __init__(self):
        self.__data = {}

    def __getattribute__(self, name):
        print('Calling getattribute with %s' % name)
        if name in ['setdefault', '_AppendingDict__data', 'json']:
            return object.__getattribute__(self, name)
        return None

    def setdefault(self, name, value):
        # TODO: I guess this is what it does?
        self.__data[name] = [value]

    def __getitem__(self, name):
        print('Getting an item in the namespace %s' % name)
        values = self.__data.get(name)
        if values:
            return values[-1]
        else:
            raise KeyError('No such key \'%s\'' % name)

    def __setitem__(self, name, value):
        print('Setting an item in the namespace %s => %s' % (name, value))
        if name not in self.__data:
            self.__data[name] = []
        self.__data[name].append(value)
        
    def __delitem__(self, name):
        if name in self.__data:
            return self.__data[name].pop()
            if not self.__data:
                del self.__data[name]
        else:
            raise KeyError('No such key \'%s\'' % name)

    def json(self):
        print('Converting to JSON')
        return json.dumps(self.__data)

    @property
    def __dict__(self):
        print('Being called')
        return self


class CodeNamespace(AppendingDict):
    def __init__(self):
        super(AppendingDict, self).init()

class ContextModule(object):
    '''
    A ContextModule instance acts like a normal Python module, but maintains the globally-
    distributed QDPy environment. Care must be taken to maintain consistency in managing basic
    attribute ACLs, so as not to impede upon other QDPy clients. For now, this purely involves
    enforcing that writes to the distributed context only overwrite locally-owned bindings. Any
    attempts to overwrite a global binding results in "masking" the global binding with a local
    one.
    '''

    def __init__(self, group=None):
        self.__group = group
        self.__locals = {}

    @property
    def __path__(self):
        return ''

    def __is_internal_attr(self, name):
        return name.startswith('_')

    def __get_internal_attr(self, name):
        return object.__getattribute__(self, name)

    def __set_internal_attr(self, name, value):
        object.__setattr__(self, name, value)

    @property
    def __globals(self):
        return {}

    @property
    def __merged_context(self):
        merged = self.__globals.copy()
        merged.update(self.__locals.copy())
        return merged

    def __getattr__(self, name):
        print('__getattr__ being called with %s' % name)
        if self.__is_internal_attr(name):
            return self.__get_internal_attr(name)
        if name in self.__merged_context:
            return self.__merged_context[name]
        else:
            raise AttributeError('No such attributed \'%s\'' % name)

    def __setattr__(self, name, value):
        print('__setattr__ being called with %s => %s' % (name, value))
        if self.__is_internal_attr(name):
            self.__set_internal_attr(name, value)
        else:
            if name in self.__globals:
                print('WARNING: masking distributed variable [%s]' % name)
            # TODO: Update the distributed context
            self.__locals[name] = value

    def setdefault(self, name, value):
        self.__setattr__(name, value)

    def __dir__(self):
        return self.__merged_context.keys()

    @property
    def __dict__(self):
        print('Using dict')
        return self.__locals

