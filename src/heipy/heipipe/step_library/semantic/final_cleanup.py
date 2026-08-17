from ...steps import XsltStep


def get_step():
    return XsltStep(files=['final_cleanup.xsl'],
                    name="final_cleanup", pipe_files=True)

