// =============================================================================
// TikzLexer.g4 — ANTLR4 Lexer grammar for TikZ
//
// Key design decisions:
//  - Two lexer MODES are used:
//      OPTION_MODE : activated by '[', handles key=value option lists.
//      BRACE_MODE  : activated by '{', collects node label text as raw tokens.
//  - Comments (%) and whitespace are skipped.
//  - A catch-all ANY token absorbs anything the parser skips over (preamble, etc.)
// =============================================================================
lexer grammar TikzLexer;

// ---------------------------------------------------------------------------
// DEFAULT MODE
// ---------------------------------------------------------------------------

// TikZ picture environment delimiters
BEGIN_TIKZ  : '\\begin{tikzpicture}'   ;
END_TIKZ    : '\\end{tikzpicture}'     ;

// Path / draw command starters  (\draw, \fill, \path, etc.)
DRAW        : '\\draw'                 ;
FILL        : '\\fill'                 ;
PATHCMD     : '\\path'                 ;
CLIP        : '\\clip'                 ;
NODE_CMD    : '\\node'                 ;
FILLDRAW    : '\\filldraw'             ;
PATTERN     : '\\pattern'              ;
SHADE       : '\\shade'                ;
SHADEDRAW   : '\\shadedraw'            ;

// Shape and path keywords
RECTANGLE   : 'rectangle'             ;
CIRCLE      : 'circle'                ;
ELLIPSE     : 'ellipse'               ;
GRID        : 'grid'                  ;
PARABOLA    : 'parabola'              ;
ARC         : 'arc'                   ;
CONTROLS    : 'controls'              ;
AND         : 'and'                   ;
NODE        : 'node'                  ;
AT          : 'at'                    ;
CYCLE       : 'cycle'                 ;
PLOT        : 'plot'                  ;
COORDINATES : 'coordinates'           ;

// Path operators
DASH_DASH   : '--'                     ;
DASH_ARROW  : '->'                     ;
PIPE_DASH   : '|-'                     ;
DASH_PIPE   : '-|'                     ;
DOT_DOT     : '..'                     ;

// Punctuation
SEMI        : ';'                      ;
COLON       : ':'                      ;
COMMA       : ','                      ;
LPAREN      : '('                      ;
RPAREN      : ')'                      ;
PLUS        : '+'                      ;

// '[' triggers OPTION_MODE to collect key=value option lists
LBRACK      : '['  -> pushMode(OPTION_MODE) ;

// '{' triggers BRACE_MODE to collect node label text
LBRACE      : '{'  -> pushMode(BRACE_MODE)  ;

// Unmatched '}' at document level (shouldn't appear normally)
RBRACE      : '}'                      ;

// Numbers: supports  1  1.5  .5  -1  -1.5  -.5
NUMBER
    : '-'? [0-9]+ ('.' [0-9]*)?
    | '-'? '.' [0-9]+
    ;

// Identifiers: node names, unit names (cm, pt, mm…), style names
ID : [a-zA-Z_][a-zA-Z0-9_]* ;

// Any other LaTeX command not matched above (e.g. \tikzstyle, \usepath, …)
COMMAND : '\\' [a-zA-Z]+ ;

// Whitespace — skip
WS : [ \t\r\n]+ -> skip ;

// Line comments — skip
COMMENT : '%' ~[\r\n]* -> skip ;

// Catch-all: absorb any single character the parser doesn't recognise.
// The parser uses this to gracefully skip unknown preamble/body tokens.
ANY : . ;


// ===========================================================================
// LEXER MODE: OPTION_MODE  — inside [ ... ]
//
// Handles nested brackets (e.g. [line width={2pt}]).
// All text tokens are OPT_TEXT; the visitor reconstructs key=value pairs.
// ===========================================================================
mode OPTION_MODE;

// Nested '[' — push another OPTION_MODE level
OPT_LBRACK  : '['  -> pushMode(OPTION_MODE) ;

// ']' — pop back to the enclosing mode
OPT_RBRACK  : ']'  -> popMode              ;
OPT_LBRACE  : '{'  -> pushMode(BRACE_MODE)  ;

OPT_EQ      : '='                          ;
OPT_COMMA   : ','                          ;

// Whitespace inside options — skip
OPT_WS      : [ \t\r\n]+  -> skip         ;

// Any text that is NOT a bracket, equals, comma, or whitespace.
// Note: In ANTLR4 character class, '[' does not need escaping;
//       ']' is escaped as '\]' to avoid closing the class.
OPT_TEXT    : ~[ \t\r\n\][=,]+            ;


// ===========================================================================
// LEXER MODE: BRACE_MODE  — inside { ... }
//
// Handles nested braces for node labels and tikzstring content.
// Nested '{' pushes another BRACE_MODE; '}' pops back.
// Everything else is captured as BRACE_CONTENT.
// ===========================================================================
mode BRACE_MODE;

// Nested '{' — push another BRACE_MODE level
BRACE_LBRACE   : '{'  -> pushMode(BRACE_MODE) ;

// '}' — pop back to the enclosing mode
BRACE_RBRACE   : '}'  -> popMode              ;

// All content inside the braces (not a brace character itself)
BRACE_CONTENT  : ~[{}]+                        ;
