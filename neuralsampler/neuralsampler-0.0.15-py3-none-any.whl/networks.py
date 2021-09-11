import torch
import torch.nn as nn
from torch.nn import Parameter
from math import pi

# this is the factory method to make a MLP neural network class 
def net_fn(n_dims, n_out=1, n_hid=200, n_depth=2, layer=nn.Linear, UseSpectral=False, use_resnet=False, period=False, sim_mode=True):
    if use_resnet: 
        return resnet(n_dims, n_out=n_out, n_hid=n_hid, n_depth=n_depth, layer=layer, UseSpectral=UseSpectral, period=period)
    else: 
        if sim_mode: 

            # return sim_net(n_dims, n_out=n_out, n_hid=n_hid, n_depth=n_depth, layer=layer, UseSpectral=UseSpectral, period=period)

            return sim_net2(n_dims, n_out=n_out, n_hid=n_hid, n_depth=n_depth, layer=layer, UseSpectral=UseSpectral, period=period)

        else:
            return SmallMLP(n_dims, n_out=n_out, n_hid=n_hid, n_depth=n_depth, layer=layer, UseSpectral=UseSpectral, period=period)

class SmallMLP(nn.Module):
    def __init__(self, n_dims, n_out=1, n_hid=200, n_depth=2, layer=nn.Linear, UseSpectral=False, period=False):
        """Build the neural network for generator and discriminator

        Args:
            n_dims (scalar): the input dimension 
            n_out (int, optional): output dimensions. Defaults to 1.
            n_hid (int, optional): hidden layer dimension. Defaults to 200.
            layer (nn.Module, optional): fully connected layer. Defaults to nn.Linear.
            UseSpectral (bool, optional): whether to use spectral normalization. Defaults to False.
        """
        super(SmallMLP, self).__init__()
        self.period = period
        if period: 
            n_dims += 1
        self.net = nn.Sequential(
            layer(n_dims, n_hid) if not UseSpectral else SpectralNorm(layer(n_dims, n_hid)),
            nn.SiLU(),
            *[(layer(n_hid, n_hid) if not UseSpectral else SpectralNorm(layer(n_hid, n_hid))) if i%2 == 0 else nn.SiLU() for i in range(2*n_depth)],
            # layer(n_hid, n_hid) if not UseSpectral else SpectralNorm(layer(n_hid, n_hid)),
            # nn.SiLU(),
            # layer(n_hid, n_hid) if not UseSpectral else SpectralNorm(layer(n_hid, n_hid)),
            # nn.SiLU(),
            # layer(n_hid, n_hid) if not UseSpectral else SpectralNorm(layer(n_hid, n_hid)),
            # nn.SiLU(),
            layer(n_hid, n_out) if not UseSpectral else SpectralNorm(layer(n_hid, n_out)),
        )

    def forward(self, x):
        if self.period: 
            if x.shape[1] == 2: 
                x = torch.stack([x[:, 0], torch.sin(2 * pi * x[:, 1]), torch.cos(2 * pi * x[:, 1]) ], dim=1)
            else: 
                x12 = torch.stack([x[:, 0], torch.sin(2 * pi * x[:, 1]), torch.cos(2 * pi * x[:, 1]) ], dim=1)
                x = torch.cat([x12, x[:, 2:] ], dim=1)

        out = self.net(x)
        out = out.squeeze()
        return out



class sim_net(nn.Module):
    def __init__(self, n_dims, n_out=1, n_hid=200, n_depth=2, layer=nn.Linear, UseSpectral=False, period=False):
        """Build the neural network for generator and discriminator

        Args:
            n_dims (scalar): the input dimension 
            n_out (int, optional): output dimensions. Defaults to 1.
            n_hid (int, optional): hidden layer dimension. Defaults to 200.
            layer (nn.Module, optional): fully connected layer. Defaults to nn.Linear.
            UseSpectral (bool, optional): whether to use spectral normalization. Defaults to False.
        """
        super(sim_net, self).__init__()
        self.period = period
        if period: 
            n_dims += 1
        n_dims = 1
        self.net = nn.Sequential(
            layer(n_dims, n_hid) if not UseSpectral else SpectralNorm(layer(n_dims, n_hid)),
            nn.GELU(),
            *[(layer(n_hid, n_hid) if not UseSpectral else SpectralNorm(layer(n_hid, n_hid))) if i%2 == 0 else nn.SiLU() for i in range(2*n_depth)],
            # layer(n_hid, n_hid) if not UseSpectral else SpectralNorm(layer(n_hid, n_hid)),
            # nn.SiLU(),
            # layer(n_hid, n_hid) if not UseSpectral else SpectralNorm(layer(n_hid, n_hid)),
            # nn.SiLU(),
            # layer(n_hid, n_hid) if not UseSpectral else SpectralNorm(layer(n_hid, n_hid)),
            # nn.SiLU(),
            layer(n_hid, n_out) if not UseSpectral else SpectralNorm(layer(n_hid, n_out)),
        )

    def forward(self, x):

        x = x.mean(axis=-1, keepdims=True)
        if self.period: 
            if x.shape[1] == 2: 
                x = torch.stack([x[:, 0], torch.sin(2 * pi * x[:, 1]), torch.cos(2 * pi * x[:, 1]) ], dim=1)
            else: 
                x12 = torch.stack([x[:, 0], torch.sin(2 * pi * x[:, 1]), torch.cos(2 * pi * x[:, 1]) ], dim=1)
                x = torch.cat([x12, x[:, 2:] ], dim=1)

        out = self.net(x)
        out = out.squeeze()
        return out




class sim_net2(nn.Module):
    def __init__(self, n_dims, n_out=1, n_hid=200, n_depth=2, layer=nn.Linear, UseSpectral=False, period=False):
        """Build the neural network for generator and discriminator

        Args:
            n_dims (scalar): the input dimension 
            n_out (int, optional): output dimensions. Defaults to 1.
            n_hid (int, optional): hidden layer dimension. Defaults to 200.
            layer (nn.Module, optional): fully connected layer. Defaults to nn.Linear.
            UseSpectral (bool, optional): whether to use spectral normalization. Defaults to False.
        """
        super(sim_net2, self).__init__()
        self.period = period
        if period: 
            n_dims += 1
        #comment out this on Aug 11
        #n_dims += 1
        self.net = nn.Sequential(
            layer(n_dims, n_hid) if not UseSpectral else SpectralNorm(layer(n_dims, n_hid)),
            #nn.GELU(),
            nn.SiLU(),
            *[(layer(n_hid, n_hid) if not UseSpectral else SpectralNorm(layer(n_hid, n_hid))) if i%2 == 0 else nn.SiLU() for i in range(2*n_depth)],
            # layer(n_hid, n_hid) if not UseSpectral else SpectralNorm(layer(n_hid, n_hid)),
            # nn.SiLU(),
            # layer(n_hid, n_hid) if not UseSpectral else SpectralNorm(layer(n_hid, n_hid)),
            # nn.SiLU(),
            # layer(n_hid, n_hid) if not UseSpectral else SpectralNorm(layer(n_hid, n_hid)),
            # nn.SiLU(),
            layer(n_hid, n_out) if not UseSpectral else SpectralNorm(layer(n_hid, n_out)),
        )

    def forward(self, x):

        #comment out this on Aug 11
        # x = torch.cat([x, x.mean(axis=-1, keepdims=True)], axis=-1)

        if self.period: 
            if x.ndim == 2: 
                if x.shape[1] == 2: 
                    x = torch.stack([x[:, 0], torch.sin(2 * pi * x[:, 1]), torch.cos(2 * pi * x[:, 1]) ], dim=1)
                else: 
                    x12 = torch.stack([x[:, 0], torch.sin(2 * pi * x[:, 1]), torch.cos(2 * pi * x[:, 1]) ], dim=1)
                    x = torch.cat([x12, x[:, 2:] ], dim=1)
            elif x.ndim == 3:
                if x.shape[1] == 2: 
                    x = torch.stack([x[:, :, 0], torch.sin(2 * pi * x[:, :, 1]), torch.cos(2 * pi * x[:, :, 1]) ], dim=-1)
                else: 
                    x12 = torch.stack([x[:, :, 0], torch.sin(2 * pi * x[:, :, 1]), torch.cos(2 * pi * x[:, :, 1]) ], dim=-1)
                    x = torch.cat([x12, x[:, :, 2:] ], dim=-1)

        out = self.net(x)
        out = out.squeeze()
        return out


class Affine(nn.Module):
    def __init__(self, dim, fn):
        super().__init__()
        self.g = nn.Parameter(torch.ones(1, dim))
        self.b = nn.Parameter(torch.zeros(1, dim))
        self.fn = fn

    def forward(self, x):
        x = x * self.g + self.b
        return self.fn(x)

class LayerScaleResidual(nn.Module): # https://arxiv.org/abs/2103.17239
    def __init__(self, dim, fn):
        super().__init__()
        init_eps = 0.1
        scale = torch.zeros(1, dim).fill_(init_eps)
        self.scale = nn.Parameter(scale)
        self.fn = fn

    def forward(self, x):
        return self.fn(x) * self.scale + x

class resnet(nn.Module):
    def __init__(self, n_dims, n_out=1, n_hid=200, n_depth=2, layer=nn.Linear, UseSpectral=False, period=False):
        """Build the neural network for generator and discriminator

        Args:
            n_dims (scalar): the input dimension 
            n_out (int, optional): output dimensions. Defaults to 1.
            n_hid (int, optional): hidden layer dimension. Defaults to 200.
            layer (nn.Module, optional): fully connected layer. Defaults to nn.Linear.
            UseSpectral (bool, optional): whether to use spectral normalization. Defaults to False.
        """
        super(resnet, self).__init__()
        expansion_factor = 4
        self.period = period
        if period: 
            n_dims += 1
        wrapper = lambda fn: LayerScaleResidual(n_hid, Affine(n_hid, fn))

        self.actv_fn = nn.SiLU()
        self.layers = nn.ModuleList([
            layer(n_dims, n_hid) if not UseSpectral else SpectralNorm(layer(n_dims, n_hid)),
            *[wrapper(nn.Sequential(
                nn.Linear(n_hid, n_hid * expansion_factor),
                nn.GELU(),
                nn.Linear(n_hid * expansion_factor, n_hid)
            )) if not UseSpectral else SpectralNorm(layer(n_hid, n_hid)) for i in range(n_depth)] ,
            # layer(n_hid, n_hid) if not UseSpectral else SpectralNorm(layer(n_hid, n_hid)),
            # layer(n_hid, n_hid) if not UseSpectral else SpectralNorm(layer(n_hid, n_hid)),
            layer(n_hid, n_out) if not UseSpectral else SpectralNorm(layer(n_hid, n_out)), 
        ])

    def forward(self, x):
        if self.period: 
            if x.shape[1] == 2: 
                x = torch.stack([x[:, 0], torch.sin(2 * pi * x[:, 1]), torch.cos(2 * pi * x[:, 1]) ], dim=1)
            else: 
                x12 = torch.stack([x[:, 0], torch.sin(2 * pi * x[:, 1]), torch.cos(2 * pi * x[:, 1]) ], dim=1)
                x = torch.cat([x12, x[:, 2:] ], dim=1)

        for i, layer in enumerate(self.layers):
            tmp = layer(x)
            if i < len(self.layers) - 1:
                tmp = self.actv_fn(tmp)
            # if layer.in_features == layer.out_features:
            #     x = x + tmp
            # else:
            x = tmp
 
        out = x.squeeze()
        return out

# utils 
def l2normalize(v, eps=1e-12):
    return v / (v.norm() + eps)

class SpectralNorm(nn.Module):
    def __init__(self, module, name='weight', power_iterations=1):
        super(SpectralNorm, self).__init__()
        self.module = module
        self.name = name
        self.power_iterations = power_iterations
        if not self._made_params():
            self._make_params()

    def _update_u_v(self):
        u = getattr(self.module, self.name + "_u")
        v = getattr(self.module, self.name + "_v")
        w = getattr(self.module, self.name + "_bar")

        height = w.data.shape[0]
        for _ in range(self.power_iterations):
            v.data = l2normalize(torch.mv(torch.t(w.view(height,-1).data), u.data))
            u.data = l2normalize(torch.mv(w.view(height,-1).data, v.data))

        # sigma = torch.dot(u.data, torch.mv(w.view(height,-1).data, v.data))
        sigma = u.dot(w.view(height, -1).mv(v))
        setattr(self.module, self.name, w / sigma.expand_as(w))

    def _made_params(self):
        try:
            u = getattr(self.module, self.name + "_u")
            v = getattr(self.module, self.name + "_v")
            w = getattr(self.module, self.name + "_bar")
            return True
        except AttributeError:
            return False


    def _make_params(self):
        w = getattr(self.module, self.name)

        height = w.data.shape[0]
        width = w.view(height, -1).data.shape[1]

        u = Parameter(w.data.new(height).normal_(0, 1), requires_grad=False)
        v = Parameter(w.data.new(width).normal_(0, 1), requires_grad=False)
        u.data = l2normalize(u.data)
        v.data = l2normalize(v.data)
        w_bar = Parameter(w.data)

        del self.module._parameters[self.name]

        self.module.register_parameter(self.name + "_u", u)
        self.module.register_parameter(self.name + "_v", v)
        self.module.register_parameter(self.name + "_bar", w_bar)


    def forward(self, *args):
        self._update_u_v()
        return self.module.forward(*args)
