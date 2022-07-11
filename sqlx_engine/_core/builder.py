from typing import Any, Dict, List, Optional, Tuple, Type, Union

LiteralString = str


import json
import logging
from abc import ABC
from textwrap import indent

log: logging.Logger = logging.getLogger(__name__)

ChildType = Union["AbstractNode", str]
ITERABLES: Tuple[Type[Any], ...] = (list, tuple, set)


class QueryBuilder:
    method: str
    operation: str
    model: Optional[str]
    include: Optional[Dict[str, Any]]
    arguments: Dict[str, Any]
    root_selection: Optional[List[str]]

    __slots__ = (
        "method",
        "operation",
        "model",
        "include",
        "arguments",
        "root_selection",
    )

    def __init__(
        self,
        *,
        method: str,
        operation: str,
        arguments: Dict[str, Any],
        model: Optional[str] = None,
        root_selection: Optional[List[str]] = None,
    ) -> None:
        self.model = model
        self.method = method
        self.operation = operation
        self.root_selection = root_selection
        self.arguments = arguments
        self.include = arguments.pop("include", None)

    def build(self) -> str:
        data = {
            "variables": {},
            "operation_name": self.operation,
            "query": self.build_query(),
        }
        return dumps(data)

    def build_query(self) -> str:
        query = self._create_root_node().render()
        log.debug("Generated query: \n%s", query)
        return query

    def _create_root_node(self) -> "RootNode":
        root = RootNode(builder=self)
        root.add(ResultNode.create(self))
        root.add(
            Selection.create(
                self,
                model=self.model,
                include=self.include,
                root_selection=self.root_selection,
            )
        )
        return root


class AbstractNode(ABC):
    __slots__ = ()

    def should_render(self) -> bool:
        """If True, rendering of the node is skipped

        Useful for some nodes as they should only actually
        be rendered if they have any children.
        """
        return True


class Node(AbstractNode):
    """Base node handling rendering of child nodes"""

    joiner: str
    indent: str
    builder: QueryBuilder
    children: List[ChildType]

    __slots__ = (
        "joiner",
        "indent",
        "builder",
        "children",
    )

    def __init__(
        self,
        builder: QueryBuilder,
        *,
        joiner: str = "\n",
        indent: str = "  ",
        children: Optional[List[ChildType]] = None,
    ) -> None:
        self.builder = builder
        self.joiner = joiner
        self.indent = indent
        self.children = children if children is not None else []

    def render(self) -> Optional[str]:
        """Render the node and it's children and to string.

        Rendering a node involves 4 steps:

        1. Entering the node
        2. Rendering it's children
        3. Departing the node
        4. Joining the previous steps together into a single string
        """
        if not self.should_render():
            return None

        strings: List[str] = []
        entered = self.enter()
        if entered is not None:
            strings.append(entered)

        for child in self.children:
            content: Optional[str] = None

            if isinstance(child, str):
                content = child
            else:
                content = child.render()

            if content:
                strings.append(indent(content, self.indent))

        departed = self.depart()
        if departed is not None:
            strings.append(departed)

        return self.joiner.join(strings)

    def add(self, child: ChildType) -> None:
        """Add a child"""
        self.children.append(child)

    @classmethod
    def create(cls, builder: Optional[QueryBuilder] = None, **kwargs: Any) -> "Node":
        """Create the node and its children

        This is useful for subclasses that add extra attributes in __init__
        """
        kwargs.setdefault("builder", builder)
        node = cls(**kwargs)
        node.children.extend(node.create_children())
        return node


class RootNode(Node):
    __slots__ = ()

    def enter(self) -> str:
        return f"{self.builder.operation} {{"

    def depart(self) -> str:
        return "}"

    def render(self) -> str:
        content = super().render()
        return content


class ResultNode(Node):
    __slots__ = ()

    def __init__(self, indent: str = "", **kwargs: Any) -> None:
        super().__init__(indent=indent, **kwargs)

    def enter(self) -> str:
        # self.builder.model is None, model is empty string.
        model = self.builder.model or ""
        result = f"result: {self.builder.method}{model}"
        return result

    def depart(self) -> Optional[str]:
        return None

    def create_children(self) -> List[ChildType]:
        return [
            Arguments.create(
                self.builder,
                arguments=self.builder.arguments,
            )
        ]


class Arguments(Node):
    arguments: Dict[str, Any]

    __slots__ = ("arguments",)

    def __init__(self, arguments: Dict[str, Any], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.arguments = arguments

    def should_render(self) -> bool:
        return bool(self.children)

    def enter(self) -> str:
        return "("

    def depart(self) -> str:
        return ")"

    def create_children(
        self, arguments: Optional[Dict[str, Any]] = None
    ) -> List[ChildType]:
        children: List[ChildType] = []

        for arg, value in self.arguments.items():
            if isinstance(value, ITERABLES):
                children.append(f"{arg}: {dumps(dumps(value))}")
            else:
                children.append(f"{arg}: {dumps(value)}")

        return children


class Selection(Node):
    model: Optional[str]
    include: Optional[Dict[str, Any]]
    root_selection: Optional[List[str]]

    __slots__ = (
        "model",
        "include",
        "root_selection",
    )

    def __init__(
        self,
        model: Optional[str] = None,
        include: Optional[Dict[str, Any]] = None,
        root_selection: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.model = model
        self.include = include
        self.root_selection = root_selection

    def should_render(self) -> bool:
        return bool(self.children)

    def create_children(self) -> List[ChildType]:
        children: List[ChildType] = []
        return children


def dumps(obj: Any, **kwargs: Any) -> str:
    kwargs.setdefault("ensure_ascii", False)
    return json.dumps(obj, **kwargs)
