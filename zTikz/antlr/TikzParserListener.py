# Generated from TikzParser.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .TikzParser import TikzParser
else:
    from TikzParser import TikzParser

# This class defines a complete listener for a parse tree produced by TikzParser.
class TikzParserListener(ParseTreeListener):

    # Enter a parse tree produced by TikzParser#document.
    def enterDocument(self, ctx:TikzParser.DocumentContext):
        pass

    # Exit a parse tree produced by TikzParser#document.
    def exitDocument(self, ctx:TikzParser.DocumentContext):
        pass


    # Enter a parse tree produced by TikzParser#skip_token.
    def enterSkip_token(self, ctx:TikzParser.Skip_tokenContext):
        pass

    # Exit a parse tree produced by TikzParser#skip_token.
    def exitSkip_token(self, ctx:TikzParser.Skip_tokenContext):
        pass


    # Enter a parse tree produced by TikzParser#tikzpicture.
    def enterTikzpicture(self, ctx:TikzParser.TikzpictureContext):
        pass

    # Exit a parse tree produced by TikzParser#tikzpicture.
    def exitTikzpicture(self, ctx:TikzParser.TikzpictureContext):
        pass


    # Enter a parse tree produced by TikzParser#tikzbody.
    def enterTikzbody(self, ctx:TikzParser.TikzbodyContext):
        pass

    # Exit a parse tree produced by TikzParser#tikzbody.
    def exitTikzbody(self, ctx:TikzParser.TikzbodyContext):
        pass


    # Enter a parse tree produced by TikzParser#tikz_stmt.
    def enterTikz_stmt(self, ctx:TikzParser.Tikz_stmtContext):
        pass

    # Exit a parse tree produced by TikzParser#tikz_stmt.
    def exitTikz_stmt(self, ctx:TikzParser.Tikz_stmtContext):
        pass


    # Enter a parse tree produced by TikzParser#standalone_node.
    def enterStandalone_node(self, ctx:TikzParser.Standalone_nodeContext):
        pass

    # Exit a parse tree produced by TikzParser#standalone_node.
    def exitStandalone_node(self, ctx:TikzParser.Standalone_nodeContext):
        pass


    # Enter a parse tree produced by TikzParser#skip_body.
    def enterSkip_body(self, ctx:TikzParser.Skip_bodyContext):
        pass

    # Exit a parse tree produced by TikzParser#skip_body.
    def exitSkip_body(self, ctx:TikzParser.Skip_bodyContext):
        pass


    # Enter a parse tree produced by TikzParser#path_cmd.
    def enterPath_cmd(self, ctx:TikzParser.Path_cmdContext):
        pass

    # Exit a parse tree produced by TikzParser#path_cmd.
    def exitPath_cmd(self, ctx:TikzParser.Path_cmdContext):
        pass


    # Enter a parse tree produced by TikzParser#path_start.
    def enterPath_start(self, ctx:TikzParser.Path_startContext):
        pass

    # Exit a parse tree produced by TikzParser#path_start.
    def exitPath_start(self, ctx:TikzParser.Path_startContext):
        pass


    # Enter a parse tree produced by TikzParser#path_element.
    def enterPath_element(self, ctx:TikzParser.Path_elementContext):
        pass

    # Exit a parse tree produced by TikzParser#path_element.
    def exitPath_element(self, ctx:TikzParser.Path_elementContext):
        pass


    # Enter a parse tree produced by TikzParser#path_skip_token.
    def enterPath_skip_token(self, ctx:TikzParser.Path_skip_tokenContext):
        pass

    # Exit a parse tree produced by TikzParser#path_skip_token.
    def exitPath_skip_token(self, ctx:TikzParser.Path_skip_tokenContext):
        pass


    # Enter a parse tree produced by TikzParser#shape_spec.
    def enterShape_spec(self, ctx:TikzParser.Shape_specContext):
        pass

    # Exit a parse tree produced by TikzParser#shape_spec.
    def exitShape_spec(self, ctx:TikzParser.Shape_specContext):
        pass


    # Enter a parse tree produced by TikzParser#circle_size.
    def enterCircle_size(self, ctx:TikzParser.Circle_sizeContext):
        pass

    # Exit a parse tree produced by TikzParser#circle_size.
    def exitCircle_size(self, ctx:TikzParser.Circle_sizeContext):
        pass


    # Enter a parse tree produced by TikzParser#ellipse_size.
    def enterEllipse_size(self, ctx:TikzParser.Ellipse_sizeContext):
        pass

    # Exit a parse tree produced by TikzParser#ellipse_size.
    def exitEllipse_size(self, ctx:TikzParser.Ellipse_sizeContext):
        pass


    # Enter a parse tree produced by TikzParser#arc_spec.
    def enterArc_spec(self, ctx:TikzParser.Arc_specContext):
        pass

    # Exit a parse tree produced by TikzParser#arc_spec.
    def exitArc_spec(self, ctx:TikzParser.Arc_specContext):
        pass


    # Enter a parse tree produced by TikzParser#arc_params.
    def enterArc_params(self, ctx:TikzParser.Arc_paramsContext):
        pass

    # Exit a parse tree produced by TikzParser#arc_params.
    def exitArc_params(self, ctx:TikzParser.Arc_paramsContext):
        pass


    # Enter a parse tree produced by TikzParser#control_spec.
    def enterControl_spec(self, ctx:TikzParser.Control_specContext):
        pass

    # Exit a parse tree produced by TikzParser#control_spec.
    def exitControl_spec(self, ctx:TikzParser.Control_specContext):
        pass


    # Enter a parse tree produced by TikzParser#node_inline.
    def enterNode_inline(self, ctx:TikzParser.Node_inlineContext):
        pass

    # Exit a parse tree produced by TikzParser#node_inline.
    def exitNode_inline(self, ctx:TikzParser.Node_inlineContext):
        pass


    # Enter a parse tree produced by TikzParser#node_name.
    def enterNode_name(self, ctx:TikzParser.Node_nameContext):
        pass

    # Exit a parse tree produced by TikzParser#node_name.
    def exitNode_name(self, ctx:TikzParser.Node_nameContext):
        pass


    # Enter a parse tree produced by TikzParser#brace_text.
    def enterBrace_text(self, ctx:TikzParser.Brace_textContext):
        pass

    # Exit a parse tree produced by TikzParser#brace_text.
    def exitBrace_text(self, ctx:TikzParser.Brace_textContext):
        pass


    # Enter a parse tree produced by TikzParser#brace_item.
    def enterBrace_item(self, ctx:TikzParser.Brace_itemContext):
        pass

    # Exit a parse tree produced by TikzParser#brace_item.
    def exitBrace_item(self, ctx:TikzParser.Brace_itemContext):
        pass


    # Enter a parse tree produced by TikzParser#edge_op.
    def enterEdge_op(self, ctx:TikzParser.Edge_opContext):
        pass

    # Exit a parse tree produced by TikzParser#edge_op.
    def exitEdge_op(self, ctx:TikzParser.Edge_opContext):
        pass


    # Enter a parse tree produced by TikzParser#coordinate.
    def enterCoordinate(self, ctx:TikzParser.CoordinateContext):
        pass

    # Exit a parse tree produced by TikzParser#coordinate.
    def exitCoordinate(self, ctx:TikzParser.CoordinateContext):
        pass


    # Enter a parse tree produced by TikzParser#coord_value.
    def enterCoord_value(self, ctx:TikzParser.Coord_valueContext):
        pass

    # Exit a parse tree produced by TikzParser#coord_value.
    def exitCoord_value(self, ctx:TikzParser.Coord_valueContext):
        pass


    # Enter a parse tree produced by TikzParser#numberunit.
    def enterNumberunit(self, ctx:TikzParser.NumberunitContext):
        pass

    # Exit a parse tree produced by TikzParser#numberunit.
    def exitNumberunit(self, ctx:TikzParser.NumberunitContext):
        pass


    # Enter a parse tree produced by TikzParser#unit.
    def enterUnit(self, ctx:TikzParser.UnitContext):
        pass

    # Exit a parse tree produced by TikzParser#unit.
    def exitUnit(self, ctx:TikzParser.UnitContext):
        pass


    # Enter a parse tree produced by TikzParser#tikz_options.
    def enterTikz_options(self, ctx:TikzParser.Tikz_optionsContext):
        pass

    # Exit a parse tree produced by TikzParser#tikz_options.
    def exitTikz_options(self, ctx:TikzParser.Tikz_optionsContext):
        pass


    # Enter a parse tree produced by TikzParser#option_list.
    def enterOption_list(self, ctx:TikzParser.Option_listContext):
        pass

    # Exit a parse tree produced by TikzParser#option_list.
    def exitOption_list(self, ctx:TikzParser.Option_listContext):
        pass


    # Enter a parse tree produced by TikzParser#option_item.
    def enterOption_item(self, ctx:TikzParser.Option_itemContext):
        pass

    # Exit a parse tree produced by TikzParser#option_item.
    def exitOption_item(self, ctx:TikzParser.Option_itemContext):
        pass


    # Enter a parse tree produced by TikzParser#opt_brace_text.
    def enterOpt_brace_text(self, ctx:TikzParser.Opt_brace_textContext):
        pass

    # Exit a parse tree produced by TikzParser#opt_brace_text.
    def exitOpt_brace_text(self, ctx:TikzParser.Opt_brace_textContext):
        pass


    # Enter a parse tree produced by TikzParser#option_atom.
    def enterOption_atom(self, ctx:TikzParser.Option_atomContext):
        pass

    # Exit a parse tree produced by TikzParser#option_atom.
    def exitOption_atom(self, ctx:TikzParser.Option_atomContext):
        pass



del TikzParser