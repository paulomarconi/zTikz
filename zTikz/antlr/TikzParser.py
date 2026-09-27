# Generated from TikzParser.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,54,324,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,
        2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,1,0,1,0,5,0,65,8,0,10,0,
        12,0,68,9,0,1,0,1,0,1,1,1,1,1,2,1,2,3,2,76,8,2,1,2,3,2,79,8,2,1,
        2,1,2,1,3,4,3,84,8,3,11,3,12,3,85,1,4,1,4,1,4,1,4,3,4,92,8,4,1,5,
        1,5,3,5,96,8,5,1,5,3,5,99,8,5,1,5,1,5,3,5,103,8,5,1,5,1,5,1,5,1,
        6,1,6,1,7,1,7,3,7,112,8,7,1,7,5,7,115,8,7,10,7,12,7,118,9,7,1,7,
        1,7,1,8,1,8,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,1,9,
        3,9,137,8,9,1,9,1,9,3,9,141,8,9,1,10,1,10,1,11,1,11,1,11,1,11,3,
        11,149,8,11,1,11,3,11,152,8,11,1,11,1,11,3,11,156,8,11,1,11,3,11,
        159,8,11,1,11,1,11,3,11,163,8,11,1,11,1,11,1,11,3,11,168,8,11,1,
        11,3,11,171,8,11,1,12,1,12,1,12,1,12,1,13,1,13,1,13,1,13,1,13,1,
        13,1,14,1,14,3,14,185,8,14,1,14,1,14,1,14,1,14,1,15,1,15,1,15,1,
        15,1,15,1,15,1,15,3,15,198,8,15,1,16,1,16,1,16,1,16,1,16,3,16,205,
        8,16,1,16,1,16,1,17,1,17,3,17,211,8,17,1,17,3,17,214,8,17,1,17,1,
        17,3,17,218,8,17,1,17,1,17,1,18,1,18,1,18,1,18,1,19,1,19,5,19,228,
        8,19,10,19,12,19,231,9,19,1,19,1,19,1,20,1,20,1,20,5,20,238,8,20,
        10,20,12,20,241,9,20,1,20,3,20,244,8,20,1,21,1,21,1,22,1,22,1,22,
        1,22,1,22,1,22,1,22,1,22,1,22,1,22,1,22,1,22,1,22,1,22,1,22,3,22,
        263,8,22,1,23,1,23,1,23,1,23,1,23,1,23,1,23,1,23,1,23,3,23,274,8,
        23,1,24,1,24,3,24,278,8,24,1,25,1,25,1,26,1,26,3,26,284,8,26,1,26,
        1,26,1,27,1,27,1,27,5,27,291,8,27,10,27,12,27,294,9,27,1,27,3,27,
        297,8,27,1,28,1,28,1,28,3,28,302,8,28,1,29,1,29,5,29,306,8,29,10,
        29,12,29,309,9,29,1,29,1,29,1,30,1,30,1,30,1,30,3,30,317,8,30,1,
        30,4,30,320,8,30,11,30,12,30,321,1,30,0,0,31,0,2,4,6,8,10,12,14,
        16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,
        60,0,4,3,0,25,34,38,41,44,44,1,0,3,11,4,0,29,29,31,32,39,41,44,44,
        1,0,25,28,350,0,66,1,0,0,0,2,71,1,0,0,0,4,73,1,0,0,0,6,83,1,0,0,
        0,8,91,1,0,0,0,10,93,1,0,0,0,12,107,1,0,0,0,14,109,1,0,0,0,16,121,
        1,0,0,0,18,140,1,0,0,0,20,142,1,0,0,0,22,170,1,0,0,0,24,172,1,0,
        0,0,26,176,1,0,0,0,28,182,1,0,0,0,30,190,1,0,0,0,32,199,1,0,0,0,
        34,208,1,0,0,0,36,221,1,0,0,0,38,225,1,0,0,0,40,243,1,0,0,0,42,245,
        1,0,0,0,44,262,1,0,0,0,46,273,1,0,0,0,48,275,1,0,0,0,50,279,1,0,
        0,0,52,281,1,0,0,0,54,287,1,0,0,0,56,298,1,0,0,0,58,303,1,0,0,0,
        60,319,1,0,0,0,62,65,3,4,2,0,63,65,3,2,1,0,64,62,1,0,0,0,64,63,1,
        0,0,0,65,68,1,0,0,0,66,64,1,0,0,0,66,67,1,0,0,0,67,69,1,0,0,0,68,
        66,1,0,0,0,69,70,5,0,0,1,70,1,1,0,0,0,71,72,7,0,0,0,72,3,1,0,0,0,
        73,75,5,1,0,0,74,76,3,52,26,0,75,74,1,0,0,0,75,76,1,0,0,0,76,78,
        1,0,0,0,77,79,3,6,3,0,78,77,1,0,0,0,78,79,1,0,0,0,79,80,1,0,0,0,
        80,81,5,2,0,0,81,5,1,0,0,0,82,84,3,8,4,0,83,82,1,0,0,0,84,85,1,0,
        0,0,85,83,1,0,0,0,85,86,1,0,0,0,86,7,1,0,0,0,87,92,3,10,5,0,88,92,
        3,14,7,0,89,92,3,52,26,0,90,92,3,12,6,0,91,87,1,0,0,0,91,88,1,0,
        0,0,91,89,1,0,0,0,91,90,1,0,0,0,92,9,1,0,0,0,93,95,5,7,0,0,94,96,
        3,52,26,0,95,94,1,0,0,0,95,96,1,0,0,0,96,98,1,0,0,0,97,99,3,36,18,
        0,98,97,1,0,0,0,98,99,1,0,0,0,99,102,1,0,0,0,100,101,5,21,0,0,101,
        103,3,44,22,0,102,100,1,0,0,0,102,103,1,0,0,0,103,104,1,0,0,0,104,
        105,3,38,19,0,105,106,5,30,0,0,106,11,1,0,0,0,107,108,7,0,0,0,108,
        13,1,0,0,0,109,111,3,16,8,0,110,112,3,52,26,0,111,110,1,0,0,0,111,
        112,1,0,0,0,112,116,1,0,0,0,113,115,3,18,9,0,114,113,1,0,0,0,115,
        118,1,0,0,0,116,114,1,0,0,0,116,117,1,0,0,0,117,119,1,0,0,0,118,
        116,1,0,0,0,119,120,5,30,0,0,120,15,1,0,0,0,121,122,7,1,0,0,122,
        17,1,0,0,0,123,141,3,44,22,0,124,141,3,22,11,0,125,141,3,28,14,0,
        126,141,3,32,16,0,127,141,3,34,17,0,128,141,3,38,19,0,129,141,3,
        42,21,0,130,141,3,52,26,0,131,141,5,22,0,0,132,133,5,21,0,0,133,
        141,3,44,22,0,134,136,5,23,0,0,135,137,3,52,26,0,136,135,1,0,0,0,
        136,137,1,0,0,0,137,138,1,0,0,0,138,141,5,24,0,0,139,141,3,20,10,
        0,140,123,1,0,0,0,140,124,1,0,0,0,140,125,1,0,0,0,140,126,1,0,0,
        0,140,127,1,0,0,0,140,128,1,0,0,0,140,129,1,0,0,0,140,130,1,0,0,
        0,140,131,1,0,0,0,140,132,1,0,0,0,140,134,1,0,0,0,140,139,1,0,0,
        0,141,19,1,0,0,0,142,143,7,2,0,0,143,21,1,0,0,0,144,145,5,12,0,0,
        145,171,3,44,22,0,146,148,5,13,0,0,147,149,3,52,26,0,148,147,1,0,
        0,0,148,149,1,0,0,0,149,151,1,0,0,0,150,152,3,24,12,0,151,150,1,
        0,0,0,151,152,1,0,0,0,152,171,1,0,0,0,153,155,5,14,0,0,154,156,3,
        52,26,0,155,154,1,0,0,0,155,156,1,0,0,0,156,158,1,0,0,0,157,159,
        3,26,13,0,158,157,1,0,0,0,158,159,1,0,0,0,159,171,1,0,0,0,160,162,
        5,15,0,0,161,163,3,52,26,0,162,161,1,0,0,0,162,163,1,0,0,0,163,164,
        1,0,0,0,164,171,3,44,22,0,165,167,5,16,0,0,166,168,3,52,26,0,167,
        166,1,0,0,0,167,168,1,0,0,0,168,169,1,0,0,0,169,171,3,44,22,0,170,
        144,1,0,0,0,170,146,1,0,0,0,170,153,1,0,0,0,170,160,1,0,0,0,170,
        165,1,0,0,0,171,23,1,0,0,0,172,173,5,33,0,0,173,174,3,48,24,0,174,
        175,5,34,0,0,175,25,1,0,0,0,176,177,5,33,0,0,177,178,3,48,24,0,178,
        179,5,19,0,0,179,180,3,48,24,0,180,181,5,34,0,0,181,27,1,0,0,0,182,
        184,5,17,0,0,183,185,3,52,26,0,184,183,1,0,0,0,184,185,1,0,0,0,185,
        186,1,0,0,0,186,187,5,33,0,0,187,188,3,30,15,0,188,189,5,34,0,0,
        189,29,1,0,0,0,190,191,3,48,24,0,191,192,5,31,0,0,192,193,3,48,24,
        0,193,194,5,31,0,0,194,197,3,48,24,0,195,196,5,19,0,0,196,198,3,
        48,24,0,197,195,1,0,0,0,197,198,1,0,0,0,198,31,1,0,0,0,199,200,5,
        29,0,0,200,201,5,18,0,0,201,204,3,44,22,0,202,203,5,19,0,0,203,205,
        3,44,22,0,204,202,1,0,0,0,204,205,1,0,0,0,205,206,1,0,0,0,206,207,
        5,29,0,0,207,33,1,0,0,0,208,210,5,20,0,0,209,211,3,52,26,0,210,209,
        1,0,0,0,210,211,1,0,0,0,211,213,1,0,0,0,212,214,3,36,18,0,213,212,
        1,0,0,0,213,214,1,0,0,0,214,217,1,0,0,0,215,216,5,21,0,0,216,218,
        3,44,22,0,217,215,1,0,0,0,217,218,1,0,0,0,218,219,1,0,0,0,219,220,
        3,38,19,0,220,35,1,0,0,0,221,222,5,33,0,0,222,223,5,40,0,0,223,224,
        5,34,0,0,224,37,1,0,0,0,225,229,5,37,0,0,226,228,3,40,20,0,227,226,
        1,0,0,0,228,231,1,0,0,0,229,227,1,0,0,0,229,230,1,0,0,0,230,232,
        1,0,0,0,231,229,1,0,0,0,232,233,5,53,0,0,233,39,1,0,0,0,234,244,
        5,54,0,0,235,239,5,52,0,0,236,238,3,40,20,0,237,236,1,0,0,0,238,
        241,1,0,0,0,239,237,1,0,0,0,239,240,1,0,0,0,240,242,1,0,0,0,241,
        239,1,0,0,0,242,244,5,53,0,0,243,234,1,0,0,0,243,235,1,0,0,0,244,
        41,1,0,0,0,245,246,7,3,0,0,246,43,1,0,0,0,247,248,5,33,0,0,248,249,
        3,46,23,0,249,250,5,34,0,0,250,263,1,0,0,0,251,252,5,35,0,0,252,
        253,5,35,0,0,253,254,5,33,0,0,254,255,3,46,23,0,255,256,5,34,0,0,
        256,263,1,0,0,0,257,258,5,35,0,0,258,259,5,33,0,0,259,260,3,46,23,
        0,260,261,5,34,0,0,261,263,1,0,0,0,262,247,1,0,0,0,262,251,1,0,0,
        0,262,257,1,0,0,0,263,45,1,0,0,0,264,265,3,48,24,0,265,266,5,32,
        0,0,266,267,3,48,24,0,267,274,1,0,0,0,268,269,3,48,24,0,269,270,
        5,31,0,0,270,271,3,48,24,0,271,274,1,0,0,0,272,274,5,40,0,0,273,
        264,1,0,0,0,273,268,1,0,0,0,273,272,1,0,0,0,274,47,1,0,0,0,275,277,
        5,39,0,0,276,278,3,50,25,0,277,276,1,0,0,0,277,278,1,0,0,0,278,49,
        1,0,0,0,279,280,5,40,0,0,280,51,1,0,0,0,281,283,5,36,0,0,282,284,
        3,54,27,0,283,282,1,0,0,0,283,284,1,0,0,0,284,285,1,0,0,0,285,286,
        5,46,0,0,286,53,1,0,0,0,287,292,3,56,28,0,288,289,5,49,0,0,289,291,
        3,56,28,0,290,288,1,0,0,0,291,294,1,0,0,0,292,290,1,0,0,0,292,293,
        1,0,0,0,293,296,1,0,0,0,294,292,1,0,0,0,295,297,5,49,0,0,296,295,
        1,0,0,0,296,297,1,0,0,0,297,55,1,0,0,0,298,301,3,60,30,0,299,300,
        5,48,0,0,300,302,3,60,30,0,301,299,1,0,0,0,301,302,1,0,0,0,302,57,
        1,0,0,0,303,307,5,47,0,0,304,306,3,40,20,0,305,304,1,0,0,0,306,309,
        1,0,0,0,307,305,1,0,0,0,307,308,1,0,0,0,308,310,1,0,0,0,309,307,
        1,0,0,0,310,311,5,53,0,0,311,59,1,0,0,0,312,320,5,51,0,0,313,320,
        3,58,29,0,314,316,5,45,0,0,315,317,3,54,27,0,316,315,1,0,0,0,316,
        317,1,0,0,0,317,318,1,0,0,0,318,320,5,46,0,0,319,312,1,0,0,0,319,
        313,1,0,0,0,319,314,1,0,0,0,320,321,1,0,0,0,321,319,1,0,0,0,321,
        322,1,0,0,0,322,61,1,0,0,0,40,64,66,75,78,85,91,95,98,102,111,116,
        136,140,148,151,155,158,162,167,170,184,197,204,210,213,217,229,
        239,243,262,273,277,283,292,296,301,307,316,319,321
    ]

class TikzParser ( Parser ):

    grammarFileName = "TikzParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'\\begin{tikzpicture}'", "'\\end{tikzpicture}'", 
                     "'\\draw'", "'\\fill'", "'\\path'", "'\\clip'", "'\\node'", 
                     "'\\filldraw'", "'\\pattern'", "'\\shade'", "'\\shadedraw'", 
                     "'rectangle'", "'circle'", "'ellipse'", "'grid'", "'parabola'", 
                     "'arc'", "'controls'", "'and'", "'node'", "'at'", "'cycle'", 
                     "'plot'", "'coordinates'", "'--'", "'->'", "'|-'", 
                     "'-|'", "'..'", "';'", "':'", "<INVALID>", "'('", "')'", 
                     "'+'", "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                     "<INVALID>", "<INVALID>", "']'", "<INVALID>", "'='" ]

    symbolicNames = [ "<INVALID>", "BEGIN_TIKZ", "END_TIKZ", "DRAW", "FILL", 
                      "PATHCMD", "CLIP", "NODE_CMD", "FILLDRAW", "PATTERN", 
                      "SHADE", "SHADEDRAW", "RECTANGLE", "CIRCLE", "ELLIPSE", 
                      "GRID", "PARABOLA", "ARC", "CONTROLS", "AND", "NODE", 
                      "AT", "CYCLE", "PLOT", "COORDINATES", "DASH_DASH", 
                      "DASH_ARROW", "PIPE_DASH", "DASH_PIPE", "DOT_DOT", 
                      "SEMI", "COLON", "COMMA", "LPAREN", "RPAREN", "PLUS", 
                      "LBRACK", "LBRACE", "RBRACE", "NUMBER", "ID", "COMMAND", 
                      "WS", "COMMENT", "ANY", "OPT_LBRACK", "OPT_RBRACK", 
                      "OPT_LBRACE", "OPT_EQ", "OPT_COMMA", "OPT_WS", "OPT_TEXT", 
                      "BRACE_LBRACE", "BRACE_RBRACE", "BRACE_CONTENT" ]

    RULE_document = 0
    RULE_skip_token = 1
    RULE_tikzpicture = 2
    RULE_tikzbody = 3
    RULE_tikz_stmt = 4
    RULE_standalone_node = 5
    RULE_skip_body = 6
    RULE_path_cmd = 7
    RULE_path_start = 8
    RULE_path_element = 9
    RULE_path_skip_token = 10
    RULE_shape_spec = 11
    RULE_circle_size = 12
    RULE_ellipse_size = 13
    RULE_arc_spec = 14
    RULE_arc_params = 15
    RULE_control_spec = 16
    RULE_node_inline = 17
    RULE_node_name = 18
    RULE_brace_text = 19
    RULE_brace_item = 20
    RULE_edge_op = 21
    RULE_coordinate = 22
    RULE_coord_value = 23
    RULE_numberunit = 24
    RULE_unit = 25
    RULE_tikz_options = 26
    RULE_option_list = 27
    RULE_option_item = 28
    RULE_opt_brace_text = 29
    RULE_option_atom = 30

    ruleNames =  [ "document", "skip_token", "tikzpicture", "tikzbody", 
                   "tikz_stmt", "standalone_node", "skip_body", "path_cmd", 
                   "path_start", "path_element", "path_skip_token", "shape_spec", 
                   "circle_size", "ellipse_size", "arc_spec", "arc_params", 
                   "control_spec", "node_inline", "node_name", "brace_text", 
                   "brace_item", "edge_op", "coordinate", "coord_value", 
                   "numberunit", "unit", "tikz_options", "option_list", 
                   "option_item", "opt_brace_text", "option_atom" ]

    EOF = Token.EOF
    BEGIN_TIKZ=1
    END_TIKZ=2
    DRAW=3
    FILL=4
    PATHCMD=5
    CLIP=6
    NODE_CMD=7
    FILLDRAW=8
    PATTERN=9
    SHADE=10
    SHADEDRAW=11
    RECTANGLE=12
    CIRCLE=13
    ELLIPSE=14
    GRID=15
    PARABOLA=16
    ARC=17
    CONTROLS=18
    AND=19
    NODE=20
    AT=21
    CYCLE=22
    PLOT=23
    COORDINATES=24
    DASH_DASH=25
    DASH_ARROW=26
    PIPE_DASH=27
    DASH_PIPE=28
    DOT_DOT=29
    SEMI=30
    COLON=31
    COMMA=32
    LPAREN=33
    RPAREN=34
    PLUS=35
    LBRACK=36
    LBRACE=37
    RBRACE=38
    NUMBER=39
    ID=40
    COMMAND=41
    WS=42
    COMMENT=43
    ANY=44
    OPT_LBRACK=45
    OPT_RBRACK=46
    OPT_LBRACE=47
    OPT_EQ=48
    OPT_COMMA=49
    OPT_WS=50
    OPT_TEXT=51
    BRACE_LBRACE=52
    BRACE_RBRACE=53
    BRACE_CONTENT=54

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class DocumentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(TikzParser.EOF, 0)

        def tikzpicture(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TikzParser.TikzpictureContext)
            else:
                return self.getTypedRuleContext(TikzParser.TikzpictureContext,i)


        def skip_token(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TikzParser.Skip_tokenContext)
            else:
                return self.getTypedRuleContext(TikzParser.Skip_tokenContext,i)


        def getRuleIndex(self):
            return TikzParser.RULE_document

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDocument" ):
                listener.enterDocument(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDocument" ):
                listener.exitDocument(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDocument" ):
                return visitor.visitDocument(self)
            else:
                return visitor.visitChildren(self)




    def document(self):

        localctx = TikzParser.DocumentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_document)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 66
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 21749680832514) != 0):
                self.state = 64
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [1]:
                    self.state = 62
                    self.tikzpicture()
                    pass
                elif token in [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 38, 39, 40, 41, 44]:
                    self.state = 63
                    self.skip_token()
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 68
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 69
            self.match(TikzParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Skip_tokenContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ANY(self):
            return self.getToken(TikzParser.ANY, 0)

        def NUMBER(self):
            return self.getToken(TikzParser.NUMBER, 0)

        def ID(self):
            return self.getToken(TikzParser.ID, 0)

        def SEMI(self):
            return self.getToken(TikzParser.SEMI, 0)

        def COLON(self):
            return self.getToken(TikzParser.COLON, 0)

        def COMMA(self):
            return self.getToken(TikzParser.COMMA, 0)

        def DASH_DASH(self):
            return self.getToken(TikzParser.DASH_DASH, 0)

        def DASH_ARROW(self):
            return self.getToken(TikzParser.DASH_ARROW, 0)

        def PIPE_DASH(self):
            return self.getToken(TikzParser.PIPE_DASH, 0)

        def DASH_PIPE(self):
            return self.getToken(TikzParser.DASH_PIPE, 0)

        def DOT_DOT(self):
            return self.getToken(TikzParser.DOT_DOT, 0)

        def LPAREN(self):
            return self.getToken(TikzParser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(TikzParser.RPAREN, 0)

        def RBRACE(self):
            return self.getToken(TikzParser.RBRACE, 0)

        def COMMAND(self):
            return self.getToken(TikzParser.COMMAND, 0)

        def getRuleIndex(self):
            return TikzParser.RULE_skip_token

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSkip_token" ):
                listener.enterSkip_token(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSkip_token" ):
                listener.exitSkip_token(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSkip_token" ):
                return visitor.visitSkip_token(self)
            else:
                return visitor.visitChildren(self)




    def skip_token(self):

        localctx = TikzParser.Skip_tokenContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_skip_token)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 71
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 21749680832512) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TikzpictureContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def BEGIN_TIKZ(self):
            return self.getToken(TikzParser.BEGIN_TIKZ, 0)

        def END_TIKZ(self):
            return self.getToken(TikzParser.END_TIKZ, 0)

        def tikz_options(self):
            return self.getTypedRuleContext(TikzParser.Tikz_optionsContext,0)


        def tikzbody(self):
            return self.getTypedRuleContext(TikzParser.TikzbodyContext,0)


        def getRuleIndex(self):
            return TikzParser.RULE_tikzpicture

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTikzpicture" ):
                listener.enterTikzpicture(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTikzpicture" ):
                listener.exitTikzpicture(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTikzpicture" ):
                return visitor.visitTikzpicture(self)
            else:
                return visitor.visitChildren(self)




    def tikzpicture(self):

        localctx = TikzParser.TikzpictureContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_tikzpicture)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 73
            self.match(TikzParser.BEGIN_TIKZ)
            self.state = 75
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,2,self._ctx)
            if la_ == 1:
                self.state = 74
                self.tikz_options()


            self.state = 78
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 21818400313336) != 0):
                self.state = 77
                self.tikzbody()


            self.state = 80
            self.match(TikzParser.END_TIKZ)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TikzbodyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def tikz_stmt(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TikzParser.Tikz_stmtContext)
            else:
                return self.getTypedRuleContext(TikzParser.Tikz_stmtContext,i)


        def getRuleIndex(self):
            return TikzParser.RULE_tikzbody

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTikzbody" ):
                listener.enterTikzbody(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTikzbody" ):
                listener.exitTikzbody(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTikzbody" ):
                return visitor.visitTikzbody(self)
            else:
                return visitor.visitChildren(self)




    def tikzbody(self):

        localctx = TikzParser.TikzbodyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_tikzbody)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 83 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 82
                self.tikz_stmt()
                self.state = 85 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 21818400313336) != 0)):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Tikz_stmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def standalone_node(self):
            return self.getTypedRuleContext(TikzParser.Standalone_nodeContext,0)


        def path_cmd(self):
            return self.getTypedRuleContext(TikzParser.Path_cmdContext,0)


        def tikz_options(self):
            return self.getTypedRuleContext(TikzParser.Tikz_optionsContext,0)


        def skip_body(self):
            return self.getTypedRuleContext(TikzParser.Skip_bodyContext,0)


        def getRuleIndex(self):
            return TikzParser.RULE_tikz_stmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTikz_stmt" ):
                listener.enterTikz_stmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTikz_stmt" ):
                listener.exitTikz_stmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTikz_stmt" ):
                return visitor.visitTikz_stmt(self)
            else:
                return visitor.visitChildren(self)




    def tikz_stmt(self):

        localctx = TikzParser.Tikz_stmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_tikz_stmt)
        try:
            self.state = 91
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,5,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 87
                self.standalone_node()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 88
                self.path_cmd()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 89
                self.tikz_options()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 90
                self.skip_body()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Standalone_nodeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NODE_CMD(self):
            return self.getToken(TikzParser.NODE_CMD, 0)

        def brace_text(self):
            return self.getTypedRuleContext(TikzParser.Brace_textContext,0)


        def SEMI(self):
            return self.getToken(TikzParser.SEMI, 0)

        def tikz_options(self):
            return self.getTypedRuleContext(TikzParser.Tikz_optionsContext,0)


        def node_name(self):
            return self.getTypedRuleContext(TikzParser.Node_nameContext,0)


        def AT(self):
            return self.getToken(TikzParser.AT, 0)

        def coordinate(self):
            return self.getTypedRuleContext(TikzParser.CoordinateContext,0)


        def getRuleIndex(self):
            return TikzParser.RULE_standalone_node

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStandalone_node" ):
                listener.enterStandalone_node(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStandalone_node" ):
                listener.exitStandalone_node(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStandalone_node" ):
                return visitor.visitStandalone_node(self)
            else:
                return visitor.visitChildren(self)




    def standalone_node(self):

        localctx = TikzParser.Standalone_nodeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_standalone_node)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 93
            self.match(TikzParser.NODE_CMD)
            self.state = 95
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==36:
                self.state = 94
                self.tikz_options()


            self.state = 98
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==33:
                self.state = 97
                self.node_name()


            self.state = 102
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==21:
                self.state = 100
                self.match(TikzParser.AT)
                self.state = 101
                self.coordinate()


            self.state = 104
            self.brace_text()
            self.state = 105
            self.match(TikzParser.SEMI)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Skip_bodyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ANY(self):
            return self.getToken(TikzParser.ANY, 0)

        def NUMBER(self):
            return self.getToken(TikzParser.NUMBER, 0)

        def ID(self):
            return self.getToken(TikzParser.ID, 0)

        def SEMI(self):
            return self.getToken(TikzParser.SEMI, 0)

        def COLON(self):
            return self.getToken(TikzParser.COLON, 0)

        def COMMA(self):
            return self.getToken(TikzParser.COMMA, 0)

        def DASH_DASH(self):
            return self.getToken(TikzParser.DASH_DASH, 0)

        def DASH_ARROW(self):
            return self.getToken(TikzParser.DASH_ARROW, 0)

        def PIPE_DASH(self):
            return self.getToken(TikzParser.PIPE_DASH, 0)

        def DASH_PIPE(self):
            return self.getToken(TikzParser.DASH_PIPE, 0)

        def DOT_DOT(self):
            return self.getToken(TikzParser.DOT_DOT, 0)

        def LPAREN(self):
            return self.getToken(TikzParser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(TikzParser.RPAREN, 0)

        def RBRACE(self):
            return self.getToken(TikzParser.RBRACE, 0)

        def COMMAND(self):
            return self.getToken(TikzParser.COMMAND, 0)

        def getRuleIndex(self):
            return TikzParser.RULE_skip_body

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSkip_body" ):
                listener.enterSkip_body(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSkip_body" ):
                listener.exitSkip_body(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitSkip_body" ):
                return visitor.visitSkip_body(self)
            else:
                return visitor.visitChildren(self)




    def skip_body(self):

        localctx = TikzParser.Skip_bodyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_skip_body)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 107
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 21749680832512) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Path_cmdContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def path_start(self):
            return self.getTypedRuleContext(TikzParser.Path_startContext,0)


        def SEMI(self):
            return self.getToken(TikzParser.SEMI, 0)

        def tikz_options(self):
            return self.getTypedRuleContext(TikzParser.Tikz_optionsContext,0)


        def path_element(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TikzParser.Path_elementContext)
            else:
                return self.getTypedRuleContext(TikzParser.Path_elementContext,i)


        def getRuleIndex(self):
            return TikzParser.RULE_path_cmd

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPath_cmd" ):
                listener.enterPath_cmd(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPath_cmd" ):
                listener.exitPath_cmd(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPath_cmd" ):
                return visitor.visitPath_cmd(self)
            else:
                return visitor.visitChildren(self)




    def path_cmd(self):

        localctx = TikzParser.Path_cmdContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_path_cmd)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 109
            self.path_start()
            self.state = 111
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,9,self._ctx)
            if la_ == 1:
                self.state = 110
                self.tikz_options()


            self.state = 116
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 21697083469824) != 0):
                self.state = 113
                self.path_element()
                self.state = 118
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 119
            self.match(TikzParser.SEMI)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Path_startContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DRAW(self):
            return self.getToken(TikzParser.DRAW, 0)

        def FILL(self):
            return self.getToken(TikzParser.FILL, 0)

        def PATHCMD(self):
            return self.getToken(TikzParser.PATHCMD, 0)

        def CLIP(self):
            return self.getToken(TikzParser.CLIP, 0)

        def NODE_CMD(self):
            return self.getToken(TikzParser.NODE_CMD, 0)

        def FILLDRAW(self):
            return self.getToken(TikzParser.FILLDRAW, 0)

        def PATTERN(self):
            return self.getToken(TikzParser.PATTERN, 0)

        def SHADE(self):
            return self.getToken(TikzParser.SHADE, 0)

        def SHADEDRAW(self):
            return self.getToken(TikzParser.SHADEDRAW, 0)

        def getRuleIndex(self):
            return TikzParser.RULE_path_start

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPath_start" ):
                listener.enterPath_start(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPath_start" ):
                listener.exitPath_start(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPath_start" ):
                return visitor.visitPath_start(self)
            else:
                return visitor.visitChildren(self)




    def path_start(self):

        localctx = TikzParser.Path_startContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_path_start)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 121
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 4088) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Path_elementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def coordinate(self):
            return self.getTypedRuleContext(TikzParser.CoordinateContext,0)


        def shape_spec(self):
            return self.getTypedRuleContext(TikzParser.Shape_specContext,0)


        def arc_spec(self):
            return self.getTypedRuleContext(TikzParser.Arc_specContext,0)


        def control_spec(self):
            return self.getTypedRuleContext(TikzParser.Control_specContext,0)


        def node_inline(self):
            return self.getTypedRuleContext(TikzParser.Node_inlineContext,0)


        def brace_text(self):
            return self.getTypedRuleContext(TikzParser.Brace_textContext,0)


        def edge_op(self):
            return self.getTypedRuleContext(TikzParser.Edge_opContext,0)


        def tikz_options(self):
            return self.getTypedRuleContext(TikzParser.Tikz_optionsContext,0)


        def CYCLE(self):
            return self.getToken(TikzParser.CYCLE, 0)

        def AT(self):
            return self.getToken(TikzParser.AT, 0)

        def PLOT(self):
            return self.getToken(TikzParser.PLOT, 0)

        def COORDINATES(self):
            return self.getToken(TikzParser.COORDINATES, 0)

        def path_skip_token(self):
            return self.getTypedRuleContext(TikzParser.Path_skip_tokenContext,0)


        def getRuleIndex(self):
            return TikzParser.RULE_path_element

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPath_element" ):
                listener.enterPath_element(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPath_element" ):
                listener.exitPath_element(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPath_element" ):
                return visitor.visitPath_element(self)
            else:
                return visitor.visitChildren(self)




    def path_element(self):

        localctx = TikzParser.Path_elementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_path_element)
        self._la = 0 # Token type
        try:
            self.state = 140
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,12,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 123
                self.coordinate()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 124
                self.shape_spec()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 125
                self.arc_spec()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 126
                self.control_spec()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 127
                self.node_inline()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 128
                self.brace_text()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 129
                self.edge_op()
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 130
                self.tikz_options()
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 131
                self.match(TikzParser.CYCLE)
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 132
                self.match(TikzParser.AT)
                self.state = 133
                self.coordinate()
                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 134
                self.match(TikzParser.PLOT)
                self.state = 136
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==36:
                    self.state = 135
                    self.tikz_options()


                self.state = 138
                self.match(TikzParser.COORDINATES)
                pass

            elif la_ == 12:
                self.enterOuterAlt(localctx, 12)
                self.state = 139
                self.path_skip_token()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Path_skip_tokenContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ANY(self):
            return self.getToken(TikzParser.ANY, 0)

        def NUMBER(self):
            return self.getToken(TikzParser.NUMBER, 0)

        def ID(self):
            return self.getToken(TikzParser.ID, 0)

        def COLON(self):
            return self.getToken(TikzParser.COLON, 0)

        def COMMA(self):
            return self.getToken(TikzParser.COMMA, 0)

        def DOT_DOT(self):
            return self.getToken(TikzParser.DOT_DOT, 0)

        def COMMAND(self):
            return self.getToken(TikzParser.COMMAND, 0)

        def getRuleIndex(self):
            return TikzParser.RULE_path_skip_token

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPath_skip_token" ):
                listener.enterPath_skip_token(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPath_skip_token" ):
                listener.exitPath_skip_token(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPath_skip_token" ):
                return visitor.visitPath_skip_token(self)
            else:
                return visitor.visitChildren(self)




    def path_skip_token(self):

        localctx = TikzParser.Path_skip_tokenContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_path_skip_token)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 142
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 21447456063488) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Shape_specContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RECTANGLE(self):
            return self.getToken(TikzParser.RECTANGLE, 0)

        def coordinate(self):
            return self.getTypedRuleContext(TikzParser.CoordinateContext,0)


        def CIRCLE(self):
            return self.getToken(TikzParser.CIRCLE, 0)

        def tikz_options(self):
            return self.getTypedRuleContext(TikzParser.Tikz_optionsContext,0)


        def circle_size(self):
            return self.getTypedRuleContext(TikzParser.Circle_sizeContext,0)


        def ELLIPSE(self):
            return self.getToken(TikzParser.ELLIPSE, 0)

        def ellipse_size(self):
            return self.getTypedRuleContext(TikzParser.Ellipse_sizeContext,0)


        def GRID(self):
            return self.getToken(TikzParser.GRID, 0)

        def PARABOLA(self):
            return self.getToken(TikzParser.PARABOLA, 0)

        def getRuleIndex(self):
            return TikzParser.RULE_shape_spec

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterShape_spec" ):
                listener.enterShape_spec(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitShape_spec" ):
                listener.exitShape_spec(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitShape_spec" ):
                return visitor.visitShape_spec(self)
            else:
                return visitor.visitChildren(self)




    def shape_spec(self):

        localctx = TikzParser.Shape_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_shape_spec)
        self._la = 0 # Token type
        try:
            self.state = 170
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [12]:
                self.enterOuterAlt(localctx, 1)
                self.state = 144
                self.match(TikzParser.RECTANGLE)
                self.state = 145
                self.coordinate()
                pass
            elif token in [13]:
                self.enterOuterAlt(localctx, 2)
                self.state = 146
                self.match(TikzParser.CIRCLE)
                self.state = 148
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,13,self._ctx)
                if la_ == 1:
                    self.state = 147
                    self.tikz_options()


                self.state = 151
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,14,self._ctx)
                if la_ == 1:
                    self.state = 150
                    self.circle_size()


                pass
            elif token in [14]:
                self.enterOuterAlt(localctx, 3)
                self.state = 153
                self.match(TikzParser.ELLIPSE)
                self.state = 155
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,15,self._ctx)
                if la_ == 1:
                    self.state = 154
                    self.tikz_options()


                self.state = 158
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,16,self._ctx)
                if la_ == 1:
                    self.state = 157
                    self.ellipse_size()


                pass
            elif token in [15]:
                self.enterOuterAlt(localctx, 4)
                self.state = 160
                self.match(TikzParser.GRID)
                self.state = 162
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==36:
                    self.state = 161
                    self.tikz_options()


                self.state = 164
                self.coordinate()
                pass
            elif token in [16]:
                self.enterOuterAlt(localctx, 5)
                self.state = 165
                self.match(TikzParser.PARABOLA)
                self.state = 167
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==36:
                    self.state = 166
                    self.tikz_options()


                self.state = 169
                self.coordinate()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Circle_sizeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self):
            return self.getToken(TikzParser.LPAREN, 0)

        def numberunit(self):
            return self.getTypedRuleContext(TikzParser.NumberunitContext,0)


        def RPAREN(self):
            return self.getToken(TikzParser.RPAREN, 0)

        def getRuleIndex(self):
            return TikzParser.RULE_circle_size

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCircle_size" ):
                listener.enterCircle_size(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCircle_size" ):
                listener.exitCircle_size(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCircle_size" ):
                return visitor.visitCircle_size(self)
            else:
                return visitor.visitChildren(self)




    def circle_size(self):

        localctx = TikzParser.Circle_sizeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_circle_size)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 172
            self.match(TikzParser.LPAREN)
            self.state = 173
            self.numberunit()
            self.state = 174
            self.match(TikzParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Ellipse_sizeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self):
            return self.getToken(TikzParser.LPAREN, 0)

        def numberunit(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TikzParser.NumberunitContext)
            else:
                return self.getTypedRuleContext(TikzParser.NumberunitContext,i)


        def AND(self):
            return self.getToken(TikzParser.AND, 0)

        def RPAREN(self):
            return self.getToken(TikzParser.RPAREN, 0)

        def getRuleIndex(self):
            return TikzParser.RULE_ellipse_size

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEllipse_size" ):
                listener.enterEllipse_size(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEllipse_size" ):
                listener.exitEllipse_size(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEllipse_size" ):
                return visitor.visitEllipse_size(self)
            else:
                return visitor.visitChildren(self)




    def ellipse_size(self):

        localctx = TikzParser.Ellipse_sizeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_ellipse_size)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 176
            self.match(TikzParser.LPAREN)
            self.state = 177
            self.numberunit()
            self.state = 178
            self.match(TikzParser.AND)
            self.state = 179
            self.numberunit()
            self.state = 180
            self.match(TikzParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Arc_specContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ARC(self):
            return self.getToken(TikzParser.ARC, 0)

        def LPAREN(self):
            return self.getToken(TikzParser.LPAREN, 0)

        def arc_params(self):
            return self.getTypedRuleContext(TikzParser.Arc_paramsContext,0)


        def RPAREN(self):
            return self.getToken(TikzParser.RPAREN, 0)

        def tikz_options(self):
            return self.getTypedRuleContext(TikzParser.Tikz_optionsContext,0)


        def getRuleIndex(self):
            return TikzParser.RULE_arc_spec

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArc_spec" ):
                listener.enterArc_spec(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArc_spec" ):
                listener.exitArc_spec(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArc_spec" ):
                return visitor.visitArc_spec(self)
            else:
                return visitor.visitChildren(self)




    def arc_spec(self):

        localctx = TikzParser.Arc_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_arc_spec)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 182
            self.match(TikzParser.ARC)
            self.state = 184
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==36:
                self.state = 183
                self.tikz_options()


            self.state = 186
            self.match(TikzParser.LPAREN)
            self.state = 187
            self.arc_params()
            self.state = 188
            self.match(TikzParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Arc_paramsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def numberunit(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TikzParser.NumberunitContext)
            else:
                return self.getTypedRuleContext(TikzParser.NumberunitContext,i)


        def COLON(self, i:int=None):
            if i is None:
                return self.getTokens(TikzParser.COLON)
            else:
                return self.getToken(TikzParser.COLON, i)

        def AND(self):
            return self.getToken(TikzParser.AND, 0)

        def getRuleIndex(self):
            return TikzParser.RULE_arc_params

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArc_params" ):
                listener.enterArc_params(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArc_params" ):
                listener.exitArc_params(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArc_params" ):
                return visitor.visitArc_params(self)
            else:
                return visitor.visitChildren(self)




    def arc_params(self):

        localctx = TikzParser.Arc_paramsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_arc_params)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 190
            self.numberunit()
            self.state = 191
            self.match(TikzParser.COLON)
            self.state = 192
            self.numberunit()
            self.state = 193
            self.match(TikzParser.COLON)
            self.state = 194
            self.numberunit()
            self.state = 197
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==19:
                self.state = 195
                self.match(TikzParser.AND)
                self.state = 196
                self.numberunit()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Control_specContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DOT_DOT(self, i:int=None):
            if i is None:
                return self.getTokens(TikzParser.DOT_DOT)
            else:
                return self.getToken(TikzParser.DOT_DOT, i)

        def CONTROLS(self):
            return self.getToken(TikzParser.CONTROLS, 0)

        def coordinate(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TikzParser.CoordinateContext)
            else:
                return self.getTypedRuleContext(TikzParser.CoordinateContext,i)


        def AND(self):
            return self.getToken(TikzParser.AND, 0)

        def getRuleIndex(self):
            return TikzParser.RULE_control_spec

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterControl_spec" ):
                listener.enterControl_spec(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitControl_spec" ):
                listener.exitControl_spec(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitControl_spec" ):
                return visitor.visitControl_spec(self)
            else:
                return visitor.visitChildren(self)




    def control_spec(self):

        localctx = TikzParser.Control_specContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_control_spec)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 199
            self.match(TikzParser.DOT_DOT)
            self.state = 200
            self.match(TikzParser.CONTROLS)
            self.state = 201
            self.coordinate()
            self.state = 204
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==19:
                self.state = 202
                self.match(TikzParser.AND)
                self.state = 203
                self.coordinate()


            self.state = 206
            self.match(TikzParser.DOT_DOT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Node_inlineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NODE(self):
            return self.getToken(TikzParser.NODE, 0)

        def brace_text(self):
            return self.getTypedRuleContext(TikzParser.Brace_textContext,0)


        def tikz_options(self):
            return self.getTypedRuleContext(TikzParser.Tikz_optionsContext,0)


        def node_name(self):
            return self.getTypedRuleContext(TikzParser.Node_nameContext,0)


        def AT(self):
            return self.getToken(TikzParser.AT, 0)

        def coordinate(self):
            return self.getTypedRuleContext(TikzParser.CoordinateContext,0)


        def getRuleIndex(self):
            return TikzParser.RULE_node_inline

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNode_inline" ):
                listener.enterNode_inline(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNode_inline" ):
                listener.exitNode_inline(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNode_inline" ):
                return visitor.visitNode_inline(self)
            else:
                return visitor.visitChildren(self)




    def node_inline(self):

        localctx = TikzParser.Node_inlineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_node_inline)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 208
            self.match(TikzParser.NODE)
            self.state = 210
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==36:
                self.state = 209
                self.tikz_options()


            self.state = 213
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==33:
                self.state = 212
                self.node_name()


            self.state = 217
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==21:
                self.state = 215
                self.match(TikzParser.AT)
                self.state = 216
                self.coordinate()


            self.state = 219
            self.brace_text()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Node_nameContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self):
            return self.getToken(TikzParser.LPAREN, 0)

        def ID(self):
            return self.getToken(TikzParser.ID, 0)

        def RPAREN(self):
            return self.getToken(TikzParser.RPAREN, 0)

        def getRuleIndex(self):
            return TikzParser.RULE_node_name

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNode_name" ):
                listener.enterNode_name(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNode_name" ):
                listener.exitNode_name(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNode_name" ):
                return visitor.visitNode_name(self)
            else:
                return visitor.visitChildren(self)




    def node_name(self):

        localctx = TikzParser.Node_nameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_node_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 221
            self.match(TikzParser.LPAREN)
            self.state = 222
            self.match(TikzParser.ID)
            self.state = 223
            self.match(TikzParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Brace_textContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(TikzParser.LBRACE, 0)

        def BRACE_RBRACE(self):
            return self.getToken(TikzParser.BRACE_RBRACE, 0)

        def brace_item(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TikzParser.Brace_itemContext)
            else:
                return self.getTypedRuleContext(TikzParser.Brace_itemContext,i)


        def getRuleIndex(self):
            return TikzParser.RULE_brace_text

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBrace_text" ):
                listener.enterBrace_text(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBrace_text" ):
                listener.exitBrace_text(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBrace_text" ):
                return visitor.visitBrace_text(self)
            else:
                return visitor.visitChildren(self)




    def brace_text(self):

        localctx = TikzParser.Brace_textContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_brace_text)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 225
            self.match(TikzParser.LBRACE)
            self.state = 229
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==52 or _la==54:
                self.state = 226
                self.brace_item()
                self.state = 231
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 232
            self.match(TikzParser.BRACE_RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Brace_itemContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def BRACE_CONTENT(self):
            return self.getToken(TikzParser.BRACE_CONTENT, 0)

        def BRACE_LBRACE(self):
            return self.getToken(TikzParser.BRACE_LBRACE, 0)

        def BRACE_RBRACE(self):
            return self.getToken(TikzParser.BRACE_RBRACE, 0)

        def brace_item(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TikzParser.Brace_itemContext)
            else:
                return self.getTypedRuleContext(TikzParser.Brace_itemContext,i)


        def getRuleIndex(self):
            return TikzParser.RULE_brace_item

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBrace_item" ):
                listener.enterBrace_item(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBrace_item" ):
                listener.exitBrace_item(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBrace_item" ):
                return visitor.visitBrace_item(self)
            else:
                return visitor.visitChildren(self)




    def brace_item(self):

        localctx = TikzParser.Brace_itemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_brace_item)
        self._la = 0 # Token type
        try:
            self.state = 243
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [54]:
                self.enterOuterAlt(localctx, 1)
                self.state = 234
                self.match(TikzParser.BRACE_CONTENT)
                pass
            elif token in [52]:
                self.enterOuterAlt(localctx, 2)
                self.state = 235
                self.match(TikzParser.BRACE_LBRACE)
                self.state = 239
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==52 or _la==54:
                    self.state = 236
                    self.brace_item()
                    self.state = 241
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 242
                self.match(TikzParser.BRACE_RBRACE)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Edge_opContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DASH_DASH(self):
            return self.getToken(TikzParser.DASH_DASH, 0)

        def DASH_ARROW(self):
            return self.getToken(TikzParser.DASH_ARROW, 0)

        def PIPE_DASH(self):
            return self.getToken(TikzParser.PIPE_DASH, 0)

        def DASH_PIPE(self):
            return self.getToken(TikzParser.DASH_PIPE, 0)

        def getRuleIndex(self):
            return TikzParser.RULE_edge_op

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEdge_op" ):
                listener.enterEdge_op(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEdge_op" ):
                listener.exitEdge_op(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEdge_op" ):
                return visitor.visitEdge_op(self)
            else:
                return visitor.visitChildren(self)




    def edge_op(self):

        localctx = TikzParser.Edge_opContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_edge_op)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 245
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 503316480) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CoordinateContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self):
            return self.getToken(TikzParser.LPAREN, 0)

        def coord_value(self):
            return self.getTypedRuleContext(TikzParser.Coord_valueContext,0)


        def RPAREN(self):
            return self.getToken(TikzParser.RPAREN, 0)

        def PLUS(self, i:int=None):
            if i is None:
                return self.getTokens(TikzParser.PLUS)
            else:
                return self.getToken(TikzParser.PLUS, i)

        def getRuleIndex(self):
            return TikzParser.RULE_coordinate

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCoordinate" ):
                listener.enterCoordinate(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCoordinate" ):
                listener.exitCoordinate(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCoordinate" ):
                return visitor.visitCoordinate(self)
            else:
                return visitor.visitChildren(self)




    def coordinate(self):

        localctx = TikzParser.CoordinateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_coordinate)
        try:
            self.state = 262
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,29,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 247
                self.match(TikzParser.LPAREN)
                self.state = 248
                self.coord_value()
                self.state = 249
                self.match(TikzParser.RPAREN)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 251
                self.match(TikzParser.PLUS)
                self.state = 252
                self.match(TikzParser.PLUS)
                self.state = 253
                self.match(TikzParser.LPAREN)
                self.state = 254
                self.coord_value()
                self.state = 255
                self.match(TikzParser.RPAREN)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 257
                self.match(TikzParser.PLUS)
                self.state = 258
                self.match(TikzParser.LPAREN)
                self.state = 259
                self.coord_value()
                self.state = 260
                self.match(TikzParser.RPAREN)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Coord_valueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def numberunit(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TikzParser.NumberunitContext)
            else:
                return self.getTypedRuleContext(TikzParser.NumberunitContext,i)


        def COMMA(self):
            return self.getToken(TikzParser.COMMA, 0)

        def COLON(self):
            return self.getToken(TikzParser.COLON, 0)

        def ID(self):
            return self.getToken(TikzParser.ID, 0)

        def getRuleIndex(self):
            return TikzParser.RULE_coord_value

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCoord_value" ):
                listener.enterCoord_value(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCoord_value" ):
                listener.exitCoord_value(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCoord_value" ):
                return visitor.visitCoord_value(self)
            else:
                return visitor.visitChildren(self)




    def coord_value(self):

        localctx = TikzParser.Coord_valueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_coord_value)
        try:
            self.state = 273
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,30,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 264
                self.numberunit()
                self.state = 265
                self.match(TikzParser.COMMA)
                self.state = 266
                self.numberunit()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 268
                self.numberunit()
                self.state = 269
                self.match(TikzParser.COLON)
                self.state = 270
                self.numberunit()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 272
                self.match(TikzParser.ID)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NumberunitContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(TikzParser.NUMBER, 0)

        def unit(self):
            return self.getTypedRuleContext(TikzParser.UnitContext,0)


        def getRuleIndex(self):
            return TikzParser.RULE_numberunit

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNumberunit" ):
                listener.enterNumberunit(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNumberunit" ):
                listener.exitNumberunit(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNumberunit" ):
                return visitor.visitNumberunit(self)
            else:
                return visitor.visitChildren(self)




    def numberunit(self):

        localctx = TikzParser.NumberunitContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_numberunit)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 275
            self.match(TikzParser.NUMBER)
            self.state = 277
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==40:
                self.state = 276
                self.unit()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class UnitContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(TikzParser.ID, 0)

        def getRuleIndex(self):
            return TikzParser.RULE_unit

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterUnit" ):
                listener.enterUnit(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitUnit" ):
                listener.exitUnit(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitUnit" ):
                return visitor.visitUnit(self)
            else:
                return visitor.visitChildren(self)




    def unit(self):

        localctx = TikzParser.UnitContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_unit)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 279
            self.match(TikzParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Tikz_optionsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACK(self):
            return self.getToken(TikzParser.LBRACK, 0)

        def OPT_RBRACK(self):
            return self.getToken(TikzParser.OPT_RBRACK, 0)

        def option_list(self):
            return self.getTypedRuleContext(TikzParser.Option_listContext,0)


        def getRuleIndex(self):
            return TikzParser.RULE_tikz_options

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTikz_options" ):
                listener.enterTikz_options(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTikz_options" ):
                listener.exitTikz_options(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTikz_options" ):
                return visitor.visitTikz_options(self)
            else:
                return visitor.visitChildren(self)




    def tikz_options(self):

        localctx = TikzParser.Tikz_optionsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_tikz_options)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 281
            self.match(TikzParser.LBRACK)
            self.state = 283
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 2427721674129408) != 0):
                self.state = 282
                self.option_list()


            self.state = 285
            self.match(TikzParser.OPT_RBRACK)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Option_listContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def option_item(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TikzParser.Option_itemContext)
            else:
                return self.getTypedRuleContext(TikzParser.Option_itemContext,i)


        def OPT_COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(TikzParser.OPT_COMMA)
            else:
                return self.getToken(TikzParser.OPT_COMMA, i)

        def getRuleIndex(self):
            return TikzParser.RULE_option_list

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOption_list" ):
                listener.enterOption_list(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOption_list" ):
                listener.exitOption_list(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOption_list" ):
                return visitor.visitOption_list(self)
            else:
                return visitor.visitChildren(self)




    def option_list(self):

        localctx = TikzParser.Option_listContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_option_list)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 287
            self.option_item()
            self.state = 292
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,33,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 288
                    self.match(TikzParser.OPT_COMMA)
                    self.state = 289
                    self.option_item() 
                self.state = 294
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,33,self._ctx)

            self.state = 296
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==49:
                self.state = 295
                self.match(TikzParser.OPT_COMMA)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Option_itemContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def option_atom(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TikzParser.Option_atomContext)
            else:
                return self.getTypedRuleContext(TikzParser.Option_atomContext,i)


        def OPT_EQ(self):
            return self.getToken(TikzParser.OPT_EQ, 0)

        def getRuleIndex(self):
            return TikzParser.RULE_option_item

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOption_item" ):
                listener.enterOption_item(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOption_item" ):
                listener.exitOption_item(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOption_item" ):
                return visitor.visitOption_item(self)
            else:
                return visitor.visitChildren(self)




    def option_item(self):

        localctx = TikzParser.Option_itemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_option_item)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 298
            self.option_atom()
            self.state = 301
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==48:
                self.state = 299
                self.match(TikzParser.OPT_EQ)
                self.state = 300
                self.option_atom()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Opt_brace_textContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def OPT_LBRACE(self):
            return self.getToken(TikzParser.OPT_LBRACE, 0)

        def BRACE_RBRACE(self):
            return self.getToken(TikzParser.BRACE_RBRACE, 0)

        def brace_item(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TikzParser.Brace_itemContext)
            else:
                return self.getTypedRuleContext(TikzParser.Brace_itemContext,i)


        def getRuleIndex(self):
            return TikzParser.RULE_opt_brace_text

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOpt_brace_text" ):
                listener.enterOpt_brace_text(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOpt_brace_text" ):
                listener.exitOpt_brace_text(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOpt_brace_text" ):
                return visitor.visitOpt_brace_text(self)
            else:
                return visitor.visitChildren(self)




    def opt_brace_text(self):

        localctx = TikzParser.Opt_brace_textContext(self, self._ctx, self.state)
        self.enterRule(localctx, 58, self.RULE_opt_brace_text)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 303
            self.match(TikzParser.OPT_LBRACE)
            self.state = 307
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==52 or _la==54:
                self.state = 304
                self.brace_item()
                self.state = 309
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 310
            self.match(TikzParser.BRACE_RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Option_atomContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def OPT_TEXT(self, i:int=None):
            if i is None:
                return self.getTokens(TikzParser.OPT_TEXT)
            else:
                return self.getToken(TikzParser.OPT_TEXT, i)

        def opt_brace_text(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TikzParser.Opt_brace_textContext)
            else:
                return self.getTypedRuleContext(TikzParser.Opt_brace_textContext,i)


        def OPT_LBRACK(self, i:int=None):
            if i is None:
                return self.getTokens(TikzParser.OPT_LBRACK)
            else:
                return self.getToken(TikzParser.OPT_LBRACK, i)

        def OPT_RBRACK(self, i:int=None):
            if i is None:
                return self.getTokens(TikzParser.OPT_RBRACK)
            else:
                return self.getToken(TikzParser.OPT_RBRACK, i)

        def option_list(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TikzParser.Option_listContext)
            else:
                return self.getTypedRuleContext(TikzParser.Option_listContext,i)


        def getRuleIndex(self):
            return TikzParser.RULE_option_atom

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOption_atom" ):
                listener.enterOption_atom(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOption_atom" ):
                listener.exitOption_atom(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOption_atom" ):
                return visitor.visitOption_atom(self)
            else:
                return visitor.visitChildren(self)




    def option_atom(self):

        localctx = TikzParser.Option_atomContext(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_option_atom)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 319 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 319
                self._errHandler.sync(self)
                token = self._input.LA(1)
                if token in [51]:
                    self.state = 312
                    self.match(TikzParser.OPT_TEXT)
                    pass
                elif token in [47]:
                    self.state = 313
                    self.opt_brace_text()
                    pass
                elif token in [45]:
                    self.state = 314
                    self.match(TikzParser.OPT_LBRACK)
                    self.state = 316
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if (((_la) & ~0x3f) == 0 and ((1 << _la) & 2427721674129408) != 0):
                        self.state = 315
                        self.option_list()


                    self.state = 318
                    self.match(TikzParser.OPT_RBRACK)
                    pass
                else:
                    raise NoViableAltException(self)

                self.state = 321 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 2427721674129408) != 0)):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





