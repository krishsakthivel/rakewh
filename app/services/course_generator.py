# if the json breaks again im quitting
import os
import json
import re
from typing import List, Dict

DEMO_MODE = not os.getenv("GROQ_API_KEY")

DEMO_COURSE = {
    "metadata": {
        "title": "Sample Course",
        "description": "A demo course generated from your notes."
    },
    "modules": [
        {
            "order": 1,
            "title": "Core Concepts",
            "explanation": "This is a demo explanation. In production with a Groq API key, this will be generated from your actual PDF content.\n\nThe system reads your notes, identifies the key ideas, and writes a clear plain-English summary for each concept module.\n\nEach module is designed to build on the last, so you always have the foundation you need before moving forward.",
            "key_concepts": ["concept one", "concept two", "concept three", "concept four"],
            "teaching_rubric": {
                "required_concepts": ["concept one", "concept two", "concept three"],
                "required_relationships": ["how concept one leads to concept two"],
                "minimum_coverage_threshold": 0.75
            },
            "questions": [
                {
                    "text": "This is a demo quiz question. Which of these is an example of concept one?",
                    "options": ["Option A (correct)", "Option B", "Option C", "Option D"],
                    "correct_index": 0,
                    "explanation": "Option A is correct because it directly demonstrates concept one in action.",
                    "concept_tag": "concept one",
                    "difficulty": 0.3
                },
                {
                    "text": "What is the relationship between concept one and concept two?",
                    "options": ["They are opposites", "One leads to the other", "They are unrelated", "They are identical"],
                    "correct_index": 1,
                    "explanation": "Concept one sets the foundation that concept two builds upon.",
                    "concept_tag": "concept two",
                    "difficulty": 0.5
                },
                {
                    "text": "Which best describes concept three?",
                    "options": ["A process", "A static state", "An external factor", "None of these"],
                    "correct_index": 0,
                    "explanation": "Concept three is best understood as an active process, not a fixed condition.",
                    "concept_tag": "concept three",
                    "difficulty": 0.4
                },
                {
                    "text": "In what situation would concept two NOT apply?",
                    "options": ["When concept one is absent", "When concept three is present", "Always applies", "When conditions are ideal"],
                    "correct_index": 0,
                    "explanation": "Concept two depends on concept one being established first.",
                    "concept_tag": "concept two",
                    "difficulty": 0.6
                },
                {
                    "text": "What is the most accurate summary of concept four?",
                    "options": ["It modifies the outcome", "It replaces concept one", "It is irrelevant", "It causes concept three"],
                    "correct_index": 0,
                    "explanation": "Concept four acts as a modifier that changes how the other concepts interact.",
                    "concept_tag": "concept four",
                    "difficulty": 0.5
                }
            ]
        },
        {
            "order": 2,
            "title": "Applying the Ideas",
            "explanation": "This second module is also a demo. With a Groq API key set, this would cover the practical application of the concepts extracted from your notes.\n\nThe course generator breaks your PDF into logical chunks and creates a separate module for each major topic it finds. A typical PDF produces between three and six modules depending on length and complexity.\n\nEach module ends with a teach session where you explain the concept to Pip, a chatbot that starts with zero knowledge and asks follow-up questions until your explanation is complete.",
            "key_concepts": ["application", "context", "edge cases", "synthesis"],
            "teaching_rubric": {
                "required_concepts": ["application", "context", "edge cases"],
                "required_relationships": ["how context changes application"],
                "minimum_coverage_threshold": 0.75
            },
            "questions": [
                {
                    "text": "When applying these concepts in a new context, what should you check first?",
                    "options": ["Whether the context matches the assumptions", "The exact wording of the rule", "Historical examples only", "Nothing, rules always apply"],
                    "correct_index": 0,
                    "explanation": "Context determines whether a concept applies. Always check assumptions before applying a rule.",
                    "concept_tag": "context",
                    "difficulty": 0.4
                },
                {
                    "text": "An edge case is best described as:",
                    "options": ["A situation where normal rules break down", "The most common scenario", "An error in the theory", "A simplified version of the concept"],
                    "correct_index": 0,
                    "explanation": "Edge cases test the limits of a concept and reveal where it stops being reliable.",
                    "concept_tag": "edge cases",
                    "difficulty": 0.3
                },
                {
                    "text": "Synthesis means:",
                    "options": ["Combining ideas into a unified understanding", "Memorizing each concept separately", "Repeating information", "Ignoring contradictions"],
                    "correct_index": 0,
                    "explanation": "Synthesis is about connecting ideas so they form a coherent whole rather than isolated facts.",
                    "concept_tag": "synthesis",
                    "difficulty": 0.5
                },
                {
                    "text": "Which is a sign that you have genuinely understood something?",
                    "options": ["You can explain it simply to someone who knows nothing", "You can recite the definition", "You passed a multiple choice test", "You read it three times"],
                    "correct_index": 0,
                    "explanation": "The Feynman test: if you can explain it simply, you know it. Recognition is not the same as understanding.",
                    "concept_tag": "application",
                    "difficulty": 0.2
                },
                {
                    "text": "What is the best way to handle a concept you cannot explain to someone else?",
                    "options": ["Go back to the source material and re-read it", "Memorize the definition", "Skip it", "Assume you understand it"],
                    "correct_index": 0,
                    "explanation": "If you cannot explain it, you have a gap. The fix is to revisit the material, not to repeat the words.",
                    "concept_tag": "synthesis",
                    "difficulty": 0.3
                }
            ]
        }
    ]
}


def _groq_generate(prompt: str, max_tokens: int = 2000) -> str:
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


def _clean_json(text: str) -> str:
    text = text.replace("```json", "").replace("```", "").strip()
    def fix_control_chars(m):
        inner = m.group(1)
        inner = inner.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        return '"' + inner + '"'
    text = re.sub(r'"((?:[^"\\]|\\.)*)"', fix_control_chars, text, flags=re.DOTALL)
    return text


COURSE_TITLE_PROMPT = """Given these notes, produce a short course title and one sentence description.
Return only JSON with no markdown: {{"title": "...", "description": "..."}}

Notes:
{text}"""

MODULE_GENERATION_PROMPT = """You are building a module for a study course based on the text below.

Return only valid JSON with no markdown and this exact structure:
{{
  "title": "short module title",
  "explanation": "2-3 short paragraphs, max 2-3 sentences each. One idea per paragraph. No walls of text. No jargon without a quick definition right after it. Write like a smart friend texting you the key points before an exam, not like a textbook.",
  "key_concepts": ["concept1", "concept2", "concept3", "concept4", "concept5"],
  "teaching_rubric": {{
    "required_concepts": ["concept a student must cover"],
    "required_relationships": ["relationships between concepts that must be explained"],
    "minimum_coverage_threshold": 0.75
  }},
  "questions": [
    {{
      "text": "question text",
      "options": ["option A", "option B", "option C", "option D"],
      "correct_index": 0,
      "explanation": "why this answer is correct",
      "concept_tag": "which concept this tests",
      "difficulty": 0.5
    }}
  ]
}}

Generate 5 quiz questions. Difficulty ranges from 0.0 to 1.0.
Keep all string values on a single line with no line breaks inside them.

Source text:
{chunk}"""


def generate_course_metadata(chunks: List[str]) -> Dict:
    combined = '\n\n'.join(chunks[:3])[:4000]
    text = _groq_generate(COURSE_TITLE_PROMPT.format(text=combined), max_tokens=256)
    return json.loads(_clean_json(text))


def generate_module(chunk: str) -> Dict:
    text = _groq_generate(MODULE_GENERATION_PROMPT.format(chunk=chunk))
    return json.loads(_clean_json(text))


def generate_full_course(chunks: List[str]) -> Dict:
    if DEMO_MODE:
        return DEMO_COURSE

    metadata = generate_course_metadata(chunks)
    modules = []
    for i, chunk in enumerate(chunks):
        mod = generate_module(chunk)
        mod["order"] = i + 1
        modules.append(mod)
    return {"metadata": metadata, "modules": modules}
