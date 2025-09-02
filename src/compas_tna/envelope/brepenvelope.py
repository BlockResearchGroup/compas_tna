from compas.geometry import Brep
from compas_tna.envelope import Envelope


class BrepEnvelope(Envelope):
    """An Envelope defined by a BRep at intrados, extrados, and middle."""

    def __init__(self, intrados: Brep = None, extrados: Brep = None, middle: Brep = None, **kwargs):
        super().__init__(**kwargs)
        self.intrados = intrados
        self.extrados = extrados
        self.middle = middle
