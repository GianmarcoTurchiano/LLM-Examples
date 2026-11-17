import json
from IPython.display import display, Markdown

_TEXT_TEMPLATE = (
    '<blockquote>\n\n'
        '{text}\n\n'
    '</blockquote>\n\n'
)

_ANSWER_TEMPLATE = (
    '<details open>'
        '<summary>'
            '<u>{title}</u>'
        '</summary>\n\n'
        '<blockquote>\n\n'
            '{text}\n\n'
        '</blockquote>\n\n'
    '</details>'
)

def print_dictionary(d):
    j = json.dumps(d, indent=4)
    print(j)

def print_markdown(markdown_txt, text_template=_TEXT_TEMPLATE):
    text_output = text_template.format(text=markdown_txt)
    return display(Markdown(text_output), display_id=False)

def print_markdown_streaming(stream, answer_template=_ANSWER_TEMPLATE):
    thinking_text=''
    content_text=''

    thinking_handle = display(Markdown(thinking_text), display_id=True)
    content_handle = display(Markdown(content_text), display_id=True)
    
    for chunk in stream:
        message = chunk['message']
        
        if 'thinking' in message:
            thinking_text += message['thinking']
            answer_output = answer_template.format(title='Think', text=thinking_text)
            thinking_handle.update(Markdown(answer_output))
        elif 'content' in message:
            content_text += message['content']
            answer_output = answer_template.format(title='Content', text=content_text)
            content_handle.update(Markdown(answer_output))

    answer = {
        'role': 'assistant',
        'content': content_text
    }

    if len(thinking_text) > 0:
        answer['thinking'] = thinking_text
        
    return answer
