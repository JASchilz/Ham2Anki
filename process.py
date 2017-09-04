import sys
import os


class Question(object):

    def __init__(self, head, question, choices, answer_key):

        self.head = head
        self.question = question
        self.choices = choices
        self.answer_key = answer_key


def extract_questions(path):

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

    return processed_questions


def format_questions(questions):

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


def write_questions(data, directory):
    
    with open(os.path.join(directory, 'out.txt'), 'w', encoding='utf-8') as out_file:
        out_file.write(data)


if __name__ == '__main__':
    directory, file_name = os.path.split(sys.argv[1])

    questions = extract_questions(sys.argv[1])
    data = format_questions(questions)
    write_questions(data, directory)

