import re
from schema import BookingAnswer
from langchain_core.output_parsers import PydanticOutputParser


class OutputParser:
    def parse(self, text: str) -> str:
        # Remove labels
        text = re.sub(r"(Answer:|Question:)", "", text, flags=re.IGNORECASE)

        # Split by bullets, numbers, or dashes
        lines = re.split(r"\n|•|-|\d+\.", text)

        # Clean whitespace
        steps = [line.strip() for line in lines if line.strip()]

        # Remove lines that are clearly questions
        steps = [s for s in steps if not s.endswith("?")]

        # Deduplicate while preserving order
        seen = set()
        unique_steps = []
        for step in steps:
            if step not in seen:
                seen.add(step)
                unique_steps.append(step)

        # Join nicely
        return " • ".join(unique_steps)
