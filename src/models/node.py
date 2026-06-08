"""
Node models for the Cognigy Charts API.

This module contains Pydantic models for Chart Node resources including
response models, create/update request models, and chart topology models.
"""

import re
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, field_validator
from .base import CognigyBaseModel, CognigyCreateUpdateModel


# Validation patterns
OBJECT_ID_PATTERN = re.compile(r"^[a-z0-9]{24}$")
UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE
)
HEX_COLOR_PATTERN = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")

# CSS Color names (complete list from API spec)
CSS_COLOR_NAMES = {
    "aliceBlue", "antiqueWhite", "aqua", "aquamarine", "azure", "beige", "bisque",
    "black", "blanchedAlmond", "blue", "blueViolet", "brown", "burlyWood",
    "cadetBlue", "chartreuse", "chocolate", "coral", "cornflowerBlue", "cornsilk",
    "crimson", "cyan", "darkBlue", "darkCyan", "darkGoldenRod", "darkGray",
    "darkGrey", "darkGreen", "darkKhaki", "darkMagenta", "darkOliveGreen",
    "darkOrange", "darkOrchid", "darkRed", "darkSalmon", "darkSeaGreen",
    "darkSlateBlue", "darkSlateGray", "darkSlateGrey", "darkTurquoise", "darkViolet",
    "deepPink", "deepSkyBlue", "dimGray", "dimGrey", "dodgerBlue", "fireBrick",
    "floralWhite", "forestGreen", "fuchsia", "gainsboro", "ghostWhite", "gold",
    "goldenRod", "gray", "grey", "green", "greenYellow", "honeyDew", "hotPink",
    "indianRed", "indigo", "ivory", "khaki", "lavender", "lavenderBlush",
    "lawnGreen", "lemonChiffon", "lightBlue", "lightCoral", "lightCyan",
    "lightGoldenRodYellow", "lightGray", "lightGrey", "lightGreen", "lightPink",
    "lightSalmon", "lightSeaGreen", "lightSkyBlue", "lightSlateGray", "lightSlateGrey",
    "lightSteelBlue", "lightYellow", "lime", "limeGreen", "linen", "magenta",
    "maroon", "mediumAquaMarine", "mediumBlue", "mediumOrchid", "mediumPurple",
    "mediumSeaGreen", "mediumSlateBlue", "mediumSpringGreen", "mediumTurquoise",
    "mediumVioletRed", "midnightBlue", "mintCream", "mistyRose", "moccasin",
    "navajoWhite", "navy", "oldLace", "olive", "oliveDrab", "orange", "orangeRed",
    "orchid", "paleGoldenRod", "paleGreen", "paleTurquoise", "paleVioletRed",
    "papayaWhip", "peachPuff", "peru", "pink", "plum", "powderBlue", "purple",
    "rebeccaPurple", "red", "rosyBrown", "royalBlue", "saddleBrown", "salmon",
    "sandyBrown", "seaGreen", "seaShell", "sienna", "silver", "skyBlue", "slateBlue",
    "slateGray", "slateGrey", "snow", "springGreen", "steelBlue", "tan", "teal",
    "thistle", "tomato", "turquoise", "violet", "wheat", "white", "whiteSmoke",
    "yellow", "yellowGreen", "none", "transparent"
}

# Node placement modes for create
NODE_PLACEMENT_MODES = {
    "append", "prepend", "appendChild", "prependChild",
    "insertChildAt", "insertAfter", "insertBefore"
}


def _validate_object_id(value: Optional[str], field_name: str) -> Optional[str]:
    """
    Validate that a string matches MongoDB ObjectId format.
    
    Args:
        value: The string value to validate.
        field_name: Name of the field for error messages.
        
    Returns:
        The validated value if valid, None if value was None.
        
    Raises:
        ValueError: If the value doesn't match the ObjectId pattern.
    """
    if value is not None and not OBJECT_ID_PATTERN.match(value):
        raise ValueError(
            f"Invalid ObjectId format for {field_name}: "
            f"must be 24 lowercase hex characters, got '{value}'"
        )
    return value


def _validate_comment_color(value: Optional[str]) -> Optional[str]:
    """
    Validate that comment color is either a hex color or a CSS color name.
    
    Args:
        value: The color value to validate.
        
    Returns:
        The validated value if valid.
        
    Raises:
        ValueError: If the value is not a valid hex color or CSS color name.
    """
    if value is None or value == "":
        return value
    if HEX_COLOR_PATTERN.match(value):
        return value
    if value in CSS_COLOR_NAMES:
        return value
    raise ValueError(
        f"Invalid comment_color: must be a hex color (#fff or #ffffff) "
        f"or a valid CSS color name, got '{value}'"
    )


class NodeMock(CognigyBaseModel):
    """
    Mock configuration for a node.
    
    When mock mode is enabled, the mock code is executed instead of the node's
    normal behavior. Useful for testing flows without triggering actual integrations.
    
    Attributes:
        is_enabled: Whether mock mode is enabled for this node.
        code: JavaScript code to execute when mock mode is enabled.
    """
    is_enabled: Optional[bool] = Field(
        None,
        alias="isEnabled",
        description="Whether mock mode is enabled for this node"
    )
    code: Optional[str] = Field(
        None,
        description="JavaScript code to execute when mock mode is enabled"
    )


class Node(CognigyBaseModel):
    """
    Response model for a Chart Node in a Cognigy Flow.
    
    Represents a single node within a flow's chart. Used for both single-node
    GET responses and list responses. The model includes node configuration,
    display properties, and optional topology information when merged.
    
    Attributes:
        id: MongoDB ObjectId of the node (24 hex characters).
        type: Type identifier of the node (e.g., "if", "say", "think").
        reference_id: UUID reference for the node.
        extension: Extension package providing this node type (e.g., "@cognigy/basic-nodes").
        label: Custom display label replacing the default node name in the Flow Editor.
        analytics_label: Label used for analytics/reporting purposes.
        comment: Additional information or notes about the node.
        comment_color: Color for the comment display. Can be a hex color (#fff or #ffffff)
                       or a CSS color name (e.g., "aliceBlue", "none", "transparent").
        is_collapsed: Whether the node is visually collapsed in the editor.
        is_entry_point: Whether this node is an entry point for the flow.
        is_disabled: Whether the node is disabled and skipped during execution.
        config: Node-specific configuration object (varies by node type).
        locale_reference: ObjectId of the locale this node references.
        mock: Mock configuration for testing purposes.
        conversion_metadata: Metadata about field changes (only included when 
                             includeConversionMetadata=true).
        next_node_id: ID of the next sibling node (injected from topology).
        child_node_ids: List of IDs of child nodes (injected from topology).
    """
    type: Optional[str] = Field(
        None,
        description="Type identifier of the node (e.g., 'if', 'say', 'think')"
    )
    reference_id: Optional[str] = Field(
        None,
        alias="referenceId",
        description="UUID reference for the node"
    )
    extension: Optional[str] = Field(
        None,
        description="Extension package providing this node type (e.g., '@cognigy/basic-nodes')"
    )
    label: Optional[str] = Field(
        None,
        description="Custom display label replacing the default node name in the Flow Editor"
    )
    analytics_label: Optional[str] = Field(
        None,
        alias="analyticsLabel",
        description="Label used for analytics/reporting purposes"
    )
    comment: Optional[str] = Field(
        None,
        description="Additional information or notes about the node"
    )
    comment_color: Optional[str] = Field(
        None,
        alias="commentColor",
        description="Color for comment display (hex color or CSS color name)"
    )
    is_collapsed: Optional[bool] = Field(
        None,
        alias="isCollapsed",
        description="Whether the node is visually collapsed in the editor"
    )
    is_entry_point: Optional[bool] = Field(
        None,
        alias="isEntryPoint",
        description="Whether this node is an entry point for the flow"
    )
    is_disabled: Optional[bool] = Field(
        None,
        alias="isDisabled",
        description="Whether the node is disabled and skipped during execution"
    )
    config: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Node-specific configuration object (varies by node type)"
    )
    locale_reference: Optional[str] = Field(
        None,
        alias="localeReference",
        description="ObjectId of the locale this node references"
    )
    mock: Optional[NodeMock] = Field(
        None,
        description="Mock configuration for testing purposes"
    )
    conversion_metadata: Optional[Dict[str, str]] = Field(
        None,
        alias="conversionMetadata",
        description="Metadata about field changes (added, removed, updated)"
    )
    
    # Topology fields (injected by SDK merge logic, not from API directly)
    next_node_id: Optional[str] = Field(
        None,
        description="ID of the next sibling node (injected from topology)"
    )
    child_node_ids: List[str] = Field(
        default_factory=list,
        description="List of IDs of child nodes (injected from topology)"
    )

    @field_validator("reference_id")
    @classmethod
    def validate_reference_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate reference_id matches UUID format."""
        if v is not None and not UUID_PATTERN.match(v):
            raise ValueError(f"Invalid UUID format for reference_id: got '{v}'")
        return v

    @field_validator("locale_reference")
    @classmethod
    def validate_locale_reference(cls, v: Optional[str]) -> Optional[str]:
        """Validate locale_reference matches ObjectId format."""
        return _validate_object_id(v, "locale_reference")

    @field_validator("comment_color")
    @classmethod
    def validate_comment_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate comment_color is a valid hex color or CSS color name."""
        return _validate_comment_color(v)


class NodeCreate(CognigyCreateUpdateModel):
    """
    Input model for creating a Chart Node.
    
    Contains required and optional fields for creating a new node via the
    POST /v2.0/flows/{flowId}/chart/nodes endpoint.
    
    Attributes:
        type: Type identifier of the node (required). E.g., "if", "say", "think".
        target: ObjectId of the node to attach to (required). This is the previous
                or parent node depending on the mode.
        mode: Placement mode determining where the node is inserted (required).
              One of: "append", "prepend", "appendChild", "prependChild",
              "insertChildAt", "insertAfter", "insertBefore".
        position: Position index for "insertChildAt" mode (0 to 2147483647).
        extension: Extension package for this node type.
        label: Custom display label for the node.
        comment: Additional notes about the node.
        comment_color: Color for comment display (hex or CSS color name).
        is_entry_point: Whether this node is a flow entry point.
        is_disabled: Whether the node should be disabled.
        config: Node-specific configuration object.
        locale_reference: Locale ObjectId for localized content.
        analytics_label: Label for analytics purposes.
        mock: Mock configuration for testing.
    """
    type: str = Field(
        ...,
        description="Type identifier of the node (required, e.g., 'if', 'say', 'think')"
    )
    target: str = Field(
        ...,
        description="ObjectId of the node to attach to (required)"
    )
    mode: str = Field(
        ...,
        description="Placement mode: append, prepend, appendChild, prependChild, insertChildAt, insertAfter, insertBefore"
    )
    position: Optional[int] = Field(
        None,
        ge=0,
        le=2147483647,
        description="Position index for 'insertChildAt' mode (0 to 2147483647)"
    )
    extension: Optional[str] = Field(
        None,
        description="Extension package for this node type"
    )
    label: Optional[str] = Field(
        None,
        description="Custom display label for the node"
    )
    comment: Optional[str] = Field(
        None,
        description="Additional notes about the node"
    )
    comment_color: Optional[str] = Field(
        None,
        alias="commentColor",
        description="Color for comment display (hex or CSS color name)"
    )
    is_entry_point: Optional[bool] = Field(
        None,
        alias="isEntryPoint",
        description="Whether this node is a flow entry point"
    )
    is_disabled: Optional[bool] = Field(
        None,
        alias="isDisabled",
        description="Whether the node should be disabled"
    )
    config: Optional[Dict[str, Any]] = Field(
        None,
        description="Node-specific configuration object"
    )
    locale_reference: Optional[str] = Field(
        None,
        alias="localeReference",
        description="Locale ObjectId for localized content"
    )
    analytics_label: Optional[str] = Field(
        None,
        alias="analyticsLabel",
        description="Label for analytics purposes"
    )
    mock: Optional[NodeMock] = Field(
        None,
        description="Mock configuration for testing"
    )

    @field_validator("target")
    @classmethod
    def validate_target(cls, v: str) -> str:
        """Validate target matches ObjectId format."""
        if not OBJECT_ID_PATTERN.match(v):
            raise ValueError(
                f"Invalid ObjectId format for target: "
                f"must be 24 lowercase hex characters, got '{v}'"
            )
        return v

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        """Validate mode is one of the allowed placement modes."""
        if v not in NODE_PLACEMENT_MODES:
            raise ValueError(
                f"Invalid mode: must be one of {sorted(NODE_PLACEMENT_MODES)}, got '{v}'"
            )
        return v

    @field_validator("locale_reference")
    @classmethod
    def validate_locale_reference(cls, v: Optional[str]) -> Optional[str]:
        """Validate locale_reference matches ObjectId format."""
        return _validate_object_id(v, "locale_reference")

    @field_validator("comment_color")
    @classmethod
    def validate_comment_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate comment_color is a valid hex color or CSS color name."""
        return _validate_comment_color(v)


class NodeMove(CognigyCreateUpdateModel):
    """
    Input model for moving a Chart Node within the flow.

    Used with POST /v2.0/flows/{flowId}/chart/nodes/{nodeId}/move.
    """

    target: str = Field(
        ...,
        description="ObjectId of the anchor node relative to which the node is moved",
    )
    mode: str = Field(
        ...,
        description="Placement mode: append, prepend, appendChild, prependChild, insertChildAt, insertAfter, insertBefore",
    )
    position: Optional[int] = Field(
        None,
        ge=0,
        le=2147483647,
        description="Index for 'insertChildAt' mode only (0 to 2147483647)",
    )

    @field_validator("target")
    @classmethod
    def validate_target(cls, v: str) -> str:
        if not OBJECT_ID_PATTERN.match(v):
            raise ValueError(
                f"Invalid ObjectId format for target: "
                f"must be 24 lowercase hex characters, got '{v}'"
            )
        return v

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        if v not in NODE_PLACEMENT_MODES:
            raise ValueError(
                f"Invalid mode: must be one of {sorted(NODE_PLACEMENT_MODES)}, got '{v}'"
            )
        return v


class NodeUpdate(CognigyCreateUpdateModel):
    """
    Input model for updating a Chart Node.

    Contains optional fields for updating an existing node via the
    PATCH /v2.0/flows/{flowId}/chart/nodes/{nodeId} endpoint.
    Only provided fields will be updated.

    Allowed fields (verified from API payload): label, analytics_label,
    comment, comment_color, is_entry_point, is_disabled, config, mock.
    Excluded from this model (not accepted by PATCH): type, extension,
    locale_reference, locale_id. TODO: Confirm allowed/excluded fields
    with Cognigy and update this model if the API changes.

    Attributes:
        label: New display label.
        comment: New comment text.
        comment_color: New comment color (hex or CSS color name).
        is_entry_point: New entry point status.
        is_disabled: New disabled status.
        config: New node configuration.
        analytics_label: New analytics label.
        mock: New mock configuration.
    """
    label: Optional[str] = Field(
        None,
        description="New display label"
    )
    comment: Optional[str] = Field(
        None,
        description="New comment text"
    )
    comment_color: Optional[str] = Field(
        None,
        alias="commentColor",
        description="New comment color (hex or CSS color name)"
    )
    is_entry_point: Optional[bool] = Field(
        None,
        alias="isEntryPoint",
        description="New entry point status"
    )
    is_disabled: Optional[bool] = Field(
        None,
        alias="isDisabled",
        description="New disabled status"
    )
    config: Optional[Dict[str, Any]] = Field(
        None,
        description="New node configuration"
    )
    analytics_label: Optional[str] = Field(
        None,
        alias="analyticsLabel",
        description="New analytics label"
    )
    mock: Optional[NodeMock] = Field(
        None,
        description="New mock configuration"
    )

    @field_validator("comment_color")
    @classmethod
    def validate_comment_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate comment_color is a valid hex color or CSS color name."""
        return _validate_comment_color(v)


class ChartNodeSummary(CognigyBaseModel):
    """
    Summary node information from the chart topology endpoint.
    
    Contains basic node metadata without full configuration details.
    Used in the GET /v2.0/flows/{flowId}/chart response.
    
    Attributes:
        id: MongoDB ObjectId of the node.
        type: Type identifier of the node.
        reference_id: UUID reference for the node.
        extension: Extension package providing this node type.
        label: Custom display label.
        analytics_label: Label for analytics.
        comment: Additional notes.
        comment_color: Color for comment display.
        is_collapsed: Whether node is collapsed in editor.
        is_entry_point: Whether node is an entry point.
        is_disabled: Whether node is disabled.
    """
    type: Optional[str] = Field(
        None,
        description="Type identifier of the node"
    )
    reference_id: Optional[str] = Field(
        None,
        alias="referenceId",
        description="UUID reference for the node"
    )
    extension: Optional[str] = Field(
        None,
        description="Extension package providing this node type"
    )
    label: Optional[str] = Field(
        None,
        description="Custom display label"
    )
    analytics_label: Optional[str] = Field(
        None,
        alias="analyticsLabel",
        description="Label for analytics"
    )
    comment: Optional[str] = Field(
        None,
        description="Additional notes about the node"
    )
    comment_color: Optional[str] = Field(
        None,
        alias="commentColor",
        description="Color for comment display"
    )
    is_collapsed: Optional[bool] = Field(
        None,
        alias="isCollapsed",
        description="Whether node is collapsed in editor"
    )
    is_entry_point: Optional[bool] = Field(
        None,
        alias="isEntryPoint",
        description="Whether node is an entry point"
    )
    is_disabled: Optional[bool] = Field(
        None,
        alias="isDisabled",
        description="Whether node is disabled"
    )


class ChartRelation(CognigyBaseModel):
    """
    Relation information defining node connections in the chart.
    
    Describes the hierarchical and sequential relationships between nodes.
    
    Attributes:
        id: MongoDB ObjectId of this relation record.
        node: ObjectId of the node this relation describes.
        children: List of ObjectIds of child nodes.
        next: ObjectId of the next sibling node (nullable).
    """
    node: Optional[str] = Field(
        None,
        description="ObjectId of the node this relation describes"
    )
    children: List[str] = Field(
        default_factory=list,
        description="List of ObjectIds of child nodes"
    )
    next: Optional[str] = Field(
        None,
        description="ObjectId of the next sibling node (nullable)"
    )

    @field_validator("node")
    @classmethod
    def validate_node(cls, v: Optional[str]) -> Optional[str]:
        """Validate node matches ObjectId format."""
        return _validate_object_id(v, "node")

    @field_validator("next")
    @classmethod
    def validate_next(cls, v: Optional[str]) -> Optional[str]:
        """Validate next matches ObjectId format."""
        return _validate_object_id(v, "next")


class NodeSearchMatch(BaseModel):
    """
    A single match within a node search result.

    Indicates where the search filter matched in the node.

    Attributes:
        field_type: Type of the matched field (e.g. "text").
        match_path: Path of the matched field (e.g. "referenceId").
    """
    field_type: str = Field(..., alias="fieldType")
    match_path: str = Field(..., alias="matchPath")

    model_config = {"populate_by_name": True}


class NodeSearchResult(BaseModel):
    """
    One item from the node search API (GET .../chart/nodes/search).

    Contains the node identifier and the list of match locations,
    not the full node configuration.

    Attributes:
        node_id: ObjectId of the node (24 hex characters).
        node_reference_id: UUID reference for the node.
        matches: List of match locations for the search filter.
    """
    node_id: str = Field(..., alias="nodeId")
    node_reference_id: str = Field(..., alias="nodeReferenceId")
    matches: List[NodeSearchMatch] = Field(default_factory=list, alias="matches")

    model_config = {"populate_by_name": True}


class Chart(CognigyBaseModel):
    """
    Full chart response containing nodes and their relations.
    
    Returned by GET /v2.0/flows/{flowId}/chart. Contains summary
    information about all nodes and their topological relationships.
    
    Attributes:
        nodes: List of node summaries in the chart.
        relations: List of relations defining node connections.
    """
    nodes: List[ChartNodeSummary] = Field(
        default_factory=list,
        description="List of node summaries in the chart"
    )
    relations: List[ChartRelation] = Field(
        default_factory=list,
        description="List of relations defining node connections"
    )
