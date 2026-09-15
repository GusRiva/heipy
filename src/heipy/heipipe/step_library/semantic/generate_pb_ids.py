from ...steps import XsltStep


def get_step():
    return XsltStep(files=['generate_pb_ids.xsl'],
                    name="generate_pb_ids", pipe_files=True)

