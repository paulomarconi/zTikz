// =============================================================================
// TikzParser.g4 — ANTLR4 Parser grammar for TikZ 
//
// This parser grammar references tokens defined in TikzLexer.g4 via
// the tokenVocab option. The visitor (tikz_visitor.py) walks the resulting
// parse tree to extract canvas shapes.
// =============================================================================
parser grammar TikzParser;

// Reference the split lexer so the parser knows all token type names
options { tokenVocab=TikzLexer; }

// ---------------------------------------------------------------------------
// TOP-LEVEL DOCUMENT
// ---------------------------------------------------------------------------

document
    : (tikzpicture | skip_token)* EOF
    ;

// Tokens the parser silently skips at the document level (preamble commands,
// unknown LaTeX, plain text, etc.)
skip_token
    : ANY
    | NUMBER
    | ID
    | SEMI
    | COLON
    | COMMA
    | DASH_DASH | DASH_ARROW | PIPE_DASH | DASH_PIPE
    | DOT_DOT
    | LPAREN | RPAREN
    | RBRACE
    | COMMAND
    ;

// ---------------------------------------------------------------------------
// TIKZPICTURE ENVIRONMENT
// ---------------------------------------------------------------------------

tikzpicture
    : BEGIN_TIKZ tikz_options? tikzbody? END_TIKZ
    ;

// The body: one or more statements
tikzbody
    : tikz_stmt+
    ;

// One statement inside the tikzpicture.
// The parser tries each alternative in order; unknown tokens fall to skip_body.
tikz_stmt
    : standalone_node  // \node [opts] at (x,y) {text} ; — handled separately
    | path_cmd          // \draw [opts] ... ;
    | tikz_options      // standalone [opts] — e.g. global options
    | skip_body         // anything we don't specifically handle
    ;

// Standalone node command (\node ... ;)
standalone_node
    : NODE_CMD tikz_options? node_name? (AT coordinate)? brace_text SEMI
    ;

// Tokens the parser silently skips inside the tikzpicture body
skip_body
    : ANY
    | NUMBER
    | ID
    | SEMI
    | COLON
    | COMMA
    | DASH_DASH | DASH_ARROW | PIPE_DASH | DASH_PIPE
    | DOT_DOT
    | LPAREN | RPAREN
    | RBRACE
    | COMMAND
    ;

// ---------------------------------------------------------------------------
// PATH COMMANDS  (\draw, \fill, \path, \node, \filldraw, …)
// ---------------------------------------------------------------------------

path_cmd
    : path_start tikz_options? path_element* SEMI
    ;

// Keywords that open a path/draw statement
path_start
    : DRAW          // \draw
    | FILL          // \fill
    | PATHCMD       // \path
    | CLIP          // \clip
    | NODE_CMD      // \node (standalone node statement)
    | FILLDRAW      // \filldraw
    | PATTERN       // \pattern
    | SHADE         // \shade
    | SHADEDRAW     // \shadedraw
    ;

// Elements that can appear along a path
path_element
    : coordinate                // (x,y)  or  (nodename)
    | shape_spec                // rectangle/circle/ellipse/…
    | arc_spec                  // arc(start:end:radius)
    | control_spec              // .. controls (p1) and (p2) ..
    | node_inline               // node [opts] {label}
    | brace_text                // {label} directly on a path
    | edge_op                   // -- , ->, |-,  -|
    | tikz_options              // [opts]  inline option override
    | CYCLE                     // cycle  (close path)
    | AT coordinate             // at (x,y) — for node placement
    | PLOT tikz_options? COORDINATES          // plot coordinates — visitor collects coords
    | path_skip_token           // unknown single token — skip gracefully
    ;

// Tokens to skip within a path element (before the semicolon)
path_skip_token
    : ANY
    | NUMBER
    | ID
    | COLON
    | COMMA
    | DOT_DOT
    | COMMAND
    ;

// ---------------------------------------------------------------------------
// SHAPE SPECS  (what follows a coordinate)
// ---------------------------------------------------------------------------

shape_spec
    : RECTANGLE coordinate              // (p1) rectangle (p2)
    | CIRCLE    tikz_options? circle_size?      // circle (r)
    | ELLIPSE   tikz_options? ellipse_size?     // ellipse (rx and ry)
    | GRID      tikz_options? coordinate        // grid (corner)
    | PARABOLA  tikz_options? coordinate        // parabola (endpoint)
    ;

// Circle radius:  (number)
circle_size
    : LPAREN numberunit RPAREN
    ;

// Ellipse radii:  (rx and ry)
ellipse_size
    : LPAREN numberunit AND numberunit RPAREN
    ;

// ---------------------------------------------------------------------------
// ARC  arc(start:end:radius)
// ---------------------------------------------------------------------------

arc_spec
    : ARC tikz_options? LPAREN arc_params RPAREN
    ;

// start-angle : end-angle : radius  (all numberunit; optional  and ry  for elliptic arcs)
arc_params
    : numberunit COLON numberunit COLON numberunit (AND numberunit)?
    ;

// ---------------------------------------------------------------------------
// BEZIER CONTROLS  .. controls (p1) and (p2) ..
// ---------------------------------------------------------------------------

control_spec
    : DOT_DOT CONTROLS coordinate (AND coordinate)? DOT_DOT
    ;

// ---------------------------------------------------------------------------
// NODE  (inline: node [opts] {text})
// ---------------------------------------------------------------------------

node_inline
    : NODE tikz_options? node_name? (AT coordinate)? brace_text
    ;

node_name
    : LPAREN ID RPAREN
    ;

// Balanced brace content — the lexer handles nesting via BRACE_MODE.
// LBRACE transitions the lexer to BRACE_MODE, so nested braces become
// BRACE_LBRACE / BRACE_RBRACE tokens; content is BRACE_CONTENT.
brace_text
    : LBRACE brace_item* BRACE_RBRACE
    ;

brace_item
    : BRACE_CONTENT                             // raw text
    | BRACE_LBRACE brace_item* BRACE_RBRACE     // nested { ... }
    ;

// ---------------------------------------------------------------------------
// EDGE OPERATORS
// ---------------------------------------------------------------------------

edge_op
    : DASH_DASH     // --
    | DASH_ARROW    // ->
    | PIPE_DASH     // |-
    | DASH_PIPE     // -|
    ;

// ---------------------------------------------------------------------------
// COORDINATES  (x,y) or (nodename)
// ---------------------------------------------------------------------------

coordinate
    : LPAREN coord_value RPAREN
    | PLUS PLUS LPAREN coord_value RPAREN
    | PLUS LPAREN coord_value RPAREN
    ;

coord_value
    : numberunit COMMA numberunit   // Cartesian  (x,y)
    | numberunit COLON numberunit   // Polar      (angle:radius)
    | ID                            // Node reference  (nodename)
    ;

// ---------------------------------------------------------------------------
// NUMBERS WITH OPTIONAL UNIT  (e.g. 1.5cm, 10pt, 0.5)
// ---------------------------------------------------------------------------

numberunit
    : NUMBER unit?
    ;

unit
    : ID    // cm | pt | mm | in | em | ex — captured as ID by the lexer
    ;

// ---------------------------------------------------------------------------
// OPTIONS  [key=value, key, ...]
// The lexer handles nested brackets via OPTION_MODE push/pop.
// ---------------------------------------------------------------------------

tikz_options
    : LBRACK option_list? OPT_RBRACK
    ;

option_list
    : option_item (OPT_COMMA option_item)* OPT_COMMA?
    ;

// Each option is  key  or  key=value.
// Both key and value are OPT_TEXT tokens; nested brackets are OPT_LBRACK … OPT_RBRACK.
option_item
    : option_atom (OPT_EQ option_atom)?
    ;

// An option atom is plain text or a nested bracket group
opt_brace_text
    : OPT_LBRACE brace_item* BRACE_RBRACE
    ;

option_atom
    : (OPT_TEXT | opt_brace_text | OPT_LBRACK option_list? OPT_RBRACK)+
    ;
