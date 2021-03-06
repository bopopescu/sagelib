r"""
Kirillov-Reshetikhin Crystals
"""

#*****************************************************************************
#       Copyright (C) 2009   Anne Schilling <anne at math.ucdavis.edu>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    General Public License for more details.
#
#  The full text of the GPL is available at:
#
#                  http://www.gnu.org/licenses/
#****************************************************************************
# Acknowledgment: most of the design and implementation of this
# library is heavily inspired from MuPAD-Combinat.
#****************************************************************************

from sage.misc.cachefunc import cached_method
from sage.combinat.combinat import CombinatorialObject
from sage.structure.parent import Parent
from sage.categories.finite_crystals import FiniteCrystals
from sage.rings.integer import Integer
from sage.rings.all import QQ
from sage.functions.other import floor
from sage.misc.functional import is_even, is_odd
from sage.combinat.crystals.affine import AffineCrystalFromClassical, AffineCrystalFromClassicalElement
from sage.combinat.crystals.affine import AffineCrystalFromClassicalAndPromotion
from sage.combinat.crystals.highest_weight_crystals import HighestWeightCrystal
from sage.combinat.crystals.direct_sum import DirectSumOfCrystals
from sage.combinat.root_system.cartan_type import CartanType
from sage.combinat.crystals.tensor_product import CrystalOfTableaux, TensorProductOfCrystals
from sage.combinat.tableau import Tableau
from sage.combinat.partition import Partition, Partitions
from sage.combinat.integer_vector import IntegerVectors
from sage.functions.other import floor, ceil


def KirillovReshetikhinCrystal(cartan_type, r, s):
    r"""
    Returns the Kirillov-Reshetikhin crystal `B^{r,s}` of the given type.

    For more information about general crystals see :mod:`sage.combinat.crystals`.

    Many Kirillov-Reshetikhin crystals are constructed from a 
    classical crystal together with an automorphism `p` on the level of crystals which
    corresponds to a Dynkin diagram automorphism mapping node 0 to some other node i.
    The action of `f_0` and `e_0` is then constructed using
    `f_0 = p^{-1} \circ f_i \circ p`.

    For example, for type `A_n^{(1)}` the Kirillov-Reshetikhin crystal `B^{r,s}`
    is obtained from the classical crystal `B(s\omega_r)` using the
    promotion operator. For other types, see

    [1] M. Shimozono
    "Affine type A crystal structure on tensor products of rectangles, 
    Demazure characters, and nilpotent varieties",
    J. Algebraic Combin.  15  (2002),  no. 2, 151-187
    (arXiv:math.QA/9804039)

    [2] A. Schilling, "Combinatorial structure of Kirillov-Reshetikhin crystals of 
    type `D_n(1)`, `B_n(1)`, `A_{2n-1}(2)`", J. Algebra 319 (2008) 2938-2962 
    (arXiv:0704.2046 [math.QA])

    [3] B. Jones, A. Schilling,
    ""Affine structures and a tableau model for `E_6` crystals",
    preprint arXiv:0909.2442 [math.CO]

    Other Kirillov-Reshetikhin crystals are constructed using similarity methods.
    See Section 4 of

    [4] G. Fourier, M. Okado, A. Schilling,
    "Kirillov-Reshetikhin crystals for nonexceptional types",
    Advances in Mathematics  222 Issue 3 (2009) 1080-1116 
    (arXiv:0810.5067 [math.RT])

    INPUT:

        - ``cartan_type`` Affine type and rank

        - ``r`` Label of finite Dynkin diagram

        - ``s`` Positive integer

    EXAMPLES::
    
        sage: K = KirillovReshetikhinCrystal(['A',3,1], 2, 1)
        sage: K.index_set()
        [0, 1, 2, 3]
        sage: K.list()
        [[[1], [2]], [[1], [3]], [[2], [3]], [[1], [4]], [[2], [4]], [[3], [4]]]
        sage: b=K(rows=[[1],[2]])
        sage: b.weight()
        -Lambda[0] + Lambda[2]

        sage: K = KirillovReshetikhinCrystal(['A',3,1], 2,2)
        sage: K.automorphism(K.module_generators[0])
        [[2, 2], [3, 3]]
        sage: K.module_generators[0].e(0)
        [[1, 2], [2, 4]]
        sage: K.module_generators[0].f(2)
        [[1, 1], [2, 3]]
        sage: K.module_generators[0].f(1)
        sage: K.module_generators[0].phi(0)
        0
        sage: K.module_generators[0].phi(1)
        0
        sage: K.module_generators[0].phi(2)
        2
        sage: K.module_generators[0].epsilon(0)
        2
        sage: K.module_generators[0].epsilon(1)
        0
        sage: K.module_generators[0].epsilon(2)
        0
        sage: b = K(rows=[[1,2],[2,3]])
        sage: b
        [[1, 2], [2, 3]]
        sage: b.f(2)
        [[1, 2], [3, 3]]

        sage: K = KirillovReshetikhinCrystal(['D',4,1], 2, 1)
        sage: K.cartan_type()
        ['D', 4, 1]
        sage: type(K.module_generators[0])
        <class 'sage.combinat.crystals.affine.KR_type_vertical_with_category.element_class'>


    The following gives some tests with regards to Lemma 3.11 in
    
    [5] C. Lecouvey, M. Okado, M. Shimozono,
    "Affine crystals, one-dimensional sums and parabolic Lusztig `q`-analogues'
    preprint arXiv:1002.3715

    TESTS::

        sage: K = KirillovReshetikhinCrystal(['A',4,2],2,1)
        sage: Lambda = K.weight_lattice_realization().fundamental_weights()
        sage: [b for b in K if b.Epsilon() == Lambda[0]]
        [[]]

        sage: K = KirillovReshetikhinCrystal(['D',4,2],1,2)
        sage: Lambda = K.weight_lattice_realization().fundamental_weights()
        sage: [b for b in K if b.Epsilon() == 2*Lambda[0]]
        [[]]
        sage: [b for b in K if b.Epsilon() == 2*Lambda[3]]
        [[[3, -3]]]
        sage: K = KirillovReshetikhinCrystal(['D',4,2],1,1)
        sage: [b for b in K if b.Epsilon() == Lambda[3]]
        [[[0]]]

        sage: K = KirillovReshetikhinCrystal(['B',3,1],2,1)
        sage: Lambda = K.weight_lattice_realization().fundamental_weights()
        sage: [b for b in K if b.Epsilon() == Lambda[0]]
        [[]]
        sage: [b for b in K if b.Epsilon() == Lambda[1]]
        [[[2], [-2]]]
        sage: K = KirillovReshetikhinCrystal(['B',3,1],2,2)
        sage: [b for b in K if b.Epsilon() == 2*Lambda[0]]
        [[]]
        sage: [b for b in K if b.Epsilon() == 2*Lambda[1]]
        [[[1, 2], [-2, -1]]]
        sage: K = KirillovReshetikhinCrystal(['B',3,1],2,3)
        sage: [b for b in K if b.Epsilon() == 3*Lambda[1]] # long time
        [[[1, 2, 2], [-2, -2, -1]]]

        sage: K = KirillovReshetikhinCrystal(['D',4,1],2,2)
        sage: Lambda = K.weight_lattice_realization().fundamental_weights()
        sage: [b for b in K if b.Epsilon() == 2*Lambda[0]] # long time
        [[]]
        sage: [b for b in K if b.Epsilon() == 2*Lambda[4]] # long time
        [[[3, -4], [4, -3]]]

        sage: K = KirillovReshetikhinCrystal(['B',3,1],3,1)
        sage: Lambda = K.weight_lattice_realization().fundamental_weights()
        sage: [b for b in K if b.Epsilon() == Lambda[0]]
        [[+++, []]]
        sage: [b for b in K if b.Epsilon() == Lambda[1]]
        [[-++, []]]
        sage: K = KirillovReshetikhinCrystal(['B',3,1],3,3)
        sage: [b for b in K if b.Epsilon() == 2*Lambda[0]] # long time
        [[+++, [[1]]]]
        sage: [b for b in K if b.Epsilon() == 2*Lambda[1]] # long time
        [[-++, [[-1]]]]

        sage: K = KirillovReshetikhinCrystal(['B',4,1],4,1)
        sage: Lambda = K.weight_lattice_realization().fundamental_weights()
        sage: [b for b in K if b.Epsilon() == Lambda[0]]
        [[++++, []]]
        sage: [b for b in K if b.Epsilon() == Lambda[1]]
        [[-+++, []]]

        sage: K = KirillovReshetikhinCrystal(['C',3,1],1,1)
        sage: Lambda = K.weight_lattice_realization().fundamental_weights()
        sage: [b for b in K if b.Epsilon() == Lambda[0]]
        [[[1]]]
        sage: [b for b in K if b.Epsilon() == Lambda[3]]
        [[[-3]]]
        sage: K = KirillovReshetikhinCrystal(['C',3,1],1,3)
        sage: [b for b in K if b.Epsilon() == 2*Lambda[3]] # long time
        [[[3, -3, -3]]]
        sage: [b for b in K if b.Epsilon() == 2*Lambda[0]] # long time
        [[[1]]]
    """
    ct = CartanType(cartan_type)
    assert ct.is_affine()
    if ct.is_untwisted_affine():
        if ct.type() == 'A':
            return KR_type_A(ct, r, s)
        elif ct.type() == 'D' and r<ct.rank()-2:
            return KR_type_vertical(ct, r, s)
        elif ct.type() == 'B':
            if r<ct.rank()-1:
                return KR_type_vertical(ct, r, s)
            elif r == ct.rank()-1:
                return KR_type_Bn(ct, r, s)
            else:
                raise ValueError("wrong range of parameters")
        elif ct.type() == 'C':
            if r<ct.rank()-1:
                return KR_type_C(ct, r, s)
            elif r == ct.rank()-1:
                return KR_type_Cn(ct, r, s)
            else:
                raise ValueError("wrong range of parameters")
        elif ct == CartanType(['E',6,1]) and r in [1,6,2]:
            return KR_type_E6(ct, r, s)
        else:
            raise NotImplementedError
    else:
        if ct.dual().type() == 'B':
            return KR_type_vertical(ct, r, s)
        elif ct.type() == 'BC':
            return KR_type_box(ct, r, s)
        elif ct.dual().type() == 'BC':
            return KR_type_A2(ct, r, s)
        elif ct.dual().type() == 'C':
            if r<ct.rank()-1:
                return KR_type_box(ct, r, s)
            elif r == ct.rank()-1:
                return KR_type_Dn_twisted(ct, r, s)
            else:
                raise ValueError("wrong range of parameters")
        else:
            raise NotImplementedError


class KirillovReshetikhinGenericCrystal(Parent):
    r"""
    Generic class for Kirillov-Reshetikhin crystal `B^{r,s}` of the given type.

    Input is a Dynkin node `r`, a positive integer `s`, and a Cartan type `cartan_type`.
    """

    def __init__(self, cartan_type, r, s, dual = None):
        r"""
        Initializes a generic Kirillov-Reshetikhin crystal.
        
        TESTS::
            
            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KirillovReshetikhinGenericCrystal(CartanType(['A',2,1]), 1, 1)
            sage: K
            Kirillov-Reshetikhin crystal of type ['A', 2, 1] with (r,s)=(1,1)
            sage: K.r()
            1
            sage: K.s()
            1
        """
        Parent.__init__(self, category = FiniteCrystals())
        if dual is None:
            self._cartan_type = cartan_type
        else:
            self._cartan_type = CartanType(cartan_type).dual()
        self._r = r
        self._s = s
        self._dual = dual

    def _repr_(self):
        """
        EXAMPLES::

            sage: sage.combinat.crystals.kirillov_reshetikhin.KirillovReshetikhinGenericCrystal(CartanType(['A',2,1]), 1, 1) # indirect doctest
            Kirillov-Reshetikhin crystal of type ['A', 2, 1] with (r,s)=(1,1)
        """
        return "Kirillov-Reshetikhin crystal of type %s with (r,s)=(%d,%d)" % (self.cartan_type(), self.r(), self.s())

    def module_generator(self):
        r"""
        Yields the module generator of weight `s \Lambda_r` of a Kirillov-Reshetikhin crystal `B^{r,s}`

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['C',2,1],1,2)
            sage: K.module_generator()
            [[1, 1]]
            sage: K = KirillovReshetikhinCrystal(['E',6,1],1,1)
            sage: K.module_generator()
            [[1]]
            
            sage: K = KirillovReshetikhinCrystal(['D',4,1],2,1)
            sage: K.module_generator()
            [[1], [2]]
        """
        R = self.weight_lattice_realization()
        Lambda = R.fundamental_weights() 
        r = self.r()
        s = self.s()
        c = R.null_coroot()[r]
        return [ b for b in self.module_generators if b.weight() == s*Lambda[r] - s*c*Lambda[0] ][0]

    def r(self):
        """
        Returns r of the underlying Kirillov-Reshetikhin crystal `B^{r,s}`

        EXAMPLES::
        
            sage: K = KirillovReshetikhinCrystal(['D',4,1], 2, 1)
            sage: K.r()
            2
        """
        return self._r
    
    def s(self):
        """
        Returns s of the underlying Kirillov-Reshetikhin crystal `B^{r,s}`
        
        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['D',4,1], 2, 1)
            sage: K.s()
            1
        """
        return self._s

    def is_perfect(self):
        r"""
        Returns True or False depending on whether ``self`` is a perfect crystal or not, respectively.

        If ``self`` is the Kirillov-Reshetikhin crystal `B^{r,s}`, then it was proven in [FOS2010]_
        that it is perfect if and only if `s/c_r` is an integer (where `c_r` is a constant related to the
        type of the crystal).

        REFERENCES:

            .. [FOS2010] G. Fourier, M. Okado, A. Schilling.
               Perfectness of Kirillov-Reshetikhin crystals for nonexceptional types
               Contemp. Math. 506 (2010) 127-143 ( arXiv:0811.1604 [math.RT] ) 

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['A',2,1], 1, 1)
            sage: K.is_perfect()
            True

            sage: K = KirillovReshetikhinCrystal(['C',2,1], 1, 1)
            sage: K.is_perfect()
            False

            sage: K = KirillovReshetikhinCrystal(['C',2,1], 1, 2)
            sage: K.is_perfect()
            True
        """
        x = self.s()/self.cartan_type().c()[self.r()]
        return x - ceil(x) == 0

    def level(self):
        r"""
        Returns the level of ``self`` assuming that it is a perfect crystal.

        If ``self`` is the Kirillov-Reshetikhin crystal `B^{r,s}`, then it was proven in [FOS2010]_
        that its level is `s/c_r` which is an integer if ``self`` is perfect
        (here `c_r` is a constant related to the type of the crystal).

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['A',2,1], 1, 1)
            sage: K.level()
            1
            sage: K = KirillovReshetikhinCrystal(['C',2,1], 1, 2)
            sage: K.level()
            1
            sage: K = KirillovReshetikhinCrystal(['D',4,1], 1, 3)
            sage: K.level()
            3

            sage: K = KirillovReshetikhinCrystal(['C',2,1], 1, 1)
            sage: K.level()                    
            Traceback (most recent call last):
            ...
            AssertionError: This crystal is not perfect!
        """
        assert self.is_perfect(), "This crystal is not perfect!"
        return self.s()/self.cartan_type().c()[self.r()]

    def R_matrix(self, K):
        r"""
        INPUT:
        
        - ``self`` -- a crystal `L`
        - ``K`` -- a Kirillov-Reshetikhin crystal of the same type as `L`.
        
        Returns the *combinatorial `R`-matrix* from `L \otimes K \to K
        \otimes L`, where the combinatorial `R`-matrix is the affine
        crystal isomorphism which maps `u_{L} \otimes u_K` to `u_K
        \otimes u_{L}`, where `u_K` is the unique element in `K =
        B^{r,s}` of weight `s\Lambda_r - s c \Lambda_0` (see
        module_generator).
        
        EXAMPLES::
        
            sage: K = KirillovReshetikhinCrystal(['A',2,1],1,1)
            sage: L = KirillovReshetikhinCrystal(['A',2,1],1,2)
            sage: f = K.R_matrix(L)
            sage: [[b,f(b)] for b in TensorProductOfCrystals(K,L)]
            [[[[[1]], [[1, 1]]], [[[1, 1]], [[1]]]],
            [[[[1]], [[1, 2]]], [[[1, 1]], [[2]]]],
            [[[[1]], [[2, 2]]], [[[1, 2]], [[2]]]],
            [[[[1]], [[1, 3]]], [[[1, 1]], [[3]]]],
            [[[[1]], [[2, 3]]], [[[1, 2]], [[3]]]],
            [[[[1]], [[3, 3]]], [[[1, 3]], [[3]]]],
            [[[[2]], [[1, 1]]], [[[1, 2]], [[1]]]],
            [[[[2]], [[1, 2]]], [[[2, 2]], [[1]]]],
            [[[[2]], [[2, 2]]], [[[2, 2]], [[2]]]],
            [[[[2]], [[1, 3]]], [[[2, 3]], [[1]]]],
            [[[[2]], [[2, 3]]], [[[2, 2]], [[3]]]],
            [[[[2]], [[3, 3]]], [[[2, 3]], [[3]]]],
            [[[[3]], [[1, 1]]], [[[1, 3]], [[1]]]],
            [[[[3]], [[1, 2]]], [[[1, 3]], [[2]]]],
            [[[[3]], [[2, 2]]], [[[2, 3]], [[2]]]],
            [[[[3]], [[1, 3]]], [[[3, 3]], [[1]]]],
            [[[[3]], [[2, 3]]], [[[3, 3]], [[2]]]],
            [[[[3]], [[3, 3]]], [[[3, 3]], [[3]]]]]
            
            sage: K = KirillovReshetikhinCrystal(['D',4,1],1,1)
            sage: L = KirillovReshetikhinCrystal(['D',4,1],2,1)
            sage: f = K.R_matrix(L)
            sage: T = TensorProductOfCrystals(K,L)
            sage: b = T( K(rows=[[1]]), L(rows=[]) ) 
            sage: f(b)
            [[[2], [-2]], [[1]]]

        Alternatively, one can compute the combinatorial `R`-matrix using the isomorphism method
        of digraphs::

            sage: K1 = KirillovReshetikhinCrystal(['A',2,1],1,1)
            sage: K2 = KirillovReshetikhinCrystal(['A',2,1],2,1)
            sage: T1 = TensorProductOfCrystals(K1,K2)
            sage: T2 = TensorProductOfCrystals(K2,K1)
            sage: T1.digraph().is_isomorphic(T2.digraph(), edge_labels = True, certify = True) #todo: not implemented (see #10904 and #10549)
            (True, {[[[1]], [[2], [3]]]: [[[1], [3]], [[2]]], [[[3]], [[2], [3]]]: [[[2], [3]], [[3]]], 
            [[[3]], [[1], [3]]]: [[[1], [3]], [[3]]], [[[1]], [[1], [3]]]: [[[1], [3]], [[1]]], [[[1]], 
            [[1], [2]]]: [[[1], [2]], [[1]]], [[[2]], [[1], [2]]]: [[[1], [2]], [[2]]], [[[3]], 
            [[1], [2]]]: [[[2], [3]], [[1]]], [[[2]], [[1], [3]]]: [[[1], [2]], [[3]]], [[[2]], [[2], [3]]]: [[[2], [3]], [[2]]]})
        """
        T1 = TensorProductOfCrystals(self, K)
        T2 = TensorProductOfCrystals(K, self)
        gen1 = T1( self.module_generator(), K.module_generator() )
        gen2 = T2( K.module_generator(), self.module_generator() )
        g = { gen1 : gen2 }
        return T1.crystal_morphism(g, acyclic = False)


class KirillovReshetikhinCrystalFromPromotion(KirillovReshetikhinGenericCrystal, AffineCrystalFromClassicalAndPromotion):
    r"""
    This generic class assumes that the Kirillov-Reshetikhin crystal is constructed
    from a classical crystal 'classical_decomposition' and an automorphism 'promotion' and its inverse 
    which corresponds to a Dynkin diagram automorphism 'dynkin_diagram_automorphism'.

    Each instance using this class needs to implement the methods:
    - classical_decomposition
    - promotion
    - promotion_inverse
    - dynkin_diagram_automorphism
    """
    def __init__(self, cartan_type, r, s):
        r"""
        TESTS::

            sage: K = KirillovReshetikhinCrystal(['B',2,1], 1, 1)
            sage: K
            Kirillov-Reshetikhin crystal of type ['B', 2, 1] with (r,s)=(1,1)
            sage: TestSuite(K).run()
        """
        KirillovReshetikhinGenericCrystal.__init__(self, cartan_type, r ,s)
        AffineCrystalFromClassicalAndPromotion.__init__(self, cartan_type, self.classical_decomposition(),
                                                        self.promotion(), self.promotion_inverse(),
                                                        self.dynkin_diagram_automorphism(0))


class KR_type_A(KirillovReshetikhinCrystalFromPromotion):
    r"""
    Class of Kirillov-Reshetikhin crystals of type `A_n^{(1)}`.

    EXAMPLES::

        sage: K = KirillovReshetikhinCrystal(['A',3,1], 2,2)
        sage: b = K(rows=[[1,2],[2,4]])
        sage: b.f(0)
        [[1, 1], [2, 2]]
    """

    def classical_decomposition(self):
        """
        Specifies the classical crystal underlying the KR crystal of type A.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['A',3,1], 2,2)
            sage: K.classical_decomposition()
            The crystal of tableaux of type ['A', 3] and shape(s) [[2, 2]]
        """
        return CrystalOfTableaux(self.cartan_type().classical(), shape = [self.s() for i in range(1,self.r()+1)])
    
    def promotion(self):
        """
        Specifies the promotion operator used to construct the affine type A crystal.
        For type A this corresponds to the Dynkin diagram automorphism which maps i to i+1 mod n+1,
        where n is the rank.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['A',3,1], 2,2)
            sage: b = K.classical_decomposition()(rows=[[1,2],[3,4]])
            sage: K.promotion()(b)
            [[1, 3], [2, 4]]
        """
        return lambda x : self.classical_crystal(x.to_tableau().promotion(self._cartan_type[1]))
    
    def promotion_inverse(self):
        """
        Specifies the inverse promotion operator used to construct the affine type A crystal.
        For type A this corresponds to the Dynkin diagram automorphism which maps i to i-1 mod n+1,
        where n is the rank.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['A',3,1], 2,2)
            sage: b = K.classical_decomposition()(rows=[[1,3],[2,4]])
            sage: K.promotion_inverse()(b)
            [[1, 2], [3, 4]]
            sage: b = K.classical_decomposition()(rows=[[1,2],[3,3]])
            sage: K.promotion_inverse()(K.promotion()(b))
            [[1, 2], [3, 3]]
        """
        return lambda x : self.classical_crystal(x.to_tableau().promotion_inverse(self._cartan_type[1]))

    def dynkin_diagram_automorphism(self, i):
        """
        Specifies the Dynkin diagram automorphism underlying the promotion action on the crystal
        elements. The automorphism needs to map node 0 to some other Dynkin node.

        For type A we use the Dynkin diagram automorphism which maps i to i+1 mod n+1, where n is the rank.

        EXAMPLES::
        
            sage: K = KirillovReshetikhinCrystal(['A',3,1], 2,2)
            sage: K.dynkin_diagram_automorphism(0)
            1
            sage: K.dynkin_diagram_automorphism(3)
            0
        """
        aut = range(1,self.cartan_type().rank())+[0]
        return aut[i]

class KR_type_vertical(KirillovReshetikhinCrystalFromPromotion):
    r"""
    Class of Kirillov-Reshetikhin crystals `B^{r,s}` of type `D_n^{(1)}` for `r\le n-2`,
    `B_n^{(1)}` for `r<n`, and `A_{2n-1}^{(2)}` for `r\le n`.

    EXAMPLES::

        sage: K = KirillovReshetikhinCrystal(['D',4,1], 2,2)
        sage: b = K(rows=[])
        sage: b.f(0)
        [[1], [2]]
        sage: b.f(0).f(0)
        [[1, 1], [2, 2]]
        sage: b.e(0)
        [[-2], [-1]]
        sage: b.e(0).e(0)
        [[-2, -2], [-1, -1]]
        
        sage: K = KirillovReshetikhinCrystal(['D',5,1], 3,1)
        sage: b = K(rows=[[1]])
        sage: b.e(0)
        [[3], [-3], [-2]]

        sage: K = KirillovReshetikhinCrystal(['B',3,1], 1,1)
        sage: [[b,b.f(0)] for b in K]
        [[[[1]], None], [[[2]], None], [[[3]], None], [[[0]], None], [[[-3]], None], [[[-2]], [[1]]], [[[-1]], [[2]]]]

        sage: K = KirillovReshetikhinCrystal(['A',5,2], 1,1)
        sage: [[b,b.f(0)] for b in K]
        [[[[1]], None], [[[2]], None], [[[3]], None], [[[-3]], None], [[[-2]], [[1]]], [[[-1]], [[2]]]]
    """
 
    def classical_decomposition(self):
        r"""
        Specifies the classical crystal underlying the Kirillov-Reshetikhin crystal of type `D_n^{(1)}`, 
        `B_n^{(1)}`, and `A_{2n-1}^{(2)}`.
        It is given by `B^{r,s} \cong \oplus_\Lambda B(\Lambda)` where `\Lambda` are weights obtained from 
        a rectangle of width s and height r by removing verticle dominoes. Here we identify the fundamental
        weight `\Lambda_i` with a column of height `i`.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['D',4,1], 2,2)
            sage: K.classical_decomposition()
            The crystal of tableaux of type ['D', 4] and shape(s) [[], [1, 1], [2, 2]]
        """
        return CrystalOfTableaux(self.cartan_type().classical(),
                                 shapes = vertical_dominoes_removed(self.r(),self.s()))
    
    def promotion(self):
        """
        Specifies the promotion operator used to construct the affine type `D_n^{(1)}` etc. crystal.
        This corresponds to the Dynkin diagram automorphism which interchanges nodes 0 and 1,
        and leaves all other nodes unchanged. On the level of crystals it is constructed using
        `\pm` diagrams.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['D',4,1], 2,2)
            sage: promotion = K.promotion()
            sage: b = K.classical_decomposition()(rows=[])
            sage: promotion(b)
            [[1, 2], [-2, -1]]
            sage: b = K.classical_decomposition()(rows=[[1,3],[2,-1]])
            sage: promotion(b)
            [[1, 3], [2, -1]]
            sage: b = K.classical_decomposition()(rows=[[1],[-3]])
            sage: promotion(b)
            [[2, -3], [-2, -1]]
        """
        T = self.classical_decomposition()
        ind = T.index_set()
        ind.remove(1)
        return T.crystal_morphism( self.promotion_on_highest_weight_vectors(), index_set = ind)
    
    promotion_inverse = promotion
    
    def dynkin_diagram_automorphism(self, i):
        """
        Specifies the Dynkin diagram automorphism underlying the promotion action on the crystal
        elements. The automorphism needs to map node 0 to some other Dynkin node.

        Here we use the Dynkin diagram automorphism which interchanges nodes 0 and 1 and leaves 
        all other nodes unchanged.

        EXAMPLES::
        
            sage: K = KirillovReshetikhinCrystal(['D',4,1],1,1)
            sage: K.dynkin_diagram_automorphism(0)
            1
            sage: K.dynkin_diagram_automorphism(1)
            0
            sage: K.dynkin_diagram_automorphism(4)
            4
        """
        aut = [1,0]+range(2,self.cartan_type().rank())
        return aut[i]

    def promotion_on_highest_weight_vectors(self):
        """
        Calculates promotion on `{2,3,...,n}` highest weight vectors.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['D',4,1], 2,2)
            sage: T = K.classical_decomposition()
            sage: hw = [ b for b in T if all(b.epsilon(i)==0 for i in [2,3,4]) ]
            sage: [K.promotion_on_highest_weight_vectors()(b) for b in hw]
            [[[1, 2], [-2, -1]], [[2, 2], [-2, -1]], [[1, 2], [3, -1]], [[2], [-2]],
            [[1, 2], [2, -2]], [[2, 2], [-1, -1]], [[2, 2], [3, -1]], [[2, 2], [3, 3]],
            [], [[1], [2]], [[1, 1], [2, 2]], [[2], [-1]], [[1, 2], [2, -1]], [[2], [3]],
            [[1, 2], [2, 3]]]
        """
        return lambda b: self.from_pm_diagram_to_highest_weight_vector(self.from_highest_weight_vector_to_pm_diagram(b).sigma())

    def from_highest_weight_vector_to_pm_diagram(self, b):
        """
        This gives the bijection between an element b in the classical decomposition
        of the KR crystal that is `{2,3,..,n}`-highest weight and `\pm` diagrams.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['D',4,1], 2,2)
            sage: T = K.classical_decomposition()
            sage: b = T(rows=[[2],[-2]])
            sage: pm = K.from_highest_weight_vector_to_pm_diagram(b); pm
            [[1, 1], [0, 0], [0]]
            sage: pm.__repr__(pretty_printing=True)
            +
            -
            sage: b = T(rows=[])
            sage: pm=K.from_highest_weight_vector_to_pm_diagram(b); pm
            [[0, 2], [0, 0], [0]]
            sage: pm.__repr__(pretty_printing=True)

            sage: hw = [ b for b in T if all(b.epsilon(i)==0 for i in [2,3,4]) ]
            sage: all(K.from_pm_diagram_to_highest_weight_vector(K.from_highest_weight_vector_to_pm_diagram(b)) == b for b in hw)
            True
        """
        n = self.cartan_type().rank()-1
        inner = Partition([Integer(b.weight()[i]) for i in range(1,n+1)])
        inter = Partition([len([i for i in r if i>0]) for r in b.to_tableau()])
        outer = b.to_tableau().shape()
        return PMDiagram([self.r(), self.s(), outer, inter, inner], from_shapes=True)
 
    def from_pm_diagram_to_highest_weight_vector(self, pm):
        """
        This gives the bijection between a `\pm` diagram and an element b in the classical 
        decomposition of the KR crystal that is {2,3,..,n}-highest weight.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['D',4,1], 2,2)
            sage: pm = sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[1, 1], [0, 0], [0]])
            sage: K.from_pm_diagram_to_highest_weight_vector(pm)
            [[2], [-2]]
        """
        u = [b for b in self.classical_decomposition().module_generators if b.to_tableau().shape() == pm.outer_shape()][0]
        ct = self.cartan_type()
        rank = ct.rank()-1
        ct_type = ct.classical().type()
        assert ct_type in ['B', 'C', 'D']
        list = []
        for h in pm.heights_of_addable_plus():
            list += range(1,h+1)
        for h in pm.heights_of_minus():
            if ct_type == 'D':
                list += range(1,rank+1)+[rank-2-k for k in range(rank-1-h)]
            elif ct_type == 'B':
                list += range(1,rank+1)+[rank-k for k in range(rank+1-h)]
            else:
                list += range(1,rank+1)+[rank-1-k for k in range(rank-h)]
        for i in reversed(list):
            u = u.f(i)
        return u

class KR_type_E6(KirillovReshetikhinCrystalFromPromotion):
    r"""
    Class of Kirillov-Reshetikhin crystals of type `E_6^{(1)}` for `r=1,2,6`.

    EXAMPLES::

        sage: K = KirillovReshetikhinCrystal(['E',6,1],2,1)
        sage: K.module_generator().e(0)
        []
        sage: K.module_generator().e(0).f(0)
        [[[2, -1], [1]]]
        sage: K = KirillovReshetikhinCrystal(['E',6,1], 1,1)
        sage: b = K.module_generator()
        sage: b
        [[1]]
        sage: b.e(0)
        [[-2, 1]]
        sage: b = [t for t in K if t.epsilon(1) == 1 and t.phi(3) == 1 and t.phi(2) == 0 and t.epsilon(2) == 0][0]
        sage: b
        [[-1, 3]]
        sage: b.e(0)
        [[-1, -2, 3]]

    The elements of the Kirillov-Reshetikhin crystals can be constructed from a classical
    crystal element using :meth:`rectract`.

    EXAMPLES::

        sage: K = KirillovReshetikhinCrystal(['E',6,1],2,1)
        sage: La = K.cartan_type().classical().root_system().weight_lattice().fundamental_weights()
        sage: H = HighestWeightCrystal(La[2])
        sage: t = H.module_generator()
        sage: t
        [[[2, -1], [1]]]
        sage: type(K.retract(t))
        <class 'sage.combinat.crystals.affine.KR_type_E6_with_category.element_class'>
        sage: K.retract(t).e(0)
        []

    TESTS::

        sage: K = KirillovReshetikhinCrystal(['E',6,1], 2,1)
        sage: La = K.weight_lattice_realization().fundamental_weights()
        sage: all(b.weight() == sum( (K.affine_weight(b.lift())[i] * La[i] for i in K.index_set()), 0*La[0]) for b in K)  # long time (26s on sage.math, 2011)
        True
    """

    def classical_decomposition(self):
        """
        Specifies the classical crystal underlying the KR crystal of type `E_6^{(1)}`.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['E',6,1], 2,2)
            sage: K.classical_decomposition()
            Direct sum of the crystals Family (Finite dimensional highest weight crystal of type ['E', 6] and highest weight 0, Finite dimensional highest weight crystal of type ['E', 6] and highest weight Lambda[2], Finite dimensional highest weight crystal of type ['E', 6] and highest weight 2*Lambda[2])
            sage: K = KirillovReshetikhinCrystal(['E',6,1], 1,2)
            sage: K.classical_decomposition()
            Direct sum of the crystals Family (Finite dimensional highest weight crystal of type ['E', 6] and highest weight 2*Lambda[1],)
        """
        La = self.cartan_type().classical().root_system().weight_lattice().fundamental_weights()
        if self.r() in [1,6]:
            dw = [self.s()*La[self.r()]]
        elif self.r() == 2:
            dw = sum( ([k*La[2]] for k in range(self.s()+1)), [])
        else:
            raise ValueError
        return DirectSumOfCrystals([HighestWeightCrystal(dominant_weight) for dominant_weight in dw], keepkey = False)

    def dynkin_diagram_automorphism(self, i):
        r"""
        Specifies the Dynkin diagram automorphism underlying the promotion action on the crystal
        elements. The automorphism needs to map node 0 to some other Dynkin node.

        Here we use the Dynkin diagram automorphism of order 3 which maps node 0 to node 1.

        EXAMPLES::
        
            sage: K = KirillovReshetikhinCrystal(['E',6,1],2,1)
            sage: [K.dynkin_diagram_automorphism(i) for i in K.index_set()]
            [1, 6, 3, 5, 4, 2, 0]
        """
        aut = [1,6,3,5,4,2,0]
        return aut[i]

    def affine_weight(self, b):
        r"""
        Returns the affine level zero weight corresponding to the element b of the classical
        crystal underlying self. For the coefficients to calculate the level, see Kac pg. 48.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['E',6,1],2,1)
            sage: [K.affine_weight(x.lift()) for x in K if all(x.epsilon(i) == 0 for i in [2,3,4,5])]
            [(0, 0, 0, 0, 0, 0, 0),
            (-2, 0, 1, 0, 0, 0, 0),
            (-1, -1, 0, 0, 0, 1, 0),
            (0, 0, 0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0, 1, -2),
            (0, -1, 1, 0, 0, 0, -1),
            (-1, 0, 0, 1, 0, 0, -1),
            (-1, -1, 0, 0, 1, 0, -1),
            (0, 0, 0, 0, 0, 0, 0),
            (0, -2, 0, 1, 0, 0, 0)]
        """
        simple_roots = self.cartan_type().classical().root_system().ambient_space().simple_roots()
        index_set = b.parent().index_set()
        weight = [ Integer(b.weight().scalar( simple_roots[i] )) for i in index_set ]
        E6_coeffs = [ 1, 2, 2, 3, 2, 1 ]
        return tuple( [-sum([ weight[i-1] * E6_coeffs[i-1] for i in index_set ])] + weight )


    @cached_method
    def hw_auxiliary(self):
        r"""
        Returns the `{2,3,4,5}` highest weight elements of self.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['E',6,1],2,1)
            sage: K.hw_auxiliary()
            [[], [[[2, -1], [1]]], [[[5, -3], [-1, 3]]], [[[6, -2], [-6, 2]]], 
            [[[5, -2, -6], [-6, 2]]], [[[-1], [-6, 2]]], [[[3, -1, -6], [1]]], 
            [[[4, -3, -6], [-1, 3]]], [[[1, -3], [-1, 3]]], [[[-1], [-1, 3]]]]
        """
        return [x for x in self.classical_decomposition() if all(x.epsilon(i) == 0 for i in [2,3,4,5])] 

    @cached_method
    def highest_weight_dict(self):
        r"""
        Returns a dictionary between `{1,2,3,4,5}` highest weight elements, and a tuple of affine weights and its classical component.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['E',6,1],2,1)
            sage: K.highest_weight_dict()
            {[[[3, -1, -6], [1]]]: ((-1, 0, 0, 1, 0, 0, -1), 1), 
            [[[5, -2, -6], [-6, 2]]]: ((0, 0, 0, 0, 0, 1, -2), 1), 
            [[[2, -1], [1]]]: ((-2, 0, 1, 0, 0, 0, 0), 1), 
            [[[6, -2], [-6, 2]]]: ((0, 0, 0, 0, 0, 0, 0), 1), 
            []: ((0, 0, 0, 0, 0, 0, 0), 0)}
        """
        hw = [x for x in self.hw_auxiliary() if x.epsilon(1) == 0]
        dic = dict( ( x, tuple( [self.affine_weight(x), len(x)] ) ) for x in hw )
        assert len(hw) == len(dic)
        return dic

    @cached_method
    def highest_weight_dict_inv(self):
        r"""
        Returns a dictionary between a tuple of affine weights and a classical component, and 
        `{2,3,4,5,6}` highest weight elements.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['E',6,1],2,1)
            sage: K.highest_weight_dict_inv()
            {((0, 0, 0, 0, 0, 0, 0), 0): [],
            ((-1, -1, 0, 0, 0, 1, 0), 1): [[[5, -3], [-1, 3]]], 
            ((0, 0, 0, 0, 0, 0, 0), 1): [[[1, -3], [-1, 3]]], 
            ((0, -2, 0, 1, 0, 0, 0), 1): [[[-1], [-1, 3]]], 
            ((-2, 0, 1, 0, 0, 0, 0), 1): [[[2, -1], [1]]]}
        """
        hw = [x for x in self.hw_auxiliary() if x.epsilon(6) == 0]
        dic = dict( ( tuple( [self.affine_weight(x), len(x)] ), x ) for x in hw )
        assert len(hw) == len(dic)
        return dic
    
    def automorphism_on_affine_weight(self, weight):
        r"""
        Acts with the Dynkin diagram automorphism on affine weights as outputted by the affine_weight method.

        EXAMPLES::
 
            sage: K = KirillovReshetikhinCrystal(['E',6,1],2,1)
            sage: [[x[0], K.automorphism_on_affine_weight(x[0])] for x in K.highest_weight_dict().values()]
            [[(-1, 0, 0, 1, 0, 0, -1), (-1, -1, 0, 0, 0, 1, 0)], 
            [(0, 0, 0, 0, 0, 1, -2), (-2, 0, 1, 0, 0, 0, 0)], 
            [(-2, 0, 1, 0, 0, 0, 0), (0, -2, 0, 1, 0, 0, 0)], 
            [(0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0)], 
            [(0, 0, 0, 0, 0, 0, 0), (0, 0, 0, 0, 0, 0, 0)]]
        """
        f = self.dynkin_diagram_automorphism
        return tuple( [weight[f(f(i))] for i in self.index_set()] )

    def promotion_on_highest_weight_vectors(self):
        r"""
        Gives a dictionary of the promotion map on `{1,2,3,4,5}` highest weight elements to
        `{2,3,4,5,6}` elements in self.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['E',6,1],2,1)
            sage: dic = K.promotion_on_highest_weight_vectors()
            sage: dic
            {[[[2, -1], [1]]]: [[[-1], [-1, 3]]], 
            [[[5, -2, -6], [-6, 2]]]: [[[2, -1], [1]]], 
            [[[3, -1, -6], [1]]]: [[[5, -3], [-1, 3]]], 
            [[[6, -2], [-6, 2]]]: [], []: [[[1, -3], [-1, 3]]]}
        """
        dic = self.highest_weight_dict()
        dic_inv = self.highest_weight_dict_inv()
        dic_weight = {}
        for (weight, i) in dic.values():
            dic_weight[weight] = dic_weight.get(weight, []) + [i]
        map_index = lambda (i, list) : max(list)+min(list)-i
        map_element = lambda x : tuple([self.automorphism_on_affine_weight(dic[x][0]), map_index((dic[x][1],dic_weight[dic[x][0]]))])
        return dict( (x, dic_inv[map_element(x)]) for x in dic.keys() )

    def promotion_on_highest_weight_vectors_function(self):
        return lambda x : self.promotion_on_highest_weight_vectors()[x]

    def promotion(self):
        """
        Specifies the promotion operator used to construct the affine type `E_6^{(1)}` crystal.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['E',6,1], 2,1)
            sage: promotion = K.promotion()
            sage: all(promotion(promotion(promotion(b))) == b for b in K.classical_decomposition())
            True
            sage: K = KirillovReshetikhinCrystal(['E',6,1],1,1)
            sage: promotion = K.promotion()
            sage: all(promotion(promotion(promotion(b))) == b for b in K.classical_decomposition())
            True
        """
        T = self.classical_decomposition()
        ind = [1,2,3,4,5]
        return T.crystal_morphism( self.promotion_on_highest_weight_vectors_function(), automorphism = lambda i : self.dynkin_diagram_automorphism(i), index_set = ind)
    
    def promotion_inverse(self):
        r"""
        Returns the inverse promotion. Since promotion is of order 3, the inverse promotion is the same
        as promotion applied twice.

        EXAMPLES::
        
            sage: K = KirillovReshetikhinCrystal(['E',6,1], 2,1)
            sage: p = K.promotion()
            sage: p_inv = K.promotion_inverse()
            sage: all(p_inv(p(b)) == b for b in K.classical_decomposition())
            True
        """
        p = self.promotion()
        return lambda x : p(p(x))


class KR_type_C(KirillovReshetikhinGenericCrystal, AffineCrystalFromClassical):
    r"""
    Class of Kirillov-Reshetikhin crystals `B^{r,s}` of type `C_n^{(1)}` for `r<n`.

    EXAMPLES::

        sage: K = KirillovReshetikhinCrystal(['C',2,1], 1,2)
        sage: K
        Kirillov-Reshetikhin crystal of type ['C', 2, 1] with (r,s)=(1,2)
        sage: b = K(rows=[])
        sage: b.f(0)
        [[1, 1]]
        sage: b.e(0)
        [[-1, -1]]
    """
    def __init__(self, cartan_type, r, s):
        r"""
        Initializes a Kirillov-Reshetikhin crystal of type `C_n^{(1)}`.

        TESTS::

            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_C(['C',2,1], 1, 1)
            sage: K
            Kirillov-Reshetikhin crystal of type ['C', 2, 1] with (r,s)=(1,1)
            sage: TestSuite(K).run()
        """
        KirillovReshetikhinGenericCrystal.__init__(self, cartan_type, r ,s)
        AffineCrystalFromClassical.__init__(self, cartan_type, self.classical_decomposition())

    def classical_decomposition(self):
        """
        Specifies the classical crystal underlying the Kirillov-Reshetikhin crystal of type `C_n^{(1)}`.
        It is given by `B^{r,s} \cong \oplus_\Lambda B(\Lambda)` where `\Lambda` are weights obtained from 
        a rectangle of width s and height r by removing horizontal dominoes. Here we identify the fundamental
        weight `\Lambda_i` with a column of height `i`.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['C',3,1], 2,2)
            sage: K.classical_decomposition()
            The crystal of tableaux of type ['C', 3] and shape(s) [[], [2], [2, 2]]
        """
        return CrystalOfTableaux(self.cartan_type().classical(), 
                                 shapes = horizontal_dominoes_removed(self.r(),self.s()))

    def ambient_crystal(self):
        r"""
        Returns the ambient crystal `'B^{r,s}` of type `A_{2n+1}^{(2)}` associated to the Kirillov-Reshetikhin
        crystal of type `C_n^{(1)}`. This ambient crystal is used to construct the zero arrows.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['C',3,1], 2,3)
            sage: K.ambient_crystal()
            Kirillov-Reshetikhin crystal of type ['B', 4, 1]^* with (r,s)=(2,3)
        """
        return KirillovReshetikhinCrystal(['A',2*self.cartan_type().classical().rank()+1,2], self.r(), self.s())

    def ambient_dict_pm_diagrams(self):
        r"""
        Gives a dictionary of all self-dual `\pm` diagrams for the ambient crystal.
        Their key is their inner shape.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['C',2,1], 1,2)
            sage: K.ambient_dict_pm_diagrams()
            {[]: [[1, 1], [0]], [2]: [[0, 0], [2]]}
            sage: K = KirillovReshetikhinCrystal(['C',3,1], 2,2)
            sage: K.ambient_dict_pm_diagrams()
            {[2, 2]: [[0, 0], [0, 0], [2]], []: [[1, 1], [0, 0], [0]], [2]: [[0, 0], [1, 1], [0]]}
            sage: K = KirillovReshetikhinCrystal(['C',3,1], 2,3)
            sage: K.ambient_dict_pm_diagrams()
            {[3, 3]: [[0, 0], [0, 0], [3]], [3, 1]: [[0, 0], [1, 1], [1]], [1, 1]: [[1, 1], [0, 0], [1]]}
        """
        list = []
        s = self.s()
        r = self.r()
        m = int(s/2)
        for i in range(m+1):
            for la in IntegerVectors(m-i, min_length=r, max_length=r):
                list.append(PMDiagram([[j,j] for j in la]+[[s-2*m+2*i]]))
        return dict( (x.inner_shape(), x) for x in list )

    def ambient_highest_weight_dict(self):
        r"""
        Gives a dictionary of all `{2,...,n+1}`-highest weight vectors in the ambient crystal.
        Their key is the inner shape of their corresponding `\pm` diagram, or equivalently, their
        `{2,...,n+1}` weight.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['C',3,1], 2,2)
            sage: K.ambient_highest_weight_dict()
            {[]: [[2], [-2]], [2, 2]: [[2, 2], [3, 3]], [2]: [[1, 2], [2, -1]]}
        """
        A = self.ambient_dict_pm_diagrams()
        ambient = self.ambient_crystal()
        return dict( (key, ambient.retract(ambient.from_pm_diagram_to_highest_weight_vector(A[key]))) for key in A )

    def highest_weight_dict(self):
        r"""
        Gives a dictionary of the classical highest weight vectors of self.
        Their key is their shape.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['C',3,1], 2,2)
            sage: K.highest_weight_dict()
            {[2, 2]: [[1, 1], [2, 2]], []: [], [2]: [[1, 1]]}
        """
        return dict( (x.lift().to_tableau().shape(),x) for x in self.module_generators )

    def to_ambient_crystal(self):
        r"""
        Provides a map from the Kirillov-Reshetikhin crystal of type `C_n^{(1)}` to the
        ambient crystal of type `A_{2n+1}^{(2)}`.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['C',3,1], 2,2)
            sage: b=K(rows=[[1,1]])
            sage: K.to_ambient_crystal()(b)
            [[1, 2], [2, -1]]
            sage: b=K(rows=[])
            sage: K.to_ambient_crystal()(b)
            [[2], [-2]]
            sage: K.to_ambient_crystal()(b).parent() # Anne: please check this!!!!
            Kirillov-Reshetikhin crystal of type ['B', 4, 1]^* with (r,s)=(2,2)
        """
        keys = self.highest_weight_dict().keys()
        pdict = dict( (self.highest_weight_dict()[key], self.ambient_highest_weight_dict()[key]) for key in keys )
        return self.crystal_morphism( pdict, index_set = self.cartan_type().classical().index_set(), 
                                      automorphism = lambda i : i+1 )

    def from_ambient_crystal(self):
        r"""
        Provides a map from the ambient crystal of type `A_{2n+1}^{(2)}` to the Kirillov-Reshetikhin crystal of 
        type `C_n^{(1)}`. Note that this map is only well-defined on elements that are in the image
        type `C_n^{(1)}` elements under `to_ambient_crystal`.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['C',3,1], 2,2)
            sage: b=K.ambient_crystal()(rows=[[2,2],[3,3]])
            sage: K.from_ambient_crystal()(b)
            [[1, 1], [2, 2]]
        """
        keys = self.highest_weight_dict().keys()
        pdict_inv = dict( (self.ambient_highest_weight_dict()[key], self.highest_weight_dict()[key]) for key in keys )
        return self.crystal_morphism( pdict_inv, index_set = [j+1 for j in self.cartan_type().classical().index_set()], 
                                      automorphism = lambda i : i-1 )

class KR_type_CElement(AffineCrystalFromClassicalElement):
    r"""
    Class for the elements in the Kirillov-Reshetikhin crystals `B^{r,s}` of type `C_n^{(1)}` for `r<n`.

    EXAMPLES::

        sage: K=KirillovReshetikhinCrystal(['C',3,1],1,2)
        sage: type(K.module_generators[0])
        <class 'sage.combinat.crystals.kirillov_reshetikhin.KR_type_C_with_category.element_class'>
    """

    def e0(self):
        r"""
        Gives `e_0` on self by mapping self to the ambient crystal, calculating `e_1 e_0` there and
        pulling the element back.

        EXAMPLES::

            sage: K=KirillovReshetikhinCrystal(['C',3,1],1,2)
            sage: b = K(rows=[])
            sage: b.e(0)
            [[-1, -1]]
        """
        b = self.parent().to_ambient_crystal()(self).e(1)
        if b is None:
            return None
        b = b.e(0)
        return self.parent().from_ambient_crystal()(b)
    
    def f0(self):
        r"""
        Gives `f_0` on self by mapping self to the ambient crystal, calculating `f_1 f_0` there and
        pulling the element back.

        EXAMPLES::

            sage: K=KirillovReshetikhinCrystal(['C',3,1],1,2)
            sage: b = K(rows=[])
            sage: b.f(0)
            [[1, 1]]
        """
        b = self.parent().to_ambient_crystal()(self).f(1)
        if b is None:
            return None
        b = b.f(0)
        return self.parent().from_ambient_crystal()(b)

    def epsilon0(self):
        r"""
        Calculates `\epsilon_0` of self by mapping the element to the ambient crystal
        and calculating `\epsilon_1` there.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['C',2,1], 1,2)
            sage: b=K(rows=[[1,1]])
            sage: b.epsilon(0)
            2
        """
        b = self.parent().to_ambient_crystal()(self)
        return b.epsilon(1)

    def phi0(self):
        r"""
        Calculates `\phi_0` of self by mapping the element to the ambient crystal
        and calculating `\phi_1` there.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['C',2,1], 1,2)
            sage: b=K(rows=[[-1,-1]])
            sage: b.phi(0)
            2
        """
        b = self.parent().to_ambient_crystal()(self)
        return b.phi(1)

KR_type_C.Element = KR_type_CElement


class KR_type_A2(KirillovReshetikhinGenericCrystal, AffineCrystalFromClassical):
    r"""
    Class of Kirillov-Reshetikhin crystals `B^{r,s}` of type `A_{2n}^{(2)}` for `1\le r \le n`
    in the realization with classical subalgebra `B_n`. The cartan type in this case is inputted as
    the dual of `A_{2n}^{(2)}`.
    This is an alternative implementation to KR_type_box which uses the classical decomposition
    into type `C_n` crystals.

    EXAMPLES::

        sage: C = CartanType(['A',4,2]).dual()
        sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_A2(C, 1, 1)
        sage: K
        Kirillov-Reshetikhin crystal of type ['BC', 2, 2]^* with (r,s)=(1,1)
        sage: b = K(rows=[[-1]])
        sage: b.f(0)
        [[1]]
        sage: b.e(0)

    We can now check whether the two KR crystals of type `A_4^{(2)}` (namely the KR crystal and its dual
    construction) are isomorphic up to relabelling of the edges::

        sage: C = CartanType(['A',4,2])
        sage: K = KirillovReshetikhinCrystal(C,1,1)
        sage: Kdual = KirillovReshetikhinCrystal(C.dual(),1,1)
        sage: G = K.digraph()
        sage: Gdual = Kdual.digraph()
        sage: f = {0:2, 1:1, 2:0}
        sage: Gnew = DiGraph(); Gnew.add_vertices(Gdual.vertices()); Gnew.add_edges([(u,v,f[i]) for (u,v,i) in Gdual.edges()])
        sage: G.is_isomorphic(Gnew, edge_labels = True)
        True
    """
    def __init__(self, cartan_type, r, s):
        r"""
        Initializes a Kirillov-Reshetikhin crystal of type `A_{2n}^{(2)}` in the realization
        with classical subalgebra `B_n`.

        TESTS::

            sage: C = CartanType(['A',4,2]).dual()
            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_A2(C, 1, 1)
            sage: K
            Kirillov-Reshetikhin crystal of type ['BC', 2, 2]^* with (r,s)=(1,1)
            sage: TestSuite(K).run()
        """
        KirillovReshetikhinGenericCrystal.__init__(self, cartan_type, r ,s)
        AffineCrystalFromClassical.__init__(self, cartan_type, self.classical_decomposition())

    def classical_decomposition(self):
        """
        Specifies the classical crystal underlying the Kirillov-Reshetikhin crystal of type `A_{2n}^{(2)}`
        with `B_n` as classical subdiagram.
        It is given by `B^{r,s} \cong \oplus_\Lambda B(\Lambda)` where `B(\Lambda)` is a highest weight crystal of type
        `B_n` of highest weight `\Lambda`. The sum is over all weights `Lambda` obtained from 
        a rectangle of width s and height r by removing horizontal dominoes. Here we identify the fundamental
        weight `\Lambda_i` with a column of height `i`.

        EXAMPLES::

            sage: C = CartanType(['A',4,2]).dual()
            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_A2(C, 2, 2)
            sage: K.classical_decomposition()
            The crystal of tableaux of type ['B', 2] and shape(s) [[], [2], [2, 2]]
        """
        return CrystalOfTableaux(['B', self.cartan_type().rank()-1], 
                                 shapes = horizontal_dominoes_removed(self.r(),self.s()))

    def ambient_crystal(self):
        r"""
        Returns the ambient crystal `'B^{r,s}` of type `B_{n+1}^{(1)}` associated to the Kirillov-Reshetikhin
        crystal of type `A_{2n}^{(2)}` dual. This ambient crystal is used to construct the zero arrows.

        EXAMPLES::

            sage: C = CartanType(['A',4,2]).dual()
            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_A2(C, 2, 3)
            sage: K.ambient_crystal()
            Kirillov-Reshetikhin crystal of type ['B', 3, 1] with (r,s)=(2,3)
        """
        return KR_type_vertical(['B', self.cartan_type().rank(), 1], self.r(), self.s())

    def ambient_dict_pm_diagrams(self):
        r"""
        Gives a dictionary of all self-dual `\pm` diagrams for the ambient crystal.
        Their key is their inner shape.

        EXAMPLES::

            sage: C = CartanType(['A',4,2]).dual()
            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_A2(C, 1, 1)
            sage: K.ambient_dict_pm_diagrams()
            {[1]: [[0, 0], [1]]}
            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_A2(C, 1, 2)
            sage: K.ambient_dict_pm_diagrams()
            {[]: [[1, 1], [0]], [2]: [[0, 0], [2]]}
            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_A2(C, 2, 2)
            sage: K.ambient_dict_pm_diagrams()
            {[2, 2]: [[0, 0], [0, 0], [2]], []: [[1, 1], [0, 0], [0]], [2]: [[0, 0], [1, 1], [0]]}
        """
        list = []
        s = self.s()
        r = self.r()
        m = int(s/2)
        for i in range(m+1):
            for la in IntegerVectors(m-i, min_length=r, max_length=r):
                list.append(PMDiagram([[j,j] for j in la]+[[s-2*m+2*i]]))
        return dict( (x.inner_shape(), x) for x in list )

    def ambient_highest_weight_dict(self):
        r"""
        Gives a dictionary of all `{2,...,n+1}`-highest weight vectors in the ambient crystal.
        Their key is the inner shape of their corresponding `\pm` diagram, or equivalently, their
        `{2,...,n+1}` weight.

        EXAMPLES::

            sage: C = CartanType(['A',4,2]).dual()
            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_A2(C, 1, 2)
            sage: K.ambient_highest_weight_dict()
            {[]: [[1, -1]], [2]: [[2, 2]]}
        """
        A = self.ambient_dict_pm_diagrams()
        ambient = self.ambient_crystal()
        return dict( (key, ambient.retract(ambient.from_pm_diagram_to_highest_weight_vector(A[key]))) for key in A )

    def highest_weight_dict(self):
        r"""
        Gives a dictionary of the classical highest weight vectors of self.
        Their key is their shape.

        EXAMPLES::

            sage: C = CartanType(['A',4,2]).dual()
            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_A2(C, 1, 2)
            sage: K.highest_weight_dict()
            {[]: [], [2]: [[1, 1]]}
        """
        return dict( (x.lift().to_tableau().shape(),x) for x in self.module_generators )

    def to_ambient_crystal(self):
        r"""
        Provides a map from the Kirillov-Reshetikhin crystal of type `A_{2n}^{(2)}` to the
        ambient crystal of type `B_{n+1}^{(1)}`.

        EXAMPLES::

            sage: C = CartanType(['A',4,2]).dual()
            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_A2(C, 1, 2)
            sage: b=K(rows=[[1,1]])
            sage: K.to_ambient_crystal()(b)
            [[2, 2]]
            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_A2(C, 2, 2)
            sage: b=K(rows=[[1,1]])
            sage: K.to_ambient_crystal()(b)
            [[1, 2], [2, -1]]
            sage: K.to_ambient_crystal()(b).parent()
            Kirillov-Reshetikhin crystal of type ['B', 3, 1] with (r,s)=(2,2)
        """
        keys = self.highest_weight_dict().keys()
        pdict = dict( (self.highest_weight_dict()[key], self.ambient_highest_weight_dict()[key]) for key in keys )
        return self.crystal_morphism( pdict, index_set = self.cartan_type().classical().index_set(), 
                                      automorphism = lambda i : i+1 )

    def from_ambient_crystal(self):
        r"""
        Provides a map from the ambient crystal of type `B_{n+1}^{(1)}` to the Kirillov-Reshetikhin crystal of 
        type `A_{2n}^{(2)}`. Note that this map is only well-defined on elements that are in the image
        type `A_{2n}^{(2)}` elements under `to_ambient_crystal`.

        EXAMPLES::

            sage: C = CartanType(['A',4,2]).dual()
            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_A2(C, 1, 2)
            sage: b = K.ambient_crystal()(rows=[[2,2]])
            sage: K.from_ambient_crystal()(b)
            [[1, 1]]
        """
        keys = self.highest_weight_dict().keys()
        pdict_inv = dict( (self.ambient_highest_weight_dict()[key], self.highest_weight_dict()[key]) for key in keys )
        return self.crystal_morphism( pdict_inv, index_set = [j+1 for j in self.cartan_type().classical().index_set()], 
                                      automorphism = lambda i : i-1 )

class KR_type_A2Element(AffineCrystalFromClassicalElement):
    r"""
    Class for the elements in the Kirillov-Reshetikhin crystals `B^{r,s}` of type `A_{2n}^{(2)}` for `r<n`
    with underlying classcial algebra `B_n`.

    EXAMPLES::
    
        sage: C = CartanType(['A',4,2]).dual()
        sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_A2(C, 1, 2)
        sage: type(K.module_generators[0])
        <class 'sage.combinat.crystals.kirillov_reshetikhin.KR_type_A2_with_category.element_class'>
    """

    def e0(self):
        r"""
        Gives `e_0` on self by mapping self to the ambient crystal, calculating `e_1 e_0` there and
        pulling the element back.

        EXAMPLES::

            sage: C = CartanType(['A',4,2]).dual()
            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_A2(C, 1, 1)
            sage: b = K(rows=[[1]])
            sage: b.e(0)
            [[-1]]
        """
        b = self.parent().to_ambient_crystal()(self).e(1)
        if b is None:
            return None
        b = b.e(0)
        return self.parent().from_ambient_crystal()(b)
    
    def f0(self):
        r"""
        Gives `f_0` on self by mapping self to the ambient crystal, calculating `f_1 f_0` there and
        pulling the element back.

        EXAMPLES::

            sage: C = CartanType(['A',4,2]).dual()
            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_A2(C, 1, 1)
            sage: b = K(rows=[[-1]])
            sage: b.f(0)
            [[1]]
        """
        b = self.parent().to_ambient_crystal()(self).f(1)
        if b is None:
            return None
        b = b.f(0)
        return self.parent().from_ambient_crystal()(b)

    def epsilon0(self):
        r"""
        Calculates `\epsilon_0` of self by mapping the element to the ambient crystal
        and calculating `\epsilon_1` there.

        EXAMPLES::

            sage: C = CartanType(['A',4,2]).dual()
            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_A2(C, 1, 1)
            sage: b=K(rows=[[1]])
            sage: b.epsilon(0)
            1
        """
        b = self.parent().to_ambient_crystal()(self)
        return b.epsilon(1)

    def phi0(self):
        r"""
        Calculates `\phi_0` of self by mapping the element to the ambient crystal
        and calculating `\phi_1` there.

        EXAMPLES::

            sage: C = CartanType(['A',4,2]).dual()
            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_A2(C, 1, 1)
            sage: b=K(rows=[[-1]])
            sage: b.phi(0)
            1
        """
        b = self.parent().to_ambient_crystal()(self)
        return b.phi(1)

KR_type_A2.Element = KR_type_A2Element


class KR_type_box(KirillovReshetikhinGenericCrystal, AffineCrystalFromClassical):
    r"""
    Class of Kirillov-Reshetikhin crystals `B^{r,s}` of type `A_{2n}^{(2)}` for `r\le n`
    and type `D_{n+1}^{(2)}` for `r<n`.

    EXAMPLES::

        sage: K = KirillovReshetikhinCrystal(['A',4,2], 1,1)
        sage: K
        Kirillov-Reshetikhin crystal of type ['BC', 2, 2] with (r,s)=(1,1)
        sage: b = K(rows=[])
        sage: b.f(0)
        [[1]]
        sage: b.e(0)
        [[-1]]
    """
    def __init__(self, cartan_type, r, s):
        r"""
        Initializes a Kirillov-Reshetikhin crystal ``self``.

        TESTS::

            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_box(['A',4,2], 1, 1)
            sage: K
            Kirillov-Reshetikhin crystal of type ['BC', 2, 2] with (r,s)=(1,1)
            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_box(['D',4,2], 1, 1)
            sage: K
            Kirillov-Reshetikhin crystal of type ['C', 3, 1]^* with (r,s)=(1,1)
            sage: TestSuite(K).run()
        """
        KirillovReshetikhinGenericCrystal.__init__(self, cartan_type, r ,s)
        AffineCrystalFromClassical.__init__(self, cartan_type, self.classical_decomposition())

    def classical_decomposition(self):
        r"""
        Specifies the classical crystal underlying the Kirillov-Reshetikhin crystal of type `A_{2n}^{(2)}`
        and `D_{n+1}^{(2)}`.
        It is given by `B^{r,s} \cong \oplus_\Lambda B(\Lambda)` where `\Lambda` are weights obtained from 
        a rectangle of width s and height r by removing boxes. Here we identify the fundamental
        weight `\Lambda_i` with a column of height `i`.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['A',4,2], 2,2)
            sage: K.classical_decomposition()
            The crystal of tableaux of type ['C', 2] and shape(s) [[], [1], [2], [1, 1], [2, 1], [2, 2]]
            sage: K = KirillovReshetikhinCrystal(['D',4,2], 2,3)
            sage: K.classical_decomposition()
            The crystal of tableaux of type ['B', 3] and shape(s) [[], [1], [2], [1, 1], [3], [2, 1], [3, 1], [2, 2], [3, 2], [3, 3]]
        """
        return CrystalOfTableaux(self.cartan_type().classical(), 
                                 shapes = partitions_in_box(self.r(),self.s()))

    def ambient_crystal(self):
        r"""
        Returns the ambient crystal `'B^{r,2s}` of type `C_n^{(1)}` associated to the Kirillov-Reshetikhin crystal.
        This ambient crystal is used to construct the zero arrows.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['A',4,2], 2,2)
            sage: K.ambient_crystal()
            Kirillov-Reshetikhin crystal of type ['C', 2, 1] with (r,s)=(2,4)
        """
        # calling KR_type_C instead of KirillovReshetikhin(['C',n,1],r,s) has the advantage that 
        # that this also works for r=n for A_{2n}^{(2)}.
        return KR_type_C(['C', self.cartan_type().classical().rank(),1], self.r(), 2*self.s())

    def highest_weight_dict(self):
        r"""
        Gives a dictionary of the classical highest weight vectors of self.
        Their key is 2 times their shape.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['A',6,2], 2,2)
            sage: K.highest_weight_dict()
            {[4, 2]: [[1, 1], [2]], [2, 2]: [[1], [2]], []: [], [4]: [[1, 1]], [4, 4]: [[1, 1], [2, 2]], [2]: [[1]]}
        """
        return dict( (Partition([2*i for i in x.lift().to_tableau().shape()]),x) for x in self.module_generators )

    def ambient_highest_weight_dict(self):
        r"""
        Gives a dictionary of the classical highest weight vectors of the ambient crystal of self.
        Their key is their shape.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['A',6,2], 2,2)
            sage: K.ambient_highest_weight_dict()
            {[4, 2]: [[1, 1, 1, 1], [2, 2]], [2, 2]: [[1, 1], [2, 2]], []: [], [4]: [[1, 1, 1, 1]], [4, 4]: [[1, 1, 1, 1], [2, 2, 2, 2]], 
            [2]: [[1, 1]]}
        """
        return dict( (x.lift().to_tableau().shape(),x) for x in self.ambient_crystal().module_generators )

    def similarity_factor(self):
        r"""
        Sets the similarity factor used to map to the ambient crystal.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['A',6,2], 2,2)
            sage: K.similarity_factor()
            {1: 2, 2: 2, 3: 2}
            sage: K = KirillovReshetikhinCrystal(['D',5,2], 1,1)
            sage: K.similarity_factor()
            {1: 2, 2: 2, 3: 2, 4: 1}
        """    
        C = self.cartan_type().classical()
        p = dict( (i,2) for i in C.index_set() )
        if C.type() == 'B':
            p[C.rank()] = 1
        return p

    def to_ambient_crystal(self):
        r"""
        Provides a map from self to the ambient crystal of type `C_n^{(1)}`.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['D',4,2], 1,1)
            sage: [K.to_ambient_crystal()(b) for b in K]
            [[], [[1, 1]], [[2, 2]], [[3, 3]], [[3, -3]], [[-3, -3]], [[-2, -2]], [[-1, -1]]]
            sage: K = KirillovReshetikhinCrystal(['A',4,2], 1,1)
            sage: [K.to_ambient_crystal()(b) for b in K]
            [[], [[1, 1]], [[2, 2]], [[-2, -2]], [[-1, -1]]]
        """
        keys = self.highest_weight_dict().keys()
        pdict = dict( (self.highest_weight_dict()[key], self.ambient_highest_weight_dict()[key]) for key in keys )
        return self.crystal_morphism( pdict, index_set = self.cartan_type().classical().index_set(), 
                                      similarity_factor = self.similarity_factor() )

    def from_ambient_crystal(self):
        r"""
        Provides a map from the ambient crystal of type `C_n^{(1)}` to the Kirillov-Reshetikhin crystal self.
        Note that this map is only well-defined on elements that are in the image under `to_ambient_crystal`.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['D',4,2], 1,1)
            sage: b = K.ambient_crystal()(rows=[[3,-3]])
            sage: K.from_ambient_crystal()(b)
            [[0]]
            sage: K = KirillovReshetikhinCrystal(['A',4,2], 1,1)
            sage: b = K.ambient_crystal()(rows=[])
            sage: K.from_ambient_crystal()(b)
            []
        """
        keys = self.highest_weight_dict().keys()
        pdict_inv = dict( (self.ambient_highest_weight_dict()[key], self.highest_weight_dict()[key]) for key in keys )
        return self.crystal_morphism( pdict_inv, index_set = self.cartan_type().classical().index_set(), 
                                      similarity_factor_domain = self.similarity_factor() )


class KR_type_boxElement(AffineCrystalFromClassicalElement):
    r"""
    Class for the elements in the Kirillov-Reshetikhin crystals `B^{r,s}` of type `A_{2n}^{(2)}` for `r\le n`
    and type `D_{n+1}^{(2)}` for `r<n`.

    EXAMPLES::

        sage: K=KirillovReshetikhinCrystal(['A',4,2],1,2)
        sage: type(K.module_generators[0])
        <class 'sage.combinat.crystals.kirillov_reshetikhin.KR_type_box_with_category.element_class'>
    """

    def e0(self):
        r"""
        Gives `e_0` on self by mapping self to the ambient crystal, calculating `e_0` there and
        pulling the element back.

        EXAMPLES::

            sage: K=KirillovReshetikhinCrystal(['A',4,2],1,1)
            sage: b = K(rows=[])
            sage: b.e(0)
            [[-1]]
        """
        b = self.parent().to_ambient_crystal()(self).e(0)
        if b is None:
            return None
        return self.parent().from_ambient_crystal()(b)
    
    def f0(self):
        r"""
        Gives `f_0` on self by mapping self to the ambient crystal, calculating `f_0` there and
        pulling the element back.

        EXAMPLES::

            sage: K=KirillovReshetikhinCrystal(['A',4,2],1,1)
            sage: b = K(rows=[])
            sage: b.f(0)
            [[1]]
        """
        b = self.parent().to_ambient_crystal()(self).f(0)
        if b is None:
            return None
        return self.parent().from_ambient_crystal()(b)

    def epsilon0(self):
        r"""
        Calculates `\epsilon_0` of self by mapping the element to the ambient crystal
        and calculating `\epsilon_0` there.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['A',4,2], 1,1)
            sage: b=K(rows=[[1]])
            sage: b.epsilon(0)
            2
        """
        b = self.parent().to_ambient_crystal()(self)
        return b.epsilon(0)

    def phi0(self):
        r"""
        Calculates `\phi_0` of self by mapping the element to the ambient crystal
        and calculating `\phi_0` there.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['D',3,2], 1,1)
            sage: b=K(rows=[[-1]])
            sage: b.phi(0)
            2
        """
        b = self.parent().to_ambient_crystal()(self)
        return b.phi(0)

KR_type_box.Element = KR_type_boxElement


class KR_type_Bn(KirillovReshetikhinGenericCrystal, AffineCrystalFromClassical):
    r"""
    Class of Kirillov-Reshetikhin crystals `B^{n,s}` of type `B_{n}^{(1)}`.

    EXAMPLES::

        sage: K = KirillovReshetikhinCrystal(['B',3,1],3,2)
        sage: K
        Kirillov-Reshetikhin crystal of type ['B', 3, 1] with (r,s)=(3,2)
        sage: b = K(rows=[[1],[2],[3]])
        sage: b.f(0)
        sage: b.e(0)
        [[3]]

        sage: K = KirillovReshetikhinCrystal(['B',3,1],3,2)
        sage: [b.weight() for b in K if b.is_highest_weight([1,2,3])]
        [-Lambda[0] + Lambda[1], -2*Lambda[0] + 2*Lambda[3]]
        sage: [b.weight() for b in K if b.is_highest_weight([0,2,3])]
        [Lambda[0] - Lambda[1], -2*Lambda[1] + 2*Lambda[3]]
    """

    def __init__(self, cartan_type, r, s):
        r"""
        Initializes a Kirillov-Reshetikhin crystal ``self``.

        TESTS::

            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_Bn(['B',3,1], 3, 1)
            sage: K
            Kirillov-Reshetikhin crystal of type ['B', 3, 1] with (r,s)=(3,1)
            sage: TestSuite(K).run()
        """
        KirillovReshetikhinGenericCrystal.__init__(self, cartan_type, r ,s)
        AffineCrystalFromClassical.__init__(self, cartan_type, self.classical_decomposition())

    def classical_decomposition(self):
        r"""
        Specifies the classical crystal underlying the Kirillov-Reshetikhin crystal `B^{n,s}` of type `B_n^{(1)}`.
        It is the same as for `r<n`, given by `B^{n,s} \cong \oplus_\Lambda B(\Lambda)` where `\Lambda` are 
        weights obtained from a rectangle of width `s/2` and height `n` by removing horizontal dominoes. 
        Here we identify the fundamental weight `\Lambda_i` with a column of height `i` for `i<n` and 
        a column of width `1/2` for `i=n`.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['B',3,1], 3, 2)
            sage: K.classical_decomposition() 
            The crystal of tableaux of type ['B', 3] and shape(s) [[1], [1, 1, 1]]
            sage: K = KirillovReshetikhinCrystal(['B',3,1], 3, 3)
            sage: K.classical_decomposition()
            The crystal of tableaux of type ['B', 3] and shape(s) [[3/2, 1/2, 1/2], [3/2, 3/2, 3/2]]
        """
        s = self.s()
        r = self.r()
        shapes = vertical_dominoes_removed(r,floor(s/2))
        if is_odd(s):
            shapes = [ [i+QQ(1)/QQ(2) for i in sh]+[QQ(1)/QQ(2)]*(r-len(sh)) for sh in shapes ]
        return CrystalOfTableaux(self.cartan_type().classical(), shapes = shapes)

    def ambient_crystal(self):
        r"""
        Returns the ambient crystal `'B^{n,s}` of type `A_{2n-1}^{(2)}` associated to the Kirillov-Reshetikhin crystal;
        see Lemma 4.2 of reference [4].
        This ambient crystal is used to construct the zero arrows.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['B',3,1],3,2)
            sage: K.ambient_crystal()
            Kirillov-Reshetikhin crystal of type ['B', 3, 1]^* with (r,s)=(3,2)
        """
        return KirillovReshetikhinCrystal(['A', 2*self.cartan_type().classical().rank()-1,2], self.r(), self.s())

    def highest_weight_dict(self):
        r"""
        Gives a dictionary of the classical highest weight vectors of self.
        Their key is 2 times their shape.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['B',3,1],3,2)
            sage: K.highest_weight_dict()
            {(2,): [[1]], (2, 2, 2): [[1], [2], [3]]}
            sage: K = KirillovReshetikhinCrystal(['B',3,1],3,3)
            sage: K.highest_weight_dict()
            {(3, 3, 3): [+++, [[1], [2], [3]]], (3, 1, 1): [+++, [[1]]]}
        """
        return dict( (tuple([2*i[1] for i in x.classical_weight()]),x) for x in self.module_generators )

    def ambient_highest_weight_dict(self):
        r"""
        Gives a dictionary of the classical highest weight vectors of the ambient crystal of self.
        Their key is their shape.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['B',3,1],3,2)
            sage: K.ambient_highest_weight_dict()
            {(2,): [[1, 1]], (2, 1, 1): [[1, 1], [2], [3]], (2, 2, 2): [[1, 1], [2, 2], [3, 3]]}

            sage: K = KirillovReshetikhinCrystal(['B',3,1],3,3)
            sage: K.ambient_highest_weight_dict()
            {(3, 3, 3): [[1, 1, 1], [2, 2, 2], [3, 3, 3]], (3, 1, 1): [[1, 1, 1], [2], [3]], 
            (3, 2, 2): [[1, 1, 1], [2, 2], [3, 3]], (3,): [[1, 1, 1]]}
        """
        return dict( (tuple([i[1] for i in x.classical_weight()]),x) for x in self.ambient_crystal().module_generators )

    def similarity_factor(self):
        r"""
        Sets the similarity factor used to map to the ambient crystal.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['B',3,1],3,2)
            sage: K.similarity_factor()
            {1: 2, 2: 2, 3: 1}
        """    
        C = self.cartan_type().classical()
        p = dict( (i,2) for i in C.index_set() )
        p[C.rank()] = 1
        return p

    def to_ambient_crystal(self):
        r"""
        Provides a map from self to the ambient crystal of type `A_{2n-1}^{(2)}`.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['B',3,1],3,1)
            sage: [K.to_ambient_crystal()(b) for b in K]
            [[[1], [2], [3]], [[1], [2], [-3]], [[1], [3], [-2]], [[2], [3], [-1]], [[1], [-3], [-2]], 
            [[2], [-3], [-1]], [[3], [-2], [-1]], [[-3], [-2], [-1]]]
        """
        keys = self.highest_weight_dict().keys()
        pdict = dict( (self.highest_weight_dict()[key], self.ambient_highest_weight_dict()[key]) for key in keys )
        return self.crystal_morphism( pdict, index_set = self.cartan_type().classical().index_set(), 
                                      similarity_factor = self.similarity_factor() )

    def from_ambient_crystal(self):
        r"""
        Provides a map from the ambient crystal of type `A_{2n-1}^{(2)}` to the Kirillov-Reshetikhin crystal self.
        Note that this map is only well-defined on elements that are in the image under `to_ambient_crystal`.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['B',3,1],3,1)
            sage: [b == K.from_ambient_crystal()(K.to_ambient_crystal()(b)) for b in K]
            [True, True, True, True, True, True, True, True]
            sage: b = K.ambient_crystal()(rows=[[1],[2],[-3]])
            sage: K.from_ambient_crystal()(b)
            [++-, []]
        """
        keys = self.highest_weight_dict().keys()
        pdict_inv = dict( (self.ambient_highest_weight_dict()[key], self.highest_weight_dict()[key]) for key in keys )
        return self.crystal_morphism( pdict_inv, index_set = self.cartan_type().classical().index_set(), 
                                      similarity_factor_domain = self.similarity_factor() )


class KR_type_BnElement(AffineCrystalFromClassicalElement):
    r"""
    Class for the elements in the Kirillov-Reshetikhin crystals `B^{n,s}` of type `B_n^{(1)}`.

    EXAMPLES::

        sage: K=KirillovReshetikhinCrystal(['B',3,1],3,2)
        sage: type(K.module_generators[0])
        <class 'sage.combinat.crystals.kirillov_reshetikhin.KR_type_Bn_with_category.element_class'>
    """

    def e0(self):
        r"""
        Gives `e_0` on self by mapping self to the ambient crystal, calculating `e_0` there and
        pulling the element back.

        EXAMPLES::

            sage: K=KirillovReshetikhinCrystal(['B',3,1],3,1)
            sage: b = K.module_generators[0]
            sage: b.e(0)
            [--+, []]
        """
        b = self.parent().to_ambient_crystal()(self).e_string([0,0])
        if b is None:
            return None
        return self.parent().from_ambient_crystal()(b)
    
    def f0(self):
        r"""
        Gives `f_0` on self by mapping self to the ambient crystal, calculating `f_0` there and
        pulling the element back.

        EXAMPLES::

            sage: K=KirillovReshetikhinCrystal(['B',3,1],3,1)
            sage: b = K.module_generators[0]
            sage: b.f(0)

        """
        b = self.parent().to_ambient_crystal()(self).f_string([0,0])
        if b is None:
            return None
        return self.parent().from_ambient_crystal()(b)

    def epsilon0(self):
        r"""
        Calculates `\epsilon_0` of self by mapping the element to the ambient crystal
        and calculating `\epsilon_0` there.

        EXAMPLES::

            sage: K=KirillovReshetikhinCrystal(['B',3,1],3,1)
            sage: b = K.module_generators[0]
            sage: b.epsilon(0)
            1
        """
        b = self.parent().to_ambient_crystal()(self)
        return b.epsilon(0)/2

    def phi0(self):
        r"""
        Calculates `\phi_0` of self by mapping the element to the ambient crystal
        and calculating `\phi_0` there.

        EXAMPLES::

            sage: K=KirillovReshetikhinCrystal(['B',3,1],3,1)
            sage: b = K.module_generators[0]
            sage: b.phi(0)
            0
        """
        b = self.parent().to_ambient_crystal()(self)
        return b.phi(0)/2

KR_type_Bn.Element = KR_type_BnElement


class KR_type_Cn(KirillovReshetikhinGenericCrystal, AffineCrystalFromClassical):
    r"""
    Class of Kirillov-Reshetikhin crystals `B^{n,s}` of type `C_n^{(1)}`. 

    EXAMPLES::

        sage: K = KirillovReshetikhinCrystal(['C',3,1],3,1)
        sage: [[b,b.f(0)] for b in K]
        [[[[1], [2], [3]], None], [[[1], [2], [-3]], None], [[[1], [3], [-3]], None], 
        [[[2], [3], [-3]], None], [[[1], [3], [-2]], None], [[[2], [3], [-2]], None], 
        [[[2], [3], [-1]], [[1], [2], [3]]], [[[1], [-3], [-2]], None], [[[2], [-3], [-2]], None], 
        [[[2], [-3], [-1]], [[1], [2], [-3]]], [[[3], [-3], [-2]], None], [[[3], [-3], [-1]], 
        [[1], [3], [-3]]], [[[3], [-2], [-1]], [[1], [3], [-2]]], [[[-3], [-2], [-1]], [[1], [-3], [-2]]]]
    """

    def __init__(self, cartan_type, r, s):
        r"""
        Initializes a Kirillov-Reshetikhin crystal ``self``.

        TESTS::

            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_Cn(['C',3,1], 3, 1)
            sage: K
            Kirillov-Reshetikhin crystal of type ['C', 3, 1] with (r,s)=(3,1)
            sage: TestSuite(K).run()
        """
        KirillovReshetikhinGenericCrystal.__init__(self, cartan_type, r ,s)
        AffineCrystalFromClassical.__init__(self, cartan_type, self.classical_decomposition())
 
    def classical_decomposition(self):
        r"""
        Specifies the classical crystal underlying the Kirillov-Reshetikhin crystal `B^{n,s}`
        of type `C_n^{(1)}`. It is given by `B^{n,s} \cong B(s \Lambda_n)`.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['C',3,1],3,2)
            sage: K.classical_decomposition()
            The crystal of tableaux of type ['C', 3] and shape(s) [[2, 2, 2]]
        """
        return CrystalOfTableaux(self.cartan_type().classical(), shape = [self.s()]*self.r() )

    def from_highest_weight_vector_to_pm_diagram(self, b):
        """
        This gives the bijection between an element b in the classical decomposition
        of the KR crystal that is `{2,3,..,n}`-highest weight and `\pm` diagrams.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['C',3,1],3,2)
            sage: T = K.classical_decomposition()
            sage: b = T(rows=[[2, 2], [3, 3], [-3, -1]])
            sage: pm = K.from_highest_weight_vector_to_pm_diagram(b); pm
            [[0, 0], [1, 0], [0, 1], [0]]
            sage: pm.__repr__(pretty_printing=True)
            .  .
            .  +
            -  -

            sage: hw = [ b for b in T if all(b.epsilon(i)==0 for i in [2,3]) ]
            sage: all(K.from_pm_diagram_to_highest_weight_vector(K.from_highest_weight_vector_to_pm_diagram(b)) == b for b in hw)
            True
        """
        n = self.cartan_type().rank()-1
        inner = Partition([Integer(b.weight()[i]) for i in range(1,n+1)])
        inter = Partition([len([i for i in r if i>0]) for r in b.to_tableau()])
        outer = b.to_tableau().shape()
        return PMDiagram([self.r(), self.s(), outer, inter, inner], from_shapes=True)
 
    def from_pm_diagram_to_highest_weight_vector(self, pm):
        """
        This gives the bijection between a `\pm` diagram and an element b in the classical 
        decomposition of the KR crystal that is {2,3,..,n}-highest weight.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['C',3,1],3,2)
            sage: pm = sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[0, 0], [1, 0], [0, 1], [0]])
            sage: K.from_pm_diagram_to_highest_weight_vector(pm)
            [[2, 2], [3, 3], [-3, -1]]
        """
        u = [b for b in self.classical_decomposition().module_generators if b.to_tableau().shape() == pm.outer_shape()][0]
        ct = self.cartan_type()
        rank = ct.rank()-1
        ct_type = ct.classical().type()
        assert ct_type in ['C']
        list = []
        for h in pm.heights_of_addable_plus():
            list += range(1,h+1)
        for h in pm.heights_of_minus():
            list += range(1,rank+1)+[rank-1-k for k in range(rank-h)]
        for i in reversed(list):
            u = u.f(i)
        return u

class KR_type_CnElement(AffineCrystalFromClassicalElement):
    r"""
    Class for the elements in the Kirillov-Reshetikhin crystals `B^{n,s}` of type `C_n^{(1)}`.

    EXAMPLES::

        sage: K=KirillovReshetikhinCrystal(['C',3,1],3,2)
        sage: type(K.module_generators[0])
        <class 'sage.combinat.crystals.kirillov_reshetikhin.KR_type_Cn_with_category.element_class'>
    """

    def e0(self):
        r"""
        Gives `e_0` on self by going to the `\pm`-diagram corresponding to the `{2,...,n}`-highest weight 
        vector in the component of `self`, then applying [Definition 6.1, 4], and pulling back from
        `\pm`-diagrams.

        EXAMPLES::

            sage: K=KirillovReshetikhinCrystal(['C',3,1],3,2)
            sage: b = K.module_generators[0]
            sage: b.e(0)
            [[1, 2], [2, 3], [3, -1]]
            sage: b = K(rows=[[1,2],[2,3],[3,-1]])
            sage: b.e(0)
            [[2, 2], [3, 3], [-1, -1]]
            sage: b=K(rows=[[1, -3], [3, -2], [-3, -1]])
            sage: b.e(0)
            [[3, -3], [-3, -2], [-1, -1]]
        """
        n = self.parent().cartan_type().n
        [b,l] = self.lift().to_highest_weight(index_set=range(2,n+1))
        pm = self.parent().from_highest_weight_vector_to_pm_diagram(b)
        [l1,l2] = pm.pm_diagram[n-1]
        if l1 == 0:
            return None
        pm.pm_diagram[n-1] = [l1-1,l2+1]
        pm = PMDiagram(pm.pm_diagram)
        b = self.parent().from_pm_diagram_to_highest_weight_vector(pm)
        b = b.f_string(reversed(l))
        return self.parent().retract(b)
    
    def f0(self):
        r"""
        Gives `e_0` on self by going to the `\pm`-diagram corresponding to the `{2,...,n}`-highest weight 
        vector in the component of `self`, then applying [Definition 6.1, 4], and pulling back from
        `\pm`-diagrams.

        EXAMPLES::

            sage: K=KirillovReshetikhinCrystal(['C',3,1],3,1)
            sage: b = K.module_generators[0]
            sage: b.f(0)
        """
        n = self.parent().cartan_type().n
        [b,l] = self.lift().to_highest_weight(index_set=range(2,n+1))
        pm = self.parent().from_highest_weight_vector_to_pm_diagram(b)
        [l1,l2] = pm.pm_diagram[n-1]
        if l2 == 0:
            return None
        pm.pm_diagram[n-1] = [l1+1,l2-1]
        pm = PMDiagram(pm.pm_diagram)
        b = self.parent().from_pm_diagram_to_highest_weight_vector(pm)
        b = b.f_string(reversed(l))
        return self.parent().retract(b)

    def epsilon0(self):
        r"""
        Calculates `\epsilon_0` of self using Lemma 6.1 of [4].

        EXAMPLES::

            sage: K=KirillovReshetikhinCrystal(['C',3,1],3,1)
            sage: b = K.module_generators[0]
            sage: b.epsilon(0)
            1
        """
        n = self.parent().cartan_type().n
        b = self.lift().to_highest_weight(index_set=range(2,n+1))[0]
        pm = self.parent().from_highest_weight_vector_to_pm_diagram(b)
        [l1,l2] = pm.pm_diagram[n-1]
        return l1

    def phi0(self):
        r"""
        Calculates `\phi_0` of self.

        EXAMPLES::

            sage: K=KirillovReshetikhinCrystal(['C',3,1],3,1)
            sage: b = K.module_generators[0]
            sage: b.phi(0)
            0
        """
        n = self.parent().cartan_type().n
        b = self.lift().to_highest_weight(index_set=range(2,n+1))[0]
        pm = self.parent().from_highest_weight_vector_to_pm_diagram(b)
        [l1,l2] = pm.pm_diagram[n-1]
        return l2

KR_type_Cn.Element = KR_type_CnElement


class KR_type_Dn_twisted(KirillovReshetikhinGenericCrystal, AffineCrystalFromClassical):
    r"""
    Class of Kirillov-Reshetikhin crystals `B^{n,s}` of type `D_{n+1}^{(2)}`. 

    EXAMPLES::

        sage: K = KirillovReshetikhinCrystal(['D',4,2],3,1)
        sage: [[b,b.f(0)] for b in K]
        [[[+++, []], None], [[++-, []], None], [[+-+, []], None], [[-++, []], 
        [+++, []]], [[+--, []], None], [[-+-, []], [++-, []]], [[--+, []], [+-+, []]], 
        [[---, []], [+--, []]]]
    """

    def __init__(self, cartan_type, r, s):
        r"""
        Initializes a Kirillov-Reshetikhin crystal ``self``.

        TESTS::

            sage: K = sage.combinat.crystals.kirillov_reshetikhin.KR_type_Dn_twisted(['D',4,2], 3, 1)
            sage: K
            Kirillov-Reshetikhin crystal of type ['C', 3, 1]^* with (r,s)=(3,1)
            sage: TestSuite(K).run()
        """
        KirillovReshetikhinGenericCrystal.__init__(self, cartan_type, r ,s)
        AffineCrystalFromClassical.__init__(self, cartan_type, self.classical_decomposition())
 
    def classical_decomposition(self):
        r"""
        Specifies the classical crystal underlying the Kirillov-Reshetikhin crystal `B^{n,s}`
        of type `D_{n+1}^{(2)}`. It is given by `B^{n,s} \cong B(s \Lambda_n)`.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['D',4,2],3,1)
            sage: K.classical_decomposition()
            The crystal of tableaux of type ['B', 3] and shape(s) [[1/2, 1/2, 1/2]]
            sage: K = KirillovReshetikhinCrystal(['D',4,2],3,2)
            sage: K.classical_decomposition()
            The crystal of tableaux of type ['B', 3] and shape(s) [[1, 1, 1]]
        """
        s = self.s()
        if is_even(s):
            s = int(s/2)
        else:
            s = s/2
        return CrystalOfTableaux(self.cartan_type().classical(), shape = [s]*self.r() )

    def from_highest_weight_vector_to_pm_diagram(self, b):
        """
        This gives the bijection between an element b in the classical decomposition
        of the KR crystal that is `{2,3,..,n}`-highest weight and `\pm` diagrams.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['D',4,2],3,1)
            sage: T = K.classical_decomposition()
            sage: hw = [ b for b in T if all(b.epsilon(i)==0 for i in [2,3]) ]
            sage: [K.from_highest_weight_vector_to_pm_diagram(b) for b in hw]
            [[[0, 0], [0, 0], [1, 0], [0]], [[0, 0], [0, 0], [0, 1], [0]]]

            sage: K = KirillovReshetikhinCrystal(['D',4,2],3,2)
            sage: T = K.classical_decomposition()
            sage: hw = [ b for b in T if all(b.epsilon(i)==0 for i in [2,3]) ]
            sage: [K.from_highest_weight_vector_to_pm_diagram(b) for b in hw]
            [[[0, 0], [0, 0], [2, 0], [0]], [[0, 0], [0, 0], [0, 0], [2]], [[0, 0], [2, 0], [0, 0], [0]], 
            [[0, 0], [0, 0], [0, 2], [0]]]

        Note that, since the classical decomposition of this crystal is of type `B_n`, there can
        be (at most one) entry `0` in the `{2,3,...,n}`-highest weight elements at height `n`.
        In the following implementation this is realized as an empty column of height `n` since
        this uniquely specifies the existence of the `0`:

        EXAMPLES::

            sage: b = hw[1]
            sage: pm = K.from_highest_weight_vector_to_pm_diagram(b)
            sage: pm.__repr__(pretty_printing=True)
            .  .
            .  .
            .  .

        TESTS::

            sage: all(K.from_pm_diagram_to_highest_weight_vector(K.from_highest_weight_vector_to_pm_diagram(b)) == b for b in hw)
            True
            sage: K = KirillovReshetikhinCrystal(['D',4,2],3,2)
            sage: T = K.classical_decomposition()
            sage: hw = [ b for b in T if all(b.epsilon(i)==0 for i in [2,3]) ]
            sage: all(K.from_pm_diagram_to_highest_weight_vector(K.from_highest_weight_vector_to_pm_diagram(b)) == b for b in hw)
            True
            sage: K = KirillovReshetikhinCrystal(['D',4,2],3,3)
            sage: T = K.classical_decomposition()
            sage: hw = [ b for b in T if all(b.epsilon(i)==0 for i in [2,3]) ]
            sage: all(K.from_pm_diagram_to_highest_weight_vector(K.from_highest_weight_vector_to_pm_diagram(b)) == b for b in hw)
            True

        """
        n = self.cartan_type().rank()-1
        s = self.s()
        if is_odd(s):
            t = b[0]
            b = b[1]
        else:
            t = b.parent()(rows=[])
        inner = [Integer(2*b.weight()[i]+2*t.weight()[i]) for i in range(1,n+1)]
        inter1 = Partition([len([i for i in r if i>0]) for r in b.to_tableau()])
        inter = Partition([len([i for i in r if i>=0]) for r in b.to_tableau()])
        if inter != inter1:
            inner[n-1] += 2
        inner = Partition(inner)
        inter = [2*i for i in inter]+[0]*(n-len(inter))
        w = t.weight()
        if w[0]==0 and w[n-1]==0:
            v = [0]*n
        else:
            v = [1]*n
            if w[0]<0 and w[n-1]>0:
                v[n-1]=0
            elif w[0]>0 and w[n-1]<0:
                v[n-1]=0
                v[n-2]=-1
        inter = Partition([inter[i] + v[i] for i in range(n)])
        outer = Partition([s]*n)
        return PMDiagram([n, s, outer, inter, inner], from_shapes=True)
 
    def from_pm_diagram_to_highest_weight_vector(self, pm):
        """
        This gives the bijection between a `\pm` diagram and an element b in the classical 
        decomposition of the KR crystal that is {2,3,..,n}-highest weight.

        EXAMPLES::

            sage: K = KirillovReshetikhinCrystal(['D',4,2],3,2)
            sage: pm = sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[0, 0], [0, 0], [0, 0], [2]])
            sage: K.from_pm_diagram_to_highest_weight_vector(pm)
            [[2], [3], [0]]
        """
        u = self.classical_decomposition().module_generators[0]
        ct = self.cartan_type()
        rank = ct.rank()-1
        assert ct.classical().type() in ['B']
        list = []
        plus = pm.heights_of_addable_plus()
        minus = pm.heights_of_minus()
        l = len([i for i in plus if i==rank-1])
        a = (len(plus) + l)/2
        list += sum(([i]*a for i in range(1,rank+1)),[])
        a = (len(minus)-l)/2
        list += (range(1,rank+1)+[rank])*a
        for i in reversed(list):
            u = u.f(i)
        return u

class KR_type_Dn_twistedElement(AffineCrystalFromClassicalElement):
    r"""
    Class for the elements in the Kirillov-Reshetikhin crystals `B^{n,s}` of type `D_{n+1}^{(2)}`.

    EXAMPLES::

        sage: K=KirillovReshetikhinCrystal(['D',4,2],3,2)
        sage: type(K.module_generators[0])
        <class 'sage.combinat.crystals.kirillov_reshetikhin.KR_type_Dn_twisted_with_category.element_class'>
    """

    def e0(self):
        r"""
        Gives `e_0` on self by going to the `\pm`-diagram corresponding to the `{2,...,n}`-highest weight 
        vector in the component of `self`, then applying [Definition 6.2, 4], and pulling back from
        `\pm`-diagrams.

        EXAMPLES::

            sage: K=KirillovReshetikhinCrystal(['D',4,2],3,3)
            sage: b = K.module_generators[0]
            sage: b.e(0)
            [+++, [[2], [3], [0]]]
        """
        n = self.parent().cartan_type().rank()-1
        s = self.parent().s()
        [b,l] = self.lift().to_highest_weight(index_set=range(2,n+1))
        pm = self.parent().from_highest_weight_vector_to_pm_diagram(b)
        [l1,l2] = pm.pm_diagram[n-1]
        l3 = pm.pm_diagram[n-2][0]
        if l1+l2+l3==s and l1==0:
            return None
        if l1+l2+l3<s:
            pm.pm_diagram[n-1][1] = l2+2
            pm.pm_diagram[n][0] -= 2
        elif l1>1:
            pm.pm_diagram[n-1][0] = l1-2
            pm.pm_diagram[n][0] += 2
        elif l1 ==1:
            pm.pm_diagram[n-1][0] = 0
            pm.pm_diagram[n-1][1] = l2+1
        pm = PMDiagram(pm.pm_diagram)
        b = self.parent().from_pm_diagram_to_highest_weight_vector(pm)
        b = b.f_string(reversed(l))
        return self.parent().retract(b)
    
    def f0(self):
        r"""
        Gives `e_0` on self by going to the `\pm`-diagram corresponding to the `{2,...,n}`-highest weight 
        vector in the component of `self`, then applying [Definition 6.2, 4], and pulling back from
        `\pm`-diagrams.

        EXAMPLES::

            sage: K=KirillovReshetikhinCrystal(['D',4,2],3,2)
            sage: b = K.module_generators[0]
            sage: b.f(0)
        """
        n = self.parent().cartan_type().rank()-1
        s = self.parent().s()
        [b,l] = self.lift().to_highest_weight(index_set=range(2,n+1))
        pm = self.parent().from_highest_weight_vector_to_pm_diagram(b)
        [l1,l2] = pm.pm_diagram[n-1]
        l3 = pm.pm_diagram[n-2][0]
        if l1+l2+l3==s and l2==0:
            return None
        if l1+l2+l3<s:
            pm.pm_diagram[n-1][0] = l1+2
            pm.pm_diagram[n][0] -= 2
        elif l2>1:
            pm.pm_diagram[n-1][1] = l2-2
            pm.pm_diagram[n][0] += 2
        elif l2 ==1:
            pm.pm_diagram[n-1][1] = 0
            pm.pm_diagram[n-1][0] = l1+1
        pm = PMDiagram(pm.pm_diagram)
        b = self.parent().from_pm_diagram_to_highest_weight_vector(pm)
        b = b.f_string(reversed(l))
        return self.parent().retract(b)

    def epsilon0(self):
        r"""
        Calculates `\epsilon_0` of self using Lemma 6.2 of [4].

        EXAMPLES::

            sage: K=KirillovReshetikhinCrystal(['D',4,2],3,1)
            sage: b = K.module_generators[0]
            sage: b.epsilon(0)
            1
        """
        n = self.parent().cartan_type().rank()-1
        s = self.parent().s()
        [b,l] = self.lift().to_highest_weight(index_set=range(2,n+1))
        pm = self.parent().from_highest_weight_vector_to_pm_diagram(b)
        l1 = pm.pm_diagram[n-1][0]
        l4 = pm.pm_diagram[n][0]
        return l1+l4

    def phi0(self):
        r"""
        Calculates `\phi_0` of self.

        EXAMPLES::

            sage: K=KirillovReshetikhinCrystal(['D',4,2],3,1)
            sage: b = K.module_generators[0]
            sage: b.phi(0)
            0
        """
        n = self.parent().cartan_type().rank()-1
        s = self.parent().s()
        [b,l] = self.lift().to_highest_weight(index_set=range(2,n+1))
        pm = self.parent().from_highest_weight_vector_to_pm_diagram(b)
        l2 = pm.pm_diagram[n-1][1]
        l4 = pm.pm_diagram[n][0]
        return l2+l4

KR_type_Dn_twisted.Element = KR_type_Dn_twistedElement

#####################################################################

class PMDiagram(CombinatorialObject):
    """
    Class of `\pm` diagrams. These diagrams are in one-to-one bijection with `X_{n-1}` highest weight vectors
    in an `X_n` highest weight crystal `X=B,C,D`. See Section 4.1 of A. Schilling, "Combinatorial structure of 
    Kirillov-Reshetikhin crystals of type `D_n(1)`, `B_n(1)`, `A_{2n-1}(2)`", J. Algebra 319 (2008) 2938-2962 
    (arXiv:0704.2046[math.QA]). 

    The input is a list `pm = [[a_0,b_0],[a_1,b_1],...,[a_{n-1},b_{n-1}],[b_n]]` of 2-tuples and a last 1-tuple.
    The tuple `[a_i,b_i]` specifies the number of `a_i` + and `b_i` - in the i-th row of the pm diagram
    if `n-i` is odd and the number of `a_i` +- pairs above row `i` and `b_i` columns of height `i` not containing
    any + or - if `n-i` is even.

    Setting the option 'from_shapes = True' one can also input a `\pm` diagram in terms of its
    outer, intermediate and inner shape by specifying a tuple [n, s, outer, intermediate, inner]
    where `s` is the width of the `\pm` diagram, and 'outer' , 'intermediate',
    and 'inner' are the outer, intermediate and inner shape, respectively.
     
    EXAMPLES::

        sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[0,1],[1,2],[1]])
        sage: pm.pm_diagram
        [[0, 1], [1, 2], [1]]
        sage: pm._list
        [1, 1, 2, 0, 1]
        sage: pm.n
        2
        sage: pm.width
        5
        sage: pm.__repr__(pretty_printing=True)
        .  .  .  .
        .  +  -  -
        sage: sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([2,5,[4,4],[4,2],[4,1]], from_shapes=True)
        [[0, 1], [1, 2], [1]]

    TESTS::
        
        sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[1,2],[1,1],[1,1],[1,1],[1]])
        sage: sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([pm.n, pm.width, pm.outer_shape(), pm.intermediate_shape(), pm.inner_shape()], from_shapes=True) == pm
        True
        sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[1,2],[1,2],[1,1],[1,1],[1,1],[1]])
        sage: sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([pm.n, pm.width, pm.outer_shape(), pm.intermediate_shape(), pm.inner_shape()], from_shapes=True) == pm
        True
    """

    def __init__(self, pm_diagram, from_shapes = None):
        r"""
        Initializes `\pm` diagrams.

        TESTS::

           sage: sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[0,1],[1,2],[1]])
           [[0, 1], [1, 2], [1]]
           sage: sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([2,5,[4,4],[4,2],[4,1]], from_shapes=True)
           [[0, 1], [1, 2], [1]]
        """
        if from_shapes:
            n = pm_diagram[0]
            s = pm_diagram[1]
            outer = [s]+list(pm_diagram[2])+[0 for i in range(n)]
            intermediate = [s]+list(pm_diagram[3])+[0 for i in range(n)]
            inner = [s]+list(pm_diagram[4])+[0 for i in range(n)]
            pm = [[inner[n]]]
            for i in range(int((n+1)/2)):
                pm.append([intermediate[n-2*i]-inner[n-2*i], inner[n-2*i-1]-intermediate[n-2*i]])
                pm.append([outer[n-2*i]-inner[n-2*i-1], inner[n-2*i-2]-outer[n-2*i]])
            if is_odd(n):
                pm.pop(n+1)
            pm_diagram = list(reversed(pm))
        self.pm_diagram = pm_diagram
        self.n = len(pm_diagram)-1
        self._list = [i for a in reversed(pm_diagram) for i in a]
        self.width = sum(i for i in self._list)

    def __repr__(self, pretty_printing = None):
        """
        Turning on pretty printing allows to display the pm diagram as a
        tableau with the + and - displayed

        EXAMPLES::

            sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[1,0],[0,1],[2,0],[0,0],[0]])
            sage: pm.__repr__(pretty_printing=True)
            .  .  .  +
            .  .  -  -
            +  +
            -  -
            sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[0,2], [0,0], [0]])
            sage: pm.__repr__(pretty_printing=True)

        """
        if pretty_printing is None:
            return repr(self.pm_diagram)
        t = []
        ish = self.inner_shape() + [0]*self.n
        msh = self.intermediate_shape() + [0]*self.n
        osh = self.outer_shape() + [0]*self.n
        for i in range(self.n):
            t.append(['.']*ish[i]+['+']*(msh[i]-ish[i])+['-']*(osh[i]-msh[i]))
        t=[i for i in t if i!= []]
        return Tableau(t).pp()

    def inner_shape(self):
        """
        Returns the inner shape of the pm diagram

        EXAMPLES::
            sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[0,1],[1,2],[1]])
            sage: pm.inner_shape()
            [4, 1]
            sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[1,2],[1,1],[1,1],[1,1],[1]])
            sage: pm.inner_shape()
            [7, 5, 3, 1]
            sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[1,2],[1,2],[1,1],[1,1],[1,1],[1]])
            sage: pm.inner_shape()
            [10, 7, 5, 3, 1]
        """
        t = []
        ll = self._list
        for i in range(self.n):
            t.append(sum(ll[0:2*i+1]))
        return Partition(list(reversed(t)))

    def outer_shape(self):
        """
        Returns the outer shape of the pm diagram

        EXAMPLES::

            sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[0,1],[1,2],[1]])
            sage: pm.outer_shape()
            [4, 4]
            sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[1,2],[1,1],[1,1],[1,1],[1]])
            sage: pm.outer_shape()
            [8, 8, 4, 4]
            sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[1,2],[1,2],[1,1],[1,1],[1,1],[1]])
            sage: pm.outer_shape()
            [13, 8, 8, 4, 4]
        """
        t = []
        ll = self._list
        for i in range((self.n)/2):
            t.append(sum(ll[0:4*i+4]))
            t.append(sum(ll[0:4*i+4]))
        if is_even(self.n+1):
            t.append(sum(ll[0:2*self.n+2]))
        return Partition(list(reversed(t)))

    def intermediate_shape(self):
        """
        Returns the intermediate shape of the pm diagram (inner shape plus positions of plusses)

        EXAMPLES::

            sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[0,1],[1,2],[1]])
            sage: pm.intermediate_shape()
            [4, 2]
            sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[1,2],[1,1],[1,1],[1,1],[1]])
            sage: pm.intermediate_shape()
            [8, 6, 4, 2]
            sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[1,2],[1,2],[1,1],[1,1],[1,1],[1]])
            sage: pm.intermediate_shape()
            [11, 8, 6, 4, 2]
            sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[1,0],[0,1],[2,0],[0,0],[0]])
            sage: pm.intermediate_shape()
            [4, 2, 2]
            sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[1, 0], [0, 0], [0, 0], [0, 0], [0]])
            sage: pm.intermediate_shape()
            [1]
        """
        p = self.inner_shape()
        p = p + [0 for i in range(self.n)]
        ll = list(reversed(self._list))
        p = [ p[i]+ll[2*i+1] for i in range(self.n) ]
        return Partition(p)

    def heights_of_minus(self):
        """
        Returns a list with the heights of all minus in the `\pm` diagram.

        EXAMPLES::

            sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[1,2],[1,2],[1,1],[1,1],[1,1],[1]])
            sage: pm.heights_of_minus()
            [5, 5, 3, 3, 1, 1]
            sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[1,2],[1,1],[1,1],[1,1],[1]])
            sage: pm.heights_of_minus()
            [4, 4, 2, 2]
        """
        n = self.n
        heights = []
        for i in range(int((n+1)/2)):
            heights += [n-2*i]*((self.outer_shape()+[0]*n)[n-2*i-1]-(self.intermediate_shape()+[0]*n)[n-2*i-1])
        return heights

    def heights_of_addable_plus(self):
        """
        Returns a list with the heights of all addable plus in the `\pm` diagram.

        EXAMPLES::

            sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[1,2],[1,2],[1,1],[1,1],[1,1],[1]])
            sage: pm.heights_of_addable_plus()
            [1, 1, 2, 3, 4, 5]
            sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[1,2],[1,1],[1,1],[1,1],[1]])
            sage: pm.heights_of_addable_plus()
            [1, 2, 3, 4]
        """
        heights = []
        for i in range(1,self.n+1):
            heights += [i]*self.sigma().pm_diagram[i][0]
        return heights

    def sigma(self):
        """
        Returns sigma on pm diagrams as needed for the analogue of the Dynkin diagram automorphism
        that interchanges nodes `0` and `1` for type `D_n(1)`, `B_n(1)`, `A_{2n-1}(2)` for 
        Kirillov-Reshetikhin crystals.

        EXAMPLES::

            sage: pm=sage.combinat.crystals.kirillov_reshetikhin.PMDiagram([[0,1],[1,2],[1]])
            sage: pm.sigma().pm_diagram
            [[1, 0], [2, 1], [1]]
        """
        pm = self.pm_diagram
        return PMDiagram([list(reversed(a)) for a in pm])


def partitions_in_box(r, s):
    """
    Returns all partitions in a box of width s and height r.
    
    EXAMPLES::

        sage: sage.combinat.crystals.kirillov_reshetikhin.partitions_in_box(3,2)
        [[], [1], [2], [1, 1], [2, 1], [1, 1, 1], [2, 2], [2, 1, 1],
        [2, 2, 1], [2, 2, 2]]
    """
    return [x for n in range(r*s+1) for x in Partitions(n,max_part=s,max_length=r)]

def vertical_dominoes_removed(r, s):
    """
    Returns all partitions obtained from a rectangle of width s and height r by removing 
    vertical dominoes.

    EXAMPLES::

        sage: sage.combinat.crystals.kirillov_reshetikhin.vertical_dominoes_removed(2,2)
        [[], [1, 1], [2, 2]]
        sage: sage.combinat.crystals.kirillov_reshetikhin.vertical_dominoes_removed(3,2)
        [[2], [2, 1, 1], [2, 2, 2]]
        sage: sage.combinat.crystals.kirillov_reshetikhin.vertical_dominoes_removed(4,2)
        [[], [1, 1], [1, 1, 1, 1], [2, 2], [2, 2, 1, 1], [2, 2, 2, 2]]
    """
    return [x.conjugate() for x in horizontal_dominoes_removed(s,r)]

def horizontal_dominoes_removed(r, s):
    """
    Returns all partitions obtained from a rectangle of width s and height r by removing 
    horizontal dominoes.

    EXAMPLES::

        sage: sage.combinat.crystals.kirillov_reshetikhin.horizontal_dominoes_removed(2,2)
        [[], [2], [2, 2]]
        sage: sage.combinat.crystals.kirillov_reshetikhin.horizontal_dominoes_removed(3,2)
        [[], [2], [2, 2], [2, 2, 2]]
    """
    list = [ [y for y in x] + [0 for i in range(r-x.length())] for x in partitions_in_box(r, int(s/2)) ]
    two = lambda x : 2*(x-int(s/2)) + s
    return [Partition([two(y) for y in x]) for x in list]
