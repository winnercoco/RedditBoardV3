"""
utils/query_parser.py

Part 1A
--------

Tokenizer
Expression AST
Value AST
Recursive Descent Parser (Skeleton)

Part 2 will implement the evaluator.

Grammar
-------

expression
    := or_expression

or_expression
    := and_expression ('OR' and_expression)*

and_expression
    := not_expression ('AND' not_expression)*

not_expression
    := NOT not_expression
     | primary

primary
    := comparison
     | '(' expression ')'

comparison
    := IDENT comparator rhs

rhs
    := literal
     | '(' value_expression ')'

value_expression
    := value_or

(value parser implemented in Part 1B)
"""

from __future__ import annotations

import re

from dataclasses import dataclass
from typing import List, Optional, Any


#####################################################################
# Token Definitions
#####################################################################

TOKEN_SPEC = [

    ("SPACE", r"\s+"),

    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("COMMA", r","),

    ("GTE", r">="),
    ("LTE", r"<="),
    ("NE", r"!="),
    ("REGEX", r"~="),
    ("GT", r">"),
    ("LT", r"<"),
    ("EQ", r"="),

    ("AND", r"\bAND\b"),
    ("OR", r"\bOR\b"),
    ("NOT", r"\bNOT\b"),
    ("IN", r"\bIN\b"),

    ("NUMBER", r"\d+(\.\d+)?"),

    ("STRING", r'"[^"]*"|\'[^\']*\''),

    (
        "IDENT",
        r"[A-Za-z0-9_\-\*\./:+]+"
    ),
]


MASTER_REGEX = re.compile(
    "|".join(
        f"(?P<{name}>{pattern})"
        for name, pattern in TOKEN_SPEC
    ),
    re.IGNORECASE,
)


#####################################################################
# Token
#####################################################################

@dataclass
class Token:

    type: str

    value: str


#####################################################################
# Tokenizer
#####################################################################

def tokenize(query: str) -> List[Token]:

    tokens = []

    pos = 0

    while pos < len(query):

        match = MASTER_REGEX.match(query, pos)

        if not match:
            raise SyntaxError(
                f"Unexpected character near:\n{query[pos:]}"
            )

        kind = match.lastgroup
        value = match.group()

        pos = match.end()

        if kind == "SPACE":
            continue

        if kind == "STRING":
            value = value[1:-1]

        if kind in ("AND", "OR", "NOT", "IN"):
            value = value.upper()

        tokens.append(
            Token(kind, value)
        )

    return tokens


#####################################################################
# AST Base Classes
#####################################################################

class Node:

    """
    Base expression node.
    """

    def evaluate(self, record):
        raise NotImplementedError()


class ValueNode:

    """
    Base value node.
    """

    pass


#####################################################################
# Expression AST
#####################################################################

@dataclass
class AndNode(Node):

    left: Node
    right: Node


@dataclass
class OrNode(Node):

    left: Node
    right: Node


@dataclass
class NotNode(Node):

    child: Node


@dataclass
class ComparisonNode(Node):

    field: str

    operator: str

    value_tree: ValueNode


#####################################################################
# Value AST
#####################################################################

@dataclass
class LiteralValue(ValueNode):

    value: Any


@dataclass
class ValueAnd(ValueNode):

    left: ValueNode
    right: ValueNode


@dataclass
class ValueOr(ValueNode):

    left: ValueNode
    right: ValueNode


@dataclass
class ValueNot(ValueNode):

    child: ValueNode


#####################################################################
# Parser
#####################################################################

class Parser:

    def __init__(self, tokens: List[Token]):

        self.tokens = tokens

        self.pos = 0

    #############################################################

    def current(self) -> Optional[Token]:

        if self.pos >= len(self.tokens):
            return None

        return self.tokens[self.pos]

    #############################################################

    def peek(self, offset=1):

        idx = self.pos + offset

        if idx >= len(self.tokens):
            return None

        return self.tokens[idx]

    #############################################################

    def consume(self, expected=None):

        token = self.current()

        if token is None:
            raise SyntaxError(
                "Unexpected end of query."
            )

        if expected and token.type != expected:

            raise SyntaxError(
                f"Expected {expected}, "
                f"received {token.type}"
            )

        self.pos += 1

        return token

    #############################################################
    # Entry
    #############################################################

    def parse(self):

        expr = self.parse_or()

        if self.current() is not None:

            raise SyntaxError(
                f"Unexpected token '{self.current().value}'"
            )

        return expr

    #############################################################
    # OR
    #############################################################

    def parse_or(self):

        node = self.parse_and()

        while True:

            token = self.current()

            if token and token.type == "OR":

                self.consume("OR")

                node = OrNode(
                    node,
                    self.parse_and()
                )

            else:
                break

        return node

    #############################################################
    # AND
    #############################################################

    def parse_and(self):

        node = self.parse_not()

        while True:

            token = self.current()

            if token and token.type == "AND":

                self.consume("AND")

                node = AndNode(
                    node,
                    self.parse_not()
                )

            else:
                break

        return node

    #############################################################
    # NOT
    #############################################################

    def parse_not(self):

        token = self.current()

        if token and token.type == "NOT":

            self.consume("NOT")

            return NotNode(
                self.parse_not()
            )

        return self.parse_primary()

    #############################################################
    # Primary
    #############################################################

    def parse_primary(self):

        token = self.current()

        if token is None:
            raise SyntaxError(
                "Unexpected end of query."
            )

        if token.type == "LPAREN":

            self.consume("LPAREN")

            expr = self.parse_or()

            self.consume("RPAREN")

            return expr

        return self.parse_comparison()

# TAKEN CONTENTS FROM PART 1B SINCE THERE WERE STUBS    
#####################################################################
# Comparison Parser
#####################################################################

    def parse_comparison(self):

        field = self.consume("IDENT").value.lower()

        operator = self.current()

        if operator is None:
            raise SyntaxError(
                "Expected comparison operator."
            )

        self.consume()

        # ---------------------------------------------------------
        # IN (...)
        # Convert to OR tree
        # ---------------------------------------------------------

        if operator.type == "IN":

            value_tree = self.parse_in_list()

            return ComparisonNode(
                field=field,
                operator="EQ",
                value_tree=value_tree
            )

        # ---------------------------------------------------------
        # = (...)
        # != (...)
        # ~= (...)
        # ---------------------------------------------------------

        if self.current() and self.current().type == "LPAREN":

            self.consume("LPAREN")

            value_tree = self.parse_value_expression()

            self.consume("RPAREN")

        else:

            value_tree = self.parse_literal()

        return ComparisonNode(
            field=field,
            operator=operator.type,
            value_tree=value_tree
        )

#####################################################################
# Value Expression
#####################################################################

    def parse_value_expression(self):

        return self.parse_value_or()

#####################################################################

    def parse_value_or(self):

        node = self.parse_value_and()

        while True:

            token = self.current()

            if token and token.type == "OR":

                self.consume("OR")

                node = ValueOr(
                    node,
                    self.parse_value_and()
                )

            else:
                break

        return node

#####################################################################

    def parse_value_and(self):

        node = self.parse_value_not()

        while True:

            token = self.current()

            if token and token.type == "AND":

                self.consume("AND")

                node = ValueAnd(
                    node,
                    self.parse_value_not()
                )

            else:
                break

        return node

#####################################################################

    def parse_value_not(self):

        token = self.current()

        if token and token.type == "NOT":

            self.consume("NOT")

            return ValueNot(
                self.parse_value_not()
            )

        return self.parse_value_primary()

#####################################################################

    def parse_value_primary(self):

        token = self.current()

        if token is None:
            raise SyntaxError(
                "Unexpected end of value expression."
            )

        if token.type == "LPAREN":

            self.consume("LPAREN")

            node = self.parse_value_expression()

            self.consume("RPAREN")

            return node

        return self.parse_literal()

#####################################################################
# Literal
#####################################################################

    def parse_literal(self):

        token = self.current()

        if token is None:
            raise SyntaxError(
                "Expected value."
            )

        if token.type == "NUMBER":

            self.consume()

            if "." in token.value:
                value = float(token.value)
            else:
                value = int(token.value)

            return LiteralValue(value)

        if token.type in ("IDENT", "STRING"):

            self.consume()

            return LiteralValue(token.value)

        raise SyntaxError(
            f"Unexpected value '{token.value}'"
        )

#####################################################################
# IN (...)
#
# Converts
#
# IN(a,b,c)
#
# into
#
#      OR
#    /    \
#   a      OR
#         /  \
#        b    c
#
#####################################################################

    def parse_in_list(self):

        self.consume("LPAREN")

        values = []

        while True:

            values.append(
                self.parse_literal()
            )

            token = self.current()

            if token is None:
                raise SyntaxError(
                    "Expected ')' in IN clause."
                )

            if token.type == "COMMA":

                self.consume("COMMA")
                continue

            break

        self.consume("RPAREN")

        if len(values) == 0:
            raise SyntaxError(
                "IN() cannot be empty."
            )

        node = values[0]

        for value in values[1:]:

            node = ValueOr(
                node,
                value
            )

        return node

#############################################################
#############################################################
#############################################################
#############################################################
# Part 1B Part 1B Part 1B Part 1B Part 1B Part 1B Part 1B 
#############################################################
#############################################################
#############################################################
#############################################################

#####################################################################
# Public API
#####################################################################

def build_ast(query: str):

    """
    Parse a query string.

    Parameters
    ----------
    query : str

    Returns
    -------
    Node
        Root expression node.
    """

    tokens = tokenize(query)

    parser = Parser(tokens)

    return parser.parse()


#############################################################
#############################################################
#############################################################
#############################################################
# Part 2A Part 2A Part 2A Part 2A Part 2A Part 2A Part 2A
#############################################################
#############################################################
#############################################################
#############################################################

#####################################################################
#
# Part 2A
#
# Evaluation Helpers
#
#####################################################################

import fnmatch


#####################################################################
# Fields containing lists
#####################################################################

LIST_FIELDS = {
    "star",
    "categories",
    "positions",
}


#####################################################################
# Normalization
#####################################################################

def normalize_string(value):
    """
    Case-insensitive normalization.

    Display values are never modified.
    """

    if value is None:
        return ""

    return str(value).casefold().strip()


#####################################################################
# Numeric Helper
#####################################################################

def is_numeric(value):

    return isinstance(value, (int, float))


#####################################################################
# Wildcard
#####################################################################

def wildcard_match(pattern, candidate):
    """
    Supports

        *

    Examples

        Ana*

        *Katana

        *heels*
    """

    pattern = normalize_string(pattern)
    candidate = normalize_string(candidate)

    return fnmatch.fnmatch(candidate, pattern)


#####################################################################
# Literal Comparison
#####################################################################

def literal_matches(candidate, literal):
    """
    Match a single literal.

    Supports

    exact

    wildcard
    """

    if is_numeric(candidate):

        return candidate == literal

    candidate = normalize_string(candidate)
    literal = normalize_string(literal)

    if "*" in literal:

        return wildcard_match(
            literal,
            candidate
        )

    return candidate == literal


#####################################################################
# Value Tree Evaluation
#####################################################################

def evaluate_value_tree(
    node,
    candidate,
):
    """
    Evaluate a Value AST.

    candidate may be

        scalar

    or

        list
    """

    ###############################################################
    # Literal
    ###############################################################

    if isinstance(node, LiteralValue):

        value = node.value

        if isinstance(candidate, list):

            for item in candidate:

                if literal_matches(
                    item,
                    value
                ):
                    return True

            return False

        return literal_matches(
            candidate,
            value
        )

    ###############################################################
    # AND
    ###############################################################

    if isinstance(node, ValueAnd):

        return (

            evaluate_value_tree(
                node.left,
                candidate
            )

            and

            evaluate_value_tree(
                node.right,
                candidate
            )

        )

    ###############################################################
    # OR
    ###############################################################

    if isinstance(node, ValueOr):

        return (

            evaluate_value_tree(
                node.left,
                candidate
            )

            or

            evaluate_value_tree(
                node.right,
                candidate
            )

        )

    ###############################################################
    # NOT
    ###############################################################

    if isinstance(node, ValueNot):

        return not evaluate_value_tree(
            node.child,
            candidate
        )

    raise TypeError(
        f"Unknown ValueNode: {type(node)}"
    )


#####################################################################
# Field Helpers
#####################################################################

def get_record_value(
    record,
    field,
):
    """
    Safe field lookup.

    Returns

        ""

    if field is missing.
    """

    if field not in record:

        if field in LIST_FIELDS:
            return []

        return ""

    return record[field]


#####################################################################
# Regex
#####################################################################

def regex_match(
    pattern,
    candidate,
):
    """
    Regex comparison.

    Scalars and list fields supported.
    """

    try:

        regex = re.compile(
            pattern,
            re.IGNORECASE
        )

    except re.error:

        return False

    if isinstance(candidate, list):

        return any(

            regex.search(
                normalize_string(x)
            )

            for x in candidate

        )

    return regex.search(

        normalize_string(candidate)

    ) is not None

#############################################################
#############################################################
#############################################################
#############################################################
# Part 2B Part 2B Part 2B Part 2B Part 2B Part 2B Part 2B
#############################################################
#############################################################
#############################################################
#############################################################

#####################################################################
#
# Part 2B
#
# Expression Evaluator
#
#####################################################################


#####################################################################
# Comparison Evaluation
#####################################################################

def evaluate_comparison(node, record):
    """
    Evaluate a ComparisonNode.
    """

    field = node.field
    operator = node.operator

    candidate = get_record_value(record, field)

    # -------------------------------------------------------------
    # Regex
    # -------------------------------------------------------------

    if operator == "REGEX":

        if not isinstance(node.value_tree, LiteralValue):
            return False

        return regex_match(
            node.value_tree.value,
            candidate
        )

    # -------------------------------------------------------------
    # Equality
    # -------------------------------------------------------------

    if operator == "EQ":

        return evaluate_value_tree(
            node.value_tree,
            candidate
        )

    # -------------------------------------------------------------
    # Not Equal
    # -------------------------------------------------------------

    if operator == "NE":

        return not evaluate_value_tree(
            node.value_tree,
            candidate
        )

    # -------------------------------------------------------------
    # Numeric Comparisons
    # -------------------------------------------------------------

    if isinstance(candidate, list):
        return False

    if not isinstance(node.value_tree, LiteralValue):
        return False

    try:

        left = float(candidate)
        right = float(node.value_tree.value)

    except Exception:
        return False

    if operator == "GT":
        return left > right

    if operator == "GTE":
        return left >= right

    if operator == "LT":
        return left < right

    if operator == "LTE":
        return left <= right

    return False


#####################################################################
# Expression Evaluation
#####################################################################

def evaluate_node(node, record):
    """
    Recursively evaluates an expression tree.
    """

    ###############################################################

    if isinstance(node, ComparisonNode):

        return evaluate_comparison(
            node,
            record
        )

    ###############################################################

    if isinstance(node, AndNode):

        return (

            evaluate_node(
                node.left,
                record
            )

            and

            evaluate_node(
                node.right,
                record
            )

        )

    ###############################################################

    if isinstance(node, OrNode):

        return (

            evaluate_node(
                node.left,
                record
            )

            or

            evaluate_node(
                node.right,
                record
            )

        )

    ###############################################################

    if isinstance(node, NotNode):

        return not evaluate_node(
            node.child,
            record
        )

    ###############################################################

    raise TypeError(
        f"Unknown AST Node: {type(node)}"
    )


#####################################################################
# Public Record Evaluation
#####################################################################

def evaluate_record(
    query,
    record,
):
    """
    Evaluate one record.

    Parameters
    ----------
    query : str

    record : dict

    Returns
    -------
    bool
    """

    ast = build_ast(query)

    return evaluate_node(
        ast,
        record
    )


#####################################################################
# DataFrame Integration
#####################################################################

def apply_advanced_query(
    df,
    query,
):
    """
    Apply the advanced query to a dataframe.

    Invalid query -> original dataframe
    """

    if query is None:
        return df

    query = query.strip()

    if query == "":
        return df

    try:

        ast = build_ast(query)

    except Exception as e:

        print(e)

        return df

    mask = []

    for _, row in df.iterrows():

        record = row.to_dict()

        try:

            result = evaluate_node(
                ast,
                record
            )

        except Exception:

            result = False

        mask.append(result)

    return (

        df.loc[mask]
        .reset_index(drop=True)

    )


#####################################################################
# Debug Helper
#####################################################################

def print_ast(query):
    """
    Quick debug helper.
    """

    ast = build_ast(query)

    print(ast)


#############################################################
#############################################################
#############################################################
#############################################################
# Part 3 Part 3 Part 3 Part 3 Part 3 Part 3 Part 3 Part 3 Part 3 
#############################################################
#############################################################
#############################################################
#############################################################

#####################################################################
# AST Pretty Printer
#####################################################################

def pretty_print_ast(node, indent=0):
    """
    Pretty-print an AST for debugging.
    """

    prefix = "  " * indent

    if isinstance(node, ComparisonNode):
        print(f"{prefix}{node.field} {node.operator}")
        print_ast(node.value_tree, indent + 1)
        return

    if isinstance(node, AndNode):
        print(f"{prefix}AND")
        print_ast(node.left, indent + 1)
        print_ast(node.right, indent + 1)
        return

    if isinstance(node, OrNode):
        print(f"{prefix}OR")
        print_ast(node.left, indent + 1)
        print_ast(node.right, indent + 1)
        return

    if isinstance(node, NotNode):
        print(f"{prefix}NOT")
        print_ast(node.child, indent + 1)
        return

    if isinstance(node, LiteralValue):
        print(f"{prefix}{node.value}")
        return

    if isinstance(node, ValueAnd):
        print(f"{prefix}VALUE AND")
        print_ast(node.left, indent + 1)
        print_ast(node.right, indent + 1)
        return

    if isinstance(node, ValueOr):
        print(f"{prefix}VALUE OR")
        print_ast(node.left, indent + 1)
        print_ast(node.right, indent + 1)
        return

    if isinstance(node, ValueNot):
        print(f"{prefix}VALUE NOT")
        print_ast(node.child, indent + 1)
        return

    print(f"{prefix}{node}")