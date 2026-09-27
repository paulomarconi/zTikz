# Generated from TikzParser.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .TikzParser import TikzParser
else:
    from TikzParser import TikzParser

# This class defines a complete generic visitor for a parse tree produced by TikzParser.

class TikzParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by TikzParser#document.
    def visitDocument(self, ctx:TikzParser.DocumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#skip_token.
    def visitSkip_token(self, ctx:TikzParser.Skip_tokenContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#tikzpicture.
    def visitTikzpicture(self, ctx:TikzParser.TikzpictureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#tikzbody.
    def visitTikzbody(self, ctx:TikzParser.TikzbodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#tikz_stmt.
    def visitTikz_stmt(self, ctx:TikzParser.Tikz_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#standalone_node.
    def visitStandalone_node(self, ctx:TikzParser.Standalone_nodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#skip_body.
    def visitSkip_body(self, ctx:TikzParser.Skip_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#path_cmd.
    def visitPath_cmd(self, ctx:TikzParser.Path_cmdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#path_start.
    def visitPath_start(self, ctx:TikzParser.Path_startContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#path_element.
    def visitPath_element(self, ctx:TikzParser.Path_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#path_skip_token.
    def visitPath_skip_token(self, ctx:TikzParser.Path_skip_tokenContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#shape_spec.
    def visitShape_spec(self, ctx:TikzParser.Shape_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#circle_size.
    def visitCircle_size(self, ctx:TikzParser.Circle_sizeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#ellipse_size.
    def visitEllipse_size(self, ctx:TikzParser.Ellipse_sizeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#arc_spec.
    def visitArc_spec(self, ctx:TikzParser.Arc_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#arc_params.
    def visitArc_params(self, ctx:TikzParser.Arc_paramsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#control_spec.
    def visitControl_spec(self, ctx:TikzParser.Control_specContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#node_inline.
    def visitNode_inline(self, ctx:TikzParser.Node_inlineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#node_name.
    def visitNode_name(self, ctx:TikzParser.Node_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#brace_text.
    def visitBrace_text(self, ctx:TikzParser.Brace_textContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#brace_item.
    def visitBrace_item(self, ctx:TikzParser.Brace_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#edge_op.
    def visitEdge_op(self, ctx:TikzParser.Edge_opContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#coordinate.
    def visitCoordinate(self, ctx:TikzParser.CoordinateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#coord_value.
    def visitCoord_value(self, ctx:TikzParser.Coord_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#numberunit.
    def visitNumberunit(self, ctx:TikzParser.NumberunitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#unit.
    def visitUnit(self, ctx:TikzParser.UnitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#tikz_options.
    def visitTikz_options(self, ctx:TikzParser.Tikz_optionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#option_list.
    def visitOption_list(self, ctx:TikzParser.Option_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#option_item.
    def visitOption_item(self, ctx:TikzParser.Option_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#opt_brace_text.
    def visitOpt_brace_text(self, ctx:TikzParser.Opt_brace_textContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TikzParser#option_atom.
    def visitOption_atom(self, ctx:TikzParser.Option_atomContext):
        return self.visitChildren(ctx)



del TikzParser