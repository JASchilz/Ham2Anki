from question import Question


class NCEVTxt(object):

    def extract_questions(self, path):

        is_a_question = lambda s: s.strip().split('\n')[-1] == '~~'

        with open(path, 'r') as data_file:
            questions = data_file.read().split('\n\n')


        possible_but_rejected = list(
                filter(
                    lambda s: len(s.strip().split('\n')) > 4 and not is_a_question(s),
                    questions
                )
            )

        if possible_but_rejected:
            print("POSSIBLE QUESTIONS REJECTED:")
            print('\n\n'.join(possible_but_rejected))

        questions = list(filter(is_a_question, questions))

        processed_questions = []
        for question in questions:

            try:
                question_split = question.strip().split('\n')

                head = question_split[0]
                answer_key = head[head.index('(') + 1]
                question_text = question_split[1]
                choices = {
                        choice.split('.')[0]: '.'.join(choice.split('.')[1:])[1:]
                        for choice in question_split[2:-1]
                    }

                processed_questions.append(
                        Question(
                            head,
                            question_text,
                            choices,
                            answer_key
                        )
                    )
            except:
                print("ERROR PROCESSING QUESTION:\n{}".format(question))


        return processed_questions
