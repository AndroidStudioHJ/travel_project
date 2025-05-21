# ------------------------------------------------------------------------
# Copyright (c) 2022 megvii-model. All Rights Reserved.
# ------------------------------------------------------------------------
# Modified from BasicSR (https://github.com/xinntao/BasicSR)
# Copyright 2018-2020 BasicSR Authors
# ------------------------------------------------------------------------

class Registry:
    """A registry to map strings to classes.
    Args:
        name (str): Registry name.
    """

    def __init__(self, name):
        self._name = name
        self._module_dict = dict()

    def __len__(self):
        return len(self._module_dict)

    def __contains__(self, key):
        return self.get(key) is not None

    def __repr__(self):
        format_str = self.__class__.__name__ + \
            f'(name={self._name}, items={list(self._module_dict.keys())})'
        return format_str

    @property
    def name(self):
        return self._name

    @property
    def module_dict(self):
        return self._module_dict

    def get(self, key):
        """Get the registry record.
        Args:
            key (str): The class name in string format.
        Returns:
            class: The corresponding class.
        """
        return self._module_dict.get(key, None)

    def _register_module(self, module_class, module_name=None, force=False):
        """Register a module.
        Args:
            module_class (type): Module class to be registered.
            module_name (str | None): The module name to be registered. If not
                specified, the class name will be used.
            force (bool, optional): Whether to override an existing class with
                the same name. Default: False.
        """
        if not isinstance(module_class, type):
            raise TypeError(f'module must be a class, but got {type(module_class)}')

        if module_name is None:
            module_name = module_class.__name__
        if not force and module_name in self._module_dict:
            raise KeyError(f'{module_name} is already registered in {self.name}')
        self._module_dict[module_name] = module_class

    def register_module(self, cls=None, module_name=None, force=False):
        """Register a module class.
        Args:
            cls (type | None): Module class to be registered. If None, it will
                be a decorator.
            module_name (str | None): The module name to be registered. If not
                specified, the class name will be used.
            force (bool, optional): Whether to override an existing class with
                the same name. Default: False.
        Returns:
            type: The registered module class.
        """
        if cls is None:
            return lambda x: self.register_module(x, module_name=module_name, force=force)
        self._register_module(cls, module_name=module_name, force=force)
        return cls

    def register(self, cls=None, module_name=None, force=False):
        """Register a module class.
        This is an alias of register_module.
        """
        return self.register_module(cls, module_name, force)

# Create registries
ARCH_REGISTRY = Registry('arch')
DATASET_REGISTRY = Registry('dataset')
MODEL_REGISTRY = Registry('model')
LOSS_REGISTRY = Registry('loss')
METRIC_REGISTRY = Registry('metric') 