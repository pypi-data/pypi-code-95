"""
Experiment Management
"""
from datetime import datetime
from os import pardir
from attrdict import AttrDict
import pathlib
import hashlib
import os
from rl_helper import envhelper
import yaml


class ExperimentManager(object):
    def __init__(self,add_env_helper=True) -> None:
        super().__init__()

        self.saves_root=pathlib.Path("./runs/")        
        self.exp_time=datetime.now().strftime("%Y%m%d-%H%M%S")
        self.env_helper=envhelper()

    def init(self,model_name,exp_class,exp_target,comments,sub_id):

        assert len(exp_target)<24, "exp target to long > 20"
        assert " " not in exp_target, "exp target should contain no space"

        self.model_name=model_name
        self.exp_class=exp_class
        self.exp_target=exp_target
        self.comments=comments
        self.sub_id=sub_id

        self.config={"model_name":self.model_name,"exp_class":self.exp_class,"exp_target":self.exp_target, "comments":self.comments,"sub_id":sub_id}
        self.paras=AttrDict()

    @property
    def health(self):
        a=[self.model_name,self.exp_class,self.exp_target, self.comments,self.sub_id 
        , self.sub_id ,  self.config , self.paras ]
        for s in a:
            assert a is not None
        return True

    def load(self,pth):
    
        pth=pathlib.Path(pth)
        assert pth.is_dir(),pth
        config_yaml=pth.joinpath("config.yaml")
        paras_yaml=pth.joinpath('paras.yaml')
        assert config_yaml.is_file()
        assert paras_yaml.is_file()

        with open(config_yaml, "r") as stream:
            self.config=yaml.safe_load(stream)
        with open(paras_yaml, "r") as stream:
            self.paras=AttrDict(yaml.safe_load(stream))

        for k in self.config.keys():
            self.__setattr__(k,self.config[k])

        assert self.health

    def get_exp_hash(self):
        hash_seed=self.model_name+self.exp_class+self.exp_target+self.comments+str(self.sub_id)
        pkeys=[]
        for k in self.paras.keys():
            pkeys.append(k)
        pkeys.sort()
        pkeys_value=[self.paras[k] for k in pkeys]
        hash_seed+=str(pkeys)
        hash_seed+=str(pkeys_value)
        return hashlib.sha1(hash_seed.encode('utf-8')).hexdigest()[:5]


    @property
    def exp_hash_dir_path(self):
        return self.saves_root.joinpath(self.exp_class).joinpath(self.exp_target).joinpath(str(self.sub_id)).joinpath(self.get_exp_hash())

    # @property
    # def model_save_dir_path(self):
    #     dir_pth=
    #     pass

    @property
    def model_save_pth(self):
        return self.exp_hash_dir_path.joinpath("model")

    @property
    def log_save_dir_pth(self):
        return self.exp_hash_dir_path.joinpath("logs")
        pass

    @property
    def paras_save_dir_pth(self):
        return self.exp_hash_dir_path.joinpath("paras")

    @property
    def tensorbord_log_name(self):
        return str(self.sub_id)
    
    @property
    def paras_dict(self):
        d={}
        for k in self.paras.keys():
            d[k]=self.paras[k]
        return d

    def add_para(self,k,value):
        assert self.paras.get(k,None) is None, "{} has existed in paras".format(k)
        self.paras[k]=value
        print("Set {} : {}".format(k,value))

    def start(self,overwrite=False):
        try:
            os.makedirs(self.exp_hash_dir_path.__str__(),exist_ok=False)
        except:
            if not overwrite:
                raise NotImplementedError("Error ! Fail to create, You already have this experiment : {}".format(self.exp_hash_dir_path))

        os.makedirs(self.paras_save_dir_pth,exist_ok=True)

        with open(self.exp_hash_dir_path.joinpath("paras.yaml"), 'w') as outfile:
            yaml.dump(self.paras_dict, outfile, default_flow_style=False)
        with open(self.exp_hash_dir_path.joinpath("config.yaml"), 'w') as outfile:
            yaml.dump(self.config, outfile, default_flow_style=False)
        for k in self.paras.keys():
            ss="{}_{}".format(k,str(self.paras[k]))
            with open(self.paras_save_dir_pth.joinpath(ss), 'w') as outfile:
                pass
        with open(self.exp_hash_dir_path.joinpath(""+str(self.exp_time)), 'w') as outfile:
            pass

    def save_gif(self,**kargs):
        self.env_helper.save_gif(path=self.log_save_dir_pth,**kargs)