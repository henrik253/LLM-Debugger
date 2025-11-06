from enum import Enum 

class LayerType(Enum): 

    POSITIONAL_ENCODING = 'Positional Encoding Layer'
    MHSA = 'Multi-Head Self-Attention'
    ATTENTION_HEAD = 'Attention Head'
    FFN = 'Feed Forward'
    RESIDUAL = 'Skip Connection'
