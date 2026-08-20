import codecs
from lxml import etree as et
from heipy.heipipe.steps import Pipeline, PythonStep
from heipy.heipipe.pipeline_library.semantic import SemanticPipe
from heipy.heipipe.step_library.public import replace_schema_url

test_pipe = Pipeline()

replace_schema_step = replace_schema_url.get_step()
replace_schema_step.add_parameter('schema_url', ' https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS/releases/2026-07-21')
test_pipe.add_step(replace_schema_step)



result = test_pipe.execute("fixtures/minimal/tei_with_entities_resolved.xml")

with codecs.open("tmp/test_pipeline.xml", 'w', 'utf-8') as output:
    output.write(result)

