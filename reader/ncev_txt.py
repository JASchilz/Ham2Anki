from question import Question


class NCEVTxt(object):

    @staticmethod
    def is_a_question(s):
        return s.strip().split('\n')[-1] == '~~'

    @staticmethod
    def process_question_text(question_text):
        question_split = question_text.strip().split('\n')

        head = question_split[0]
        answer_key = head[head.index('(') + 1]
        question_text = question_split[1]
        choices = {
            choice.split('.')[0]: '.'.join(choice.split('.')[1:])[1:]
                for choice in question_split[2:-1]
            }

        return Question(
                head,
                question_text,
                choices,
                answer_key
            )

    @classmethod
    def extract_questions(cls, path):

        with open(path, 'r') as data_file:
            questions = data_file.read().split('\n\n')

        possible_but_rejected = list(
                filter(
                    lambda s: len(s.strip().split('\n')) > 4 and not cls.is_a_question(s),
                    questions
                )
            )

        question_texts = list(filter(cls.is_a_question, questions))

        processed_questions = []
        error_questions = []
        for question_text in question_texts:
            try:
                processed_questions.append(cls.process_question_text(question_text))
            except:
                error_questions.append(question_text)

        return processed_questions, possible_but_rejected, error_questions
