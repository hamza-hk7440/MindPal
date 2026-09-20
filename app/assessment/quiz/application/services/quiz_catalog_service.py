from __future__ import annotations

from copy import deepcopy


class QuizCatalogService:
    def __init__(self) -> None:
        self._quizzes = {
            "mindpal-basics": {
                "code": "mindpal-basics",
                "title": "MindPal Platform Basics",
                "description": "A short demo quiz that shows how the assessment module can work.",
                "questions": [
                    {
                        "id": "q1",
                        "prompt": "Which module handles chat conversations and streamed answers?",
                        "choices": [
                            {"id": "a", "label": "Chat"},
                            {"id": "b", "label": "Ingestion"},
                            {"id": "c", "label": "Assessment"},
                        ],
                        "answer": "a",
                        "explanation": "The chat module stores conversations and streams responses.",
                    },
                    {
                        "id": "q2",
                        "prompt": "Which module turns uploads into chunks and vectors?",
                        "choices": [
                            {"id": "a", "label": "User management"},
                            {"id": "b", "label": "Ingestion"},
                            {"id": "c", "label": "Chat"},
                        ],
                        "answer": "b",
                        "explanation": "The ingestion module owns resources, chunks, and vectorization.",
                    },
                    {
                        "id": "q3",
                        "prompt": "What is the current frontend foundation in this workspace?",
                        "choices": [
                            {"id": "a", "label": "React website"},
                            {"id": "b", "label": "No frontend yet"},
                            {"id": "c", "label": "Angular app"},
                        ],
                        "answer": "b",
                        "explanation": "The repository did not include a frontend app, so one is being added.",
                    },
                ],
            }
        }

    def list_quizzes(self) -> list[dict]:
        return [
            {
                "code": quiz["code"],
                "title": quiz["title"],
                "description": quiz["description"],
                "question_count": len(quiz["questions"]),
            }
            for quiz in self._quizzes.values()
        ]

    def get_quiz(self, quiz_code: str) -> dict:
        quiz = self._quizzes.get(quiz_code)
        if quiz is None:
            raise KeyError(quiz_code)
        return deepcopy(quiz)

    def score_quiz(self, quiz_code: str, answers: dict[str, str]) -> dict:
        quiz = self.get_quiz(quiz_code)
        feedback = []
        score = 0

        for question in quiz["questions"]:
            expected_answer = question["answer"]
            selected_answer = answers.get(question["id"])
            correct = selected_answer == expected_answer
            if correct:
                score += 1
            feedback.append(
                {
                    "question_id": question["id"],
                    "prompt": question["prompt"],
                    "selected_answer": selected_answer,
                    "correct_answer": expected_answer,
                    "correct": correct,
                    "explanation": question["explanation"],
                }
            )

        return {
            "quiz_code": quiz_code,
            "score": score,
            "total": len(quiz["questions"]),
            "passed": score == len(quiz["questions"]),
            "feedback": feedback,
        }