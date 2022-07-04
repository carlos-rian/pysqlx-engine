from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, Type, Union

LiteralString = str


import inspect
import json
import logging
from abc import ABC, abstractmethod
from functools import singledispatch
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

    @abstractmethod
    def render(self) -> Optional[str]:
        """Render the node to a string

        None is returned if the node should not be rendered.
        """
        ...

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

    def enter(self) -> Optional[str]:
        """Get the string used to enter the node.

        This string will be rendered *before* the children.
        """
        return None

    def depart(self) -> Optional[str]:
        """Get the string used to depart the node.

        This string will be rendered *after* the children.
        """
        return None

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

    def create_children(self) -> List[ChildType]:
        """Create the node's children

        If children are passed to the constructor, the children
        returned from this method are used to extend the already
        set children.
        """
        return []

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
        if not content:
            raise RuntimeError("Could not generate query.")
        return content


class ResultNode(Node):
    __slots__ = ()

    def __init__(self, indent: str = "", **kwargs: Any) -> None:
        super().__init__(indent=indent, **kwargs)

    def enter(self) -> str:
        model = self.builder.model
        if model is not None:
            return f"result: {self.builder.method}{model}"

        return f"result: {self.builder.method}"

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
            if value is None:
                # ignore None values for convenience
                continue

            if isinstance(value, dict):
                children.append(Key(arg, node=Data.create(self.builder, data=value)))
            elif isinstance(value, ITERABLES):
                # NOTE: we have a special case for execute_raw and query_raw
                # here as prisma expects parameters to be passed as a json string
                # value like "[\"John\",\"123\"]", and we encode twice to ensure
                # that only the inner quotes are escaped
                if self.builder.method in {"queryRaw", "executeRaw"}:
                    children.append(f"{arg}: {dumps(dumps(value))}")
                else:
                    children.append(
                        Key(arg, node=ListNode.create(self.builder, data=value))
                    )
            else:
                children.append(f"{arg}: {dumps(value)}")

        return children


class Data(Node):
    data: Mapping[str, Any]

    __slots__ = ("data",)

    def __init__(self, data: Mapping[str, Any], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.data = data

    def enter(self) -> str:
        return "{"

    def depart(self) -> str:
        return "}"

    def create_children(self) -> List[ChildType]:
        children: List[ChildType] = []

        for key, value in self.data.items():
            if isinstance(value, dict):
                children.append(Key(key, node=Data.create(self.builder, data=value)))
            elif isinstance(value, (list, tuple, set)):
                children.append(Key(key, node=ListNode.create(self.builder, data=value)))
            else:
                children.append(f"{key}: {dumps(value)}")

        return children


class ListNode(Node):
    data: Iterable[Any]

    __slots__ = ("data",)

    def __init__(self, data: Iterable[Any], joiner: str = ",\n", **kwargs: Any) -> None:
        super().__init__(joiner=joiner, **kwargs)
        self.data = data

    def enter(self) -> str:
        return "["

    def depart(self) -> str:
        return "]"

    def create_children(self) -> List[ChildType]:
        children: List[ChildType] = []

        for item in self.data:
            if isinstance(item, dict):
                children.append(Data.create(self.builder, data=item))
            else:
                children.append(dumps(item))

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

    def enter(self) -> str:
        return "{"

    def depart(self) -> str:
        return "}"

    def create_children(self) -> List[ChildType]:
        model = self.model
        include = self.include
        builder = self.builder
        children: List[ChildType] = []

        # root_selection, if present overrides the default fields
        # for a model as it is used by methods such as count()
        # that do not support returning model fields
        root_selection = self.root_selection
        if root_selection is not None:
            children.extend(root_selection)
        elif model is not None:
            children.extend(builder.get_default_fields(model))

        if include is not None:
            if model is None:
                raise ValueError("Cannot include fields when model is None.")

            for key, value in include.items():
                if value is True:
                    # e.g. posts { post_fields }
                    children.append(
                        Key(
                            key,
                            sep=" ",
                            node=Selection.create(
                                builder,
                                include=None,
                                model=builder.get_relational_model(
                                    current_model=model, field=key
                                ),
                            ),
                        )
                    )
                elif isinstance(value, dict):
                    # e.g. given {'posts': {where': {'published': True}}} return
                    # posts( where: { published: true }) { post_fields }
                    args = value.copy()
                    nested_include = args.pop("include", None)
                    children.extend(
                        [
                            Key(
                                key,
                                sep="",
                                node=Arguments.create(builder, arguments=args),
                            ),
                            Selection.create(
                                builder,
                                include=nested_include,
                                model=builder.get_relational_model(
                                    current_model=model, field=key
                                ),
                            ),
                        ]
                    )
                elif value is False:
                    continue
                else:
                    raise TypeError(
                        f"Expected `bool` or `dict` include value but got {type(value)} instead."
                    )

        return children


class Key(AbstractNode):
    key: str
    sep: str
    node: Node

    __slots__ = (
        "key",
        "sep",
        "node",
    )

    def __init__(self, key: str, node: Node, sep: str = ": ") -> None:
        self.key = key
        self.node = node
        self.sep = sep

    def render(self) -> str:
        content = self.node.render()
        if content:
            return f"{self.key}{self.sep}{content}"
        return f"{self.key}{self.sep}"


@singledispatch
def serializer(obj: Any):
    """Single dispatch generic function for serializing objects to JSON"""
    if inspect.isclass(obj):
        typ = obj
    else:
        typ = type(obj)

    raise TypeError(f"Type {typ} not serializable")


def dumps(obj: Any, **kwargs: Any) -> str:
    kwargs.setdefault("default", serializer)
    kwargs.setdefault("ensure_ascii", False)
    return json.dumps(obj, **kwargs)
