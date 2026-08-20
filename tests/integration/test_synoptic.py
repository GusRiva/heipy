"""
Tests for full pipelines

"""
from heipy.parsers import heiparse
from heipy.heipipe.pipeline_library.synoptic import SynopticPipe
from heipy.heipipe.step_library.synoptic import append_synoptic_links
from tests.helpers.xml_compare import assert_xml_equal



class TestSynopticPipeline:
    """Test Synoptic Pipeline."""

    def test_synoptic_basic(self, synoptic_fixtures_dir):
        mapping = {
            "Gregorius_A_Rom_kurz.xml": {
                "siglum": "A",
                "dwork_project": "bav_reg_lat_1354_foll108-136",
                "synoptic_pre": "a"
            },
            "Gregorius_B_Strassburg_kurz.xml": {
                "siglum": "B",
                "dwork_project": "mam_ms_314_foll55-120",
                "synoptic_pre": "b"
            },
            "Gregorius_J_Berlin_kurz.xml": {
                "siglum": "J",
                "dwork_project": "sbb-pk_mgq979_pagg1-194",
                "synoptic_pre": "j"
            }
        }
        for file in synoptic_fixtures_dir.iterdir():
            if not file.is_file():
                continue
            file_name = file.name
            if file_name == "synoptic.xml":
                continue    
            pipe_synoptic = SynopticPipe()
            pipe_synoptic.add_step(append_synoptic_links.get_step(), 
                            parameters={'synoptic_map': synoptic_fixtures_dir / 'synoptic.xml',
                                        'base_file': file_name,
                                        'sigla_mapping': mapping})
            result = pipe_synoptic.execute(file)
            # output_file_path = synoptic_fixtures_dir / f"expected/{file_name}"
            # output_file_path.write_text(result, encoding="utf-8")
            assert_xml_equal(heiparse(synoptic_fixtures_dir / f"expected/{file_name}"), result)
        return