from ..steps import Pipeline
from ..step_library import delete_comments, normalize_unicode, langusage, break_no, format_header, combining_to_entities
from ..step_library.public import check_prefixes, replace_schema_url, update_changeList, check_for_ub_publisher


class PublicPipe(Pipeline):
    def __init__(self, parameters = None):
        pipe_steps = [
            check_for_ub_publisher.get_step(),
            delete_comments.get_step(),
            normalize_unicode.get_step(),
            check_prefixes.get_step(),
            replace_schema_url.get_step(),
            langusage.get_step(),
            break_no.get_step(),
            update_changeList.get_step(),
            # string-based steps: any later step would parse the document again
            # and undo the formatting and the character references
            format_header.get_step(),
            combining_to_entities.get_step()
        ]
        
        description = "Public Pipeline - Standard"
        super().__init__(steps=pipe_steps, name="public_pipe", desc=description, serial=False)
