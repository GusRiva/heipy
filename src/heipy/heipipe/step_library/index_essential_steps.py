from ..steps import XsltStep


def get_step():
    return XsltStep(files=['index/doublePosting.xsl',
                           'index/verbalizeDates.xsl',
                           'index/preferredAppellation.xsl'],
                            name="index_essential_steps", pipe_files=True)

