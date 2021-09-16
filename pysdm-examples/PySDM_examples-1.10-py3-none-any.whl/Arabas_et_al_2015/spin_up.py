from PySDM.dynamics import Displacement, Coalescence, Freezing


class SpinUp:

    def __init__(self, core, spin_up_steps):
        self.spin_up_steps = spin_up_steps
        core.observers.append(self)
        self.core = core
        self.set(Coalescence, 'enable', False)
        self.set(Displacement, 'enable_sedimentation', False)
        self.set(Freezing, 'enable', False)

    def notify(self):
        if self.core.n_steps == self.spin_up_steps:
            self.set(Coalescence, 'enable', True)
            self.set(Displacement, 'enable_sedimentation', True)
            self.set(Freezing, 'enable', True)

    def set(self, dynamic, attr, value):
        key = dynamic.__name__
        if key in self.core.dynamics:
            setattr(self.core.dynamics[key], attr, value)
