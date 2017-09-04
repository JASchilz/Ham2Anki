class AnkiTSV(object):

    def format_questions(self, questions):

        formatted_questions = []
        for question in questions:
            choices = '<br>'.join([
                    '({}) {}'.format(key, question.choices[key])
                    for key in sorted(question.choices.keys())
                ])

            formatted_questions.append('\t'.join([
                    question.head,
                    question.question,
                    choices,
                    question.answer_key,
                    question.choices[question.answer_key]
                ]))

        return '\n'.join(formatted_questions)

    def write_questions(self, questions, path):
        data = self.format_questions(questions)

        with open(path, 'w', encoding='utf-8') as out_file:
            out_file.write(data)
