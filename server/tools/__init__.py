import inspect
import logging

from .base_tool import BaseTool
from .video_search import VideoSearchTool
from .question_generator import QuestionGeneratorTool

logger = logging.getLogger(__name__)

AVAILABLE_TOOLS = {
    "VIDEO_SEARCH": VideoSearchTool,
    "QUESTION_GENERATOR": QuestionGeneratorTool,
}


def _validate_tools():
    invalid_tools = []

    for name, tool_class in AVAILABLE_TOOLS.items():
        if not (inspect.isclass(tool_class) and issubclass(tool_class, BaseTool)):
            invalid_tools.append(
                f"'{name}': {tool_class} is not inherit from BaseClass"
            )

        if inspect.isabstract(tool_class):
            invalid_tools.append(
                f"'{name}': {tool_class} has unimplemented abstract methods"
            )

    if invalid_tools:
        logger.error(
            "Tool validation failed for some tools:" + "\n - ".join(invalid_tools)
        )
    else:
        logger.debug("Tool validation completed.")


_validate_tools()


def create_tool(tool_name: str) -> BaseTool | None:
    """
    Factory function for creating tool instance.
    """
    logger.debug(f"Factory: Attempting to create tool '{tool_name}'")

    tool_class = AVAILABLE_TOOLS.get(tool_name)

    if tool_class:
        try:
            tool_instance = tool_class()
            return tool_instance
        except Exception as e:
            logger.error(
                f"Factory failed to initialize tool '{tool_name}': {e}", exc_info=True
            )
            return None
    else:
        logger.error(f"Factory: Tool '{tool_name}' not found in registry.")
        logger.debug(f"Available tools are: {list(AVAILABLE_TOOLS.keys())}")
        return None


def execute_tool(tool_name: str, arguments: dict):
    """
    Orchestrates tool creation and execution.
    """

    tool_instance = create_tool(tool_name)

    if tool_name:
        try:
            logger.debug("Orchestrator: Calling run() on {tool_instance}...")
            result = tool_instance.run(**arguments)
            logger.debug("<<< Orchestrator: Tool '{tool_name}' execution successfully.")
            return result
        except (ValueError, TypeError) as arg_err:
            logger.error(
                f"Orchestrator: Invalid argument provided to {tool_instance}: {arg_err}"
            )
            return None
        except Exception as e:
            logger.exception(
                f"Orchestrator: Unexpected error during {tool_instance}.run()"
            )
            return None
    else:
        logger.error(
            f"<<< Orchestrator: Tool '{tool_name}' execution failed (could not create instance)."
        )
        return None


__all__ = ["execute_tool"]
