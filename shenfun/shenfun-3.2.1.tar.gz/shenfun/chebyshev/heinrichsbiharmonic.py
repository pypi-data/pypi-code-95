#class HeinrichsBiharmonic(CompositeSpace):
#    """Function space for biharmonic equation
#
#    Using 2 Dirichlet and 2 Neumann boundary conditions. All possibly
#    nonhomogeneous.
#
#    Parameters
#    ----------
#        N : int, optional
#            Number of quadrature points
#        quad : str, optional
#            Type of quadrature
#
#            - GL - Chebyshev-Gauss-Lobatto
#            - GC - Chebyshev-Gauss
#        bc : 4-tuple of numbers
#            The values of the 4 boundary conditions at x=(-1, 1).
#            The two Dirichlet at (-1, 1) first and then the Neumann at (-1, 1).
#        domain : 2-tuple of floats, optional
#            The computational domain
#        dtype : data-type, optional
#            Type of input data in real physical space. Will be overloaded when
#            basis is part of a :class:`.TensorProductSpace`.
#        padding_factor : float, optional
#            Factor for padding backward transforms.
#        dealias_direct : bool, optional
#            Set upper 1/3 of coefficients to zero before backward transform
#        coordinates: 2- or 3-tuple (coordinate, position vector (, sympy assumptions)), optional
#            Map for curvilinear coordinatesystem.
#            The new coordinate variable in the new coordinate system is the first item.
#            Second item is a tuple for the Cartesian position vector as function of the
#            new variable in the first tuple. Example::
#
#                theta = sp.Symbols('x', real=True, positive=True)
#                rv = (sp.cos(theta), sp.sin(theta))
#
#    """
#    def __init__(self, N, quad="GC", bc=(0, 0, 0, 0), domain=(-1., 1.), dtype=float,
#                 padding_factor=1, dealias_direct=False, coordinates=None):
#        CompositeSpace.__init__(self, N, quad=quad, domain=domain, dtype=dtype,
#                                padding_factor=padding_factor, dealias_direct=dealias_direct,
#                                coordinates=coordinates)
#        from shenfun.tensorproductspace import BoundaryValues
#        self._bc_basis = None
#        self.bc = BoundaryValues(self, bc=bc)
#
#    @staticmethod
#    def boundary_condition():
#        return 'Biharmonic'
#
#    @staticmethod
#    def short_name():
#        return 'HB'
#
#    @property
#    def has_nonhomogeneous_bcs(self):
#        return self.bc.has_nonhomogeneous_bcs()
#
#    def _composite(self, V, argument=0):
#        P = np.zeros_like(V)
#        P[:, 4:-4] = (V[:, :-8]-2*V[:, 2:-6]+6*V[:, 4:-4]-4*V[:, 6:-2]+V[:, 8:])/16
#        P[:, 3] = (-7*V[:, 1]+6*V[:, 3]-4*V[:, 5]+V[:, 7])/16
#        P[:, 2] = (-4*V[:, 0]+7*V[:, 2]-4*V[:, 4]+V[:, 6])/16
#        P[:, 1] = (2*V[:, 1]-3*V[:, 3]+V[:, 5])/16
#        P[:, 0] = (6*V[:, 0]-8*V[:, 2]+2*V[:, 4])/16
#        if argument == 1: # if trial function
#            P[:, -4:] = np.tensordot(V[:, :4], BCBiharmonic.stencil_matrix(), (1, 1))
#        return P
#
#    def sympy_basis(self, i=0, x=xp):
#        if i < self.N-4:
#            f = (1-x**2)**2*sp.chebyshevt(i, x)
#        else:
#            f = BCBiharmonic.stencil_matrix()[i]*np.array([sp.chebyshevt(j, x) for j in range(4)])
#        return f
#
#    def evaluate_basis(self, x, i=0, output_array=None):
#        x = np.atleast_1d(x)
#        if output_array is None:
#            output_array = np.zeros(x.shape)
#        w = np.arccos(x)
#        output_array[:] = (1-x**2)**2*np.cos(i*w)
#        return output_array
#
#    def evaluate_basis_derivative(self, x=None, i=0, k=0, output_array=None):
#        if x is None:
#            x = self.mesh(False, False)
#        if output_array is None:
#            output_array = np.zeros(x.shape)
#        x = np.atleast_1d(x)
#        basis = self.sympy_basis(i)
#        xp = basis.free_symbols.pop()
#        output_array[:] = sp.lambdify(xp, basis.diff(xp, k))(x)
#        return output_array
#
#    def _evaluate_scalar_product(self, fast_transform=True):
#        if fast_transform is False:
#            SpectralBase._evaluate_scalar_product(self)
#            self.scalar_product.output_array[self.sl[slice(-4, None)]] = 0
#            return
#        Orthogonal._evaluate_scalar_product(self, True)
#        output = self.scalar_product.output_array
#        wk = output.copy()
#
#        output[self.si[0]] = (6*wk[self.si[0]]-8*wk[self.si[2]]+2*wk[self.si[4]])/16
#        output[self.si[1]] = (2*wk[self.si[1]]-3*wk[self.si[3]]+wk[self.si[5]])/16
#        output[self.si[2]] = (-4*wk[self.si[0]]+7*wk[self.si[2]]-4*wk[self.si[4]]+wk[self.si[6]])/16
#        output[self.si[3]] = (-7*wk[self.si[1]]+6*wk[self.si[3]]-4*wk[self.si[5]]+wk[self.si[7]])/16
#
#        output[self.sl[slice(4, self.N-4)]] *= 3/8
#        output[self.sl[slice(4, self.N-4)]] -= wk[self.sl[slice(2, self.N-6)]]/8
#        output[self.sl[slice(4, self.N-4)]] += wk[self.sl[slice(0, self.N-8)]]/16
#        output[self.sl[slice(4, self.N-4)]] -= wk[self.sl[slice(6, self.N-2)]]/4
#        output[self.sl[slice(4, self.N-4)]] += wk[self.sl[slice(8, self.N)]]/16
#        output[self.sl[slice(-4, None)]] = 0
#
#    def to_ortho(self, input_array, output_array=None):
#        if output_array is None:
#            output_array = np.zeros_like(input_array)
#        else:
#            output_array.fill(0)
#        output_array[self.si[0]] = 3/8*input_array[self.si[0]]-1/4*input_array[self.si[2]]
#        output_array[self.si[1]] = 1/8*input_array[self.si[1]]-7/16*input_array[self.si[3]]
#        output_array[self.si[2]] = -1/2*input_array[self.si[0]]+7/16*input_array[self.si[2]]
#        output_array[self.si[3]] = -3/16*input_array[self.si[1]]-7/16*input_array[self.si[3]]
#        output_array[self.si[4]] = 1/8*input_array[self.si[0]]-1/4*input_array[self.si[2]]
#        output_array[self.si[5]] = 1/16*input_array[self.si[1]]-1/4*input_array[self.si[3]]
#        output_array[self.si[6]] = 1/16*input_array[self.si[2]]
#        output_array[self.si[7]] = 1/16*input_array[self.si[3]]
#        s0 = self.sl[slice(0, self.N-8)]
#        s1 = self.sl[slice(2, self.N-6)]
#        s2 = self.sl[slice(4, self.N-4)]
#        s3 = self.sl[slice(6, self.N-2)]
#        s4 = self.sl[slice(8, self.N)]
#        output_array[s0] += input_array[s2]/16
#        output_array[s1] -= input_array[s2]/8
#        output_array[s2] += input_array[s2]*(3/8)
#        output_array[s3] -= input_array[s2]/4
#        output_array[s4] += input_array[s2]/16
#        self.bc.add_to_orthogonal(output_array, input_array)
#        return output_array
#
#    def slice(self):
#        return slice(0, self.N-4)
#
#    def eval(self, x, u, output_array=None):
#        x = np.atleast_1d(x)
#        if output_array is None:
#            output_array = np.zeros(x.shape, dtype=self.dtype)
#        x = self.map_reference_domain(x)
#        w = self.to_ortho(u)
#        output_array[:] = chebval(x, w)
#        return output_array
#
#    def get_bc_basis(self):
#        if self._bc_basis:
#            return self._bc_basis
#        self._bc_basis = BCBiharmonic(self.N, quad=self.quad, domain=self.domain,
#                                      coordinates=self.coors.coordinates)
#        return self._bc_basis
#
#    def get_refined(self, N):
#        return HeinrichsBiharmonic(N,
#                                   quad=self.quad,
#                                   domain=self.domain,
#                                   dtype=self.dtype,
#                                   padding_factor=self.padding_factor,
#                                   dealias_direct=self.dealias_direct,
#                                   coordinates=self.coors.coordinates,
#                                   bc=self.bc.bc)
#
#    def get_dealiased(self, padding_factor=1.5, dealias_direct=False):
#        return HeinrichsBiharmonic(self.N,
#                                   quad=self.quad,
#                                   domain=self.domain,
#                                   dtype=self.dtype,
#                                   padding_factor=padding_factor,
#                                   dealias_direct=dealias_direct,
#                                   coordinates=self.coors.coordinates,
#                                   bc=self.bc.bc)
#
#    def get_unplanned(self):
#        return HeinrichsBiharmonic(self.N,
#                                   quad=self.quad,
#                                   domain=self.domain,
#                                   dtype=self.dtype,
#                                   padding_factor=self.padding_factor,
#                                   dealias_direct=self.dealias_direct,
#                                   coordinates=self.coors.coordinates,
#                                   bc=self.bc.bc)
