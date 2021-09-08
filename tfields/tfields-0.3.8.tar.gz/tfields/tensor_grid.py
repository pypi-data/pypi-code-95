"""
Implementaiton of TensorGrid class
"""
import numpy as np
from .lib import grid, util
from .core import Tensors, TensorFields


class TensorGrid(TensorFields):
    """
    A Tensor Grid is a TensorField which is aware of it's grid nature, which is order of iteration
    (iter-order) over the base vectors (base_vectors).

    Args:
        *base_vectors (tuple): indices of the axes which should be iterated
        **kwargs:
            num (np.array): same as np.linspace 'num'
            iter_order (np.array): index order of building the grid.
            further: see TensorFields class
    """

    __slots__ = ["coord_sys", "name", "fields", "base_vectors", "num", "iter_order"]
    __slot_setters__ = TensorFields.__slot_setters__ + [
        None,
        None,
        None,
    ]

    def __new__(cls, tensors, *fields, **kwargs):
        if isinstance(tensors, TensorGrid):
            default_base_vectors = tensors.base_vectors
            default_num = tensors.num
            default_iter_order = tensors.iter_order
        else:
            default_base_vectors = kwargs.pop("base_vectors", None)
            default_num = None
            default_iter_order = None
        base_vectors = kwargs.pop("base_vectors", default_base_vectors)
        num = kwargs.pop("num", default_num)
        iter_order = kwargs.pop("iter_order", default_iter_order)

        obj = super(TensorGrid, cls).__new__(cls, tensors, *fields, **kwargs)

        if len(base_vectors) == 3:
            base_vectors = tuple(tuple(bv) for bv in base_vectors)
            base_vectors = grid.ensure_complex(*base_vectors)
        if (
            isinstance(base_vectors, (tuple, list))
            and base_vectors
            and len(base_vectors[0]) == 3
        ):
            if num is None:
                num = np.array([int(bv[2].imag) for bv in base_vectors], dtype=int)
            base_vectors = np.transpose([[bv[0], bv[1]] for bv in base_vectors])

        # base_vectors
        base_vectors = Tensors(base_vectors, coord_sys=obj.coord_sys)
        if len(base_vectors) != 2:
            raise ValueError(
                f"base_vectors must be of lenght 2. Lenght is {len(base_vectors)}."
            )
        obj.base_vectors = base_vectors

        # num
        if num is None:
            num = np.array([1 for _ in range(base_vectors.dim)])
        else:
            num = np.array(num, dtype=int)
        obj.num = num

        # iter_order
        if iter_order is None:
            iter_order = np.arange(base_vectors.dim)
        else:
            iter_order = np.array(iter_order, dtype=int)
        obj.iter_order = iter_order

        if isinstance(tensors, TensorGrid):
            if (obj.num != tensors.num).all() or (
                obj.is_empty() and not obj.base_vectors.equal(tensors.base_vectors)
            ):
                # copy constructor with shape change
                return obj.empty(*obj.base_num_tuples(), iter_order=iter_order)
            if (obj.iter_order != tensors.iter_order).all():
                # iter_order was changed in copy constructor
                obj.iter_order = (
                    tensors.iter_order
                )  # set to 'default_iter_order' and change later
                obj.change_iter_order(iter_order)
        return obj

    def __getitem__(self, index):
        if not self.is_empty():
            return super().__getitem__(index)
        item = self.explicit()
        if not util.is_full_slice(index, item.shape):
            # downgrade to TensorFields
            item = TensorFields(item)
        return item.__getitem__(index)

    @classmethod
    # pylint:disable=arguments-differ
    def grid(cls, *base_vectors, tensors=None, fields=None, **kwargs):
        """
        Build the grid (explicitly) from base vectors

        Args:
            explicit args: see __new__
            **kwargs: see TensorFields
        """
        iter_order = kwargs.pop("iter_order", np.arange(len(base_vectors)))
        if tensors is None:
            tensors = TensorFields.grid(*base_vectors, iter_order=iter_order, **kwargs)
        obj = cls(tensors, base_vectors=base_vectors, iter_order=iter_order, **kwargs)
        if fields:
            # pylint:disable=attribute-defined-outside-init
            obj.fields = fields
        return obj

    @classmethod
    def empty(cls, *base_vectors, **kwargs):
        """
        Build the grid (implicitly) from base vectors
        """
        base_vectors = grid.ensure_complex(*base_vectors)
        bv_lengths = [int(bv[2].imag) for bv in base_vectors]
        tensors = np.empty(shape=(np.prod(bv_lengths), 0))

        return cls.grid(*base_vectors, tensors=tensors, **kwargs)

    @classmethod
    def merged(cls, *objects, **kwargs):
        if "base_vectors" not in kwargs:
            base_vectors = None
            for obj in objects:
                if base_vectors is None:
                    base_vectors = obj.base_vectors
                else:
                    if not all(
                        ((a == b).all() for a, b in zip(base_vectors, obj.base_vectors))
                    ):
                        raise NotImplementedError("Non-alligned base vectors")
            kwargs.setdefault("base_vectors", base_vectors)
        merge = super().merged(*objects, **kwargs)
        return merge

    def base_num_tuples(self):
        """
        Returns the grid style base_vectors + num tuples
        """
        return tuple(
            (bv[0], bv[1], complex(0, n))
            for bv, n in zip(self.base_vectors.T, self.num)
        )

    @property
    def rank(self):
        if self.is_empty():
            return 1
        return super().rank

    def is_empty(self):
        """
        Check if the object is an implicit grid (base points are empty but base_vectors and iter
        order can be used to build the explicit grid's base points).
        """
        return 0 in self.shape

    def explicit(self):
        """
        Build the grid explicitly (e.g. after changing base_vector, iter_order or init with empty)
        """
        kwargs = {
            attr: getattr(self, attr)
            for attr in self.__slots__
            if attr not in ("base_vectors", "num", "coord_sys")
        }
        base_num_tuples = self.base_num_tuples()
        kwargs["coord_sys"] = self.base_vectors.coord_sys
        obj = self.grid(*base_num_tuples, **kwargs)
        obj.transform(self.coord_sys)
        return obj

    def change_iter_order(self, iter_order):
        """
        Transform the iter order
        """
        field_swap_indices = grid.change_iter_order(
            # pylint:disable=access-member-before-definition
            self.num,
            self.iter_order,
            iter_order,
        )
        for field in self.fields:
            field[:] = field[field_swap_indices]
        # pylint:disable=attribute-defined-outside-init
        self.iter_order = iter_order
        self[:] = self.explicit()
