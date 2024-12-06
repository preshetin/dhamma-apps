import sys
from dotenv import load_dotenv
from shared_functions import get_answer_from_document

load_dotenv()

# Usage:
# python utils/childen_playground.py "скинь ссылку на письмо домой"
if __name__ == '__main__':

    query = sys.argv[1]

    index_name = "children-courses-org"
    namespace = "children-courses-org"

    result = get_answer_from_document(query, index_name, namespace)


    print('\n\n\n')
    print('final result', result)
    print('\n\n\n')
