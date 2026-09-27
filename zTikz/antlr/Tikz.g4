// =============================================================================
// Tikz.g4 — ANTLR4 grammar for TikZ 
// Key differences from the original:
//   - Removed ANTLR3 AST rewrite rules (-> ^(...))
//   - Removed embedded C#/Java code blocks
//   - Replaced ANTLR3 options block with ANTLR4 equivalents
//   - Uses ANTLR4 lexer modes for option brackets and text braces
// =============================================================================
grammar Tikz;

// ---------------------------------------------------------------------------
// PARSER RULES
// ---------------------------------------------------------------------------

// Top-level document: may contain preamble commands and one tikzpicture
document
    : (tikzpicture | skip_token)* EOF
    ;

// Tokens to skip at the document level (preamble etc.)
skip_token
    : ANY
    | NUMBER
    | ID
    | SEMI
    | COLON
    | COMMA
    | DASH_DASH
    | DASH_ARROW
    | PIPE_DASH
    | DASH_PIPE
    | DOT_DOT
    | LPAREN
    | RPAREN
    | COMMAND
    ;

// The tikzpicture environment
tikzpicture
    : BEGIN_TIKZ tikz_options? tikzbody? END_TIKZ
    ;

// Body of a tikzpicture — a sequence of statements
tikzbody
    : tikz_stmt+
    ;

// A single statement inside the tikzpicture
tikz_stmt
    : path_cmd       // \draw, \fill, \path, \node, etc.
    | tikz_options   // standalone options block [...]
    | skip_body      // anything else we don't understand yet
    ;

// Tokens to skip inside the tikzpicture body
skip_body
    : ANY
    | NUMBER
    | ID
    | SEMI
    | COLON
    | COMMA
    | DASH_DASH
    | DASH_ARROW
    | PIPE_DASH
    | DASH_PIPE
    | DOT_DOT
    | LPAREN
    | RPAREN
    | COMMAND
    ;

// ---------------------------------------------------------------------------
// PATH COMMANDS  (\draw, \fill, \path, \node, etc.)
// ---------------------------------------------------------------------------

// A full path command, terminated by semicolon
path_cmd
    : path_start tikz_options? path_element* SEMI
    ;

// Keywords that start a path/draw command
path_start
    : DRAW        // \draw
    | FILL        // \fill
    | PATHCMD     // \path
    | CLIP        // \clip
    | NODE_CMD    // \node (standalone node)
    | FILLDRAW    // \filldraw
    | PATTERN     // \pattern
    | SHADE       // \shade
    | SHADEDRAW   // \shadedraw
    ;

// Elements that can appear along a path
path_element
    : coordinate              // (x,y) or (name)
    | shape_spec              // rectangle/circle/ellipse/grid/parabola
    | arc_spec                // arc(...)
    | control_spec            // .. controls (p1) and (p2) ..
    | node_inline             // node [opts] {label}
    | edge_op                 // --, ->, |-. -|
    | tikz_options            // [opts] inline
    | CYCLE                   // -- cycle
    | PLOT tikz_options? COORDINATES        // plot coordinates — skip plotting, visitor collects coords below
    ;

// ---------------------------------------------------------------------------
// SHAPE SPECS  (what follows a coordinate on a path)
// ---------------------------------------------------------------------------

shape_spec
    : RECTANGLE coordinate                          // (p1) rectangle (p2)
    | CIRCLE    tikz_options? circle_size?          // circle (r)
    | ELLIPSE   tikz_options? ellipse_size?         // ellipse (rx and ry)
    | GRID      tikz_options? coordinate            // grid (p2)
    | PARABOLA  tikz_options? coordinate            // parabola (p)
    ;

// Circle size: ( number )
circle_size
    : LPAREN numberunit RPAREN
    ;

// Ellipse size: ( rx and ry )
ellipse_size
    : LPAREN numberunit AND numberunit RPAREN
    ;

// ---------------------------------------------------------------------------
// ARC  arc(start:end:radius)
// ---------------------------------------------------------------------------

arc_spec
    : ARC tikz_options? LPAREN arc_params RPAREN
    ;

// start : end : radius   (all numbers, optional 'and' for x/y radii)
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
// NODE  (inline: node [opts] {text}, or standalone: \node ...)
// ---------------------------------------------------------------------------

node_inline
    : NODE tikz_options? (AT coordinate)? brace_text
    ;

// Balanced brace content {  any text or nested braces  }
brace_text
    : LBRACE brace_item* RBRACE
    ;

brace_item
    : brace_text        // nested braces
    | BRACE_CONTENT     // any text/tokens inside braces
    ;

// ---------------------------------------------------------------------------
// EDGE OPS
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

// Either  x,y  or  a node name
coord_value
    : numberunit COMMA numberunit    // (x,y)
    | ID                             // (nodename)
    ;

// ---------------------------------------------------------------------------
// NUMBERS AND UNITS
// ---------------------------------------------------------------------------

// A number optionally followed by a unit (cm, pt, mm, in, em, ex)
numberunit
    : NUMBER unit?
    ;

unit
    : ID    // cm, pt, mm, in, em, ex  — captured as ID in the lexer
    ;

// ---------------------------------------------------------------------------
// OPTIONS  [key=value, key, ...]
// ---------------------------------------------------------------------------

// Opening bracket is a regular token; content is tokenised in OPTION_MODE
tikz_options
    : LBRACK opt_item* RBRACK
    ;

// Items inside the options list
opt_item
    : OPT_TEXT                              // plain key or value text
    | OPT_EQ                               // =
    | OPT_COMMA                            // ,
    | LBRACK opt_item* RBRACK              // nested [...]
    ;

// ---------------------------------------------------------------------------
// LEXER RULES
// ---------------------------------------------------------------------------

// ---- TikZ environment delimiters ----
BEGIN_TIKZ : '\\begin{tikzpicture}' ;
END_TIKZ   : '\\end{tikzpicture}'  ;

// ---- Path command keywords ----
DRAW      : '\\draw'              ;
FILL      : '\\fill'              ;
PATHCMD   : '\\path'              ;
CLIP      : '\\clip'              ;
NODE_CMD  : '\\node'              ;
FILLDRAW  : '\\filldraw'          ;
PATTERN   : '\\pattern'           ;
SHADE     : '\\shade'             ;
SHADEDRAW : '\\shadedraw'         ;

// ---- Shape & path keywords ----
RECTANGLE  : 'rectangle'  ;
CIRCLE     : 'circle'     ;
ELLIPSE    : 'ellipse'    ;
GRID       : 'grid'       ;
PARABOLA   : 'parabola'   ;
ARC        : 'arc'        ;
CONTROLS   : 'controls'   ;
AND        : 'and'        ;
NODE       : 'node'       ;
AT         : 'at'         ;
CYCLE      : 'cycle'      ;
PLOT       : 'plot'       ;
COORDINATES: 'coordinates';

// ---- Operators ----
DASH_DASH  : '--'  ;
DASH_ARROW : '->'  ;
PIPE_DASH  : '|-'  ;
DASH_PIPE  : '-|'  ;
DOT_DOT    : '..'  ;

// ---- Punctuation ----
SEMI   : ';' ;
COLON  : ':' ;
COMMA  : ',' ;
LPAREN : '(' ;
RPAREN : ')' ;
PLUS   : '+' ;

// ---- Brace content (handled with lexer mode) ----
LBRACE : '{' -> pushMode(BRACE_MODE) ;
RBRACE : '}' ;   // unmatched } — shouldn't normally appear in default mode

// ---- Options bracket (handled with lexer mode) ----
LBRACK : '[' -> pushMode(OPTION_MODE) ;
RBRACK : ']' ;   // unmatched ] — shouldn't normally appear in default mode

// ---- Numbers ----
// Supports: 1  1.5  .5  -1  -1.5  -.5
NUMBER
    : '-'? [0-9]+ ('.' [0-9]*)?
    | '-'? '.' [0-9]+
    ;

// ---- Identifiers and generic LaTeX commands ----
// Covers node names, unit names (cm, pt...), style names
ID : [a-zA-Z_][a-zA-Z0-9_]* ;

// ---- Generic LaTeX command: \something  (not one of the above) ----
COMMAND : '\\' [a-zA-Z]+ ;

// ---- Whitespace: skip silently ----
WS : [ \t\r\n]+ -> skip ;

// ---- Comments: % ... end-of-line ----
COMMENT : '%' ~[\r\n]* -> skip ;

// ---- Catch-all: single character we don't recognise ----
ANY : . ;

// ===========================================================================
// LEXER MODE: OPTION_MODE  — inside [ ... ]
// Handles nested brackets.  All text is captured as OPT_TEXT tokens so the
// parser/visitor can inspect key=value pairs.
// ===========================================================================
mode OPTION_MODE;

// Nested open bracket — push another OPTION_MODE
OPT_LBRACK : '[' -> pushMode(OPTION_MODE) ;

// Close bracket — pop back to the enclosing mode (or default)
RBRACK : ']' -> popMode ;

OPT_EQ     : '='  ;
OPT_COMMA  : ','  ;
OPT_WS     : [ \t\r\n]+ -> skip ;

// Any text that is not a special option character
OPT_TEXT   : ~[ \t\r\n\[\]=,]+ ;

// ===========================================================================
// LEXER MODE: BRACE_MODE  — inside { ... }
// Nested braces are handled by pushing/popping the mode.
// Everything inside is collected as BRACE_CONTENT (raw text).
// ===========================================================================
mode BRACE_MODE;

TXT_LBRACE : '{' -> pushMode(BRACE_MODE) ;
TXT_RBRACE : '}' -> popMode ;

// Give the parser grammar aliases that match what it expects
LBRACE     : '{' -> pushMode(BRACE_MODE) ;  // re-open — alias for TXT_LBRACE? No – handled by TXT_LBRACE
RBRACE     : '}' -> popMode ;               // alias for TXT_RBRACE? No

// Any text inside the braces (not a brace itself)
BRACE_CONTENT : ~[{}]+ ;
