import os
import pickle as pkl

class Config():
    
    def __init__(self, **kwargs):
        for key in kwargs:
            if key=="dict":
                raise KeyError("Key dict is a protected attribute.")
            if key=="keys":
                raise KeyError("Key keys is a protected attribute.")
            setattr(self, key, kwargs[key])
    
    def save(self, path):
        pkl.dump(self.__dict__, open(path, "wb"))
    
    @property
    def default_run_dir(self):
        msg = "log_dir must be set."
        assert self.log_dir is not None, msg

        msg = "name must be set."
        assert self.name is not None, msg

        return os.path.join(self.log_dir, self.name)
    
    @property
    def default_model_path(self):
        return os.path.join(self.default_run_dir, "model.pt")
    
    @property
    def default_config_path(self):
        return os.path.join(self.default_run_dir, "config.pt")
    
    @classmethod
    def load(cls, path):
        return cls(**pkl.load(open(path, "rb")))
    
    @property
    def dict(self):
        return self.__dict__
    
    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        return None
    
    def __getstate__(self): 
        return self.__dict__

    def __setstate__(self, d): 
        self.__dict__.update(d)

    def __repr__(self):
        return self.__str__()
    
    def keys(self):
        return self.__dict__.keys()
    
    def __getitem__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        return None

    def push_as_meta(self, run, prefix=""):
        """Push the config as meta information to run.
        """
        for key, val in self.__dict__.items():
            if isinstance(val, Config):
                val.push_as_meta(run, prefix=prefix+f"{key}/")
            else:
                run.add_meta(f"{prefix}{key}", str(val))
                
    def __str__(self):
        s = "\n"
        for key, val in self.__dict__.items():
            if isinstance(val, Config):
                _s = "\n"+(" "+key+" ").ljust(20, '>').rjust(30, '>')
                _s += str(val)
                _s += ("").ljust(30, '<')+"\n"
                s += _s
            else:
                _s = key.ljust(20, ' ')+ ": "+ str(val)+"\n"
                s += _s
        return s