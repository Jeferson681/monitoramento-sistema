import os
import tempfile

def test_gerar_log_cria_arquivo():
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ["PASTA_SERVICES"] = temp_dir
        gerar_log("teste", "cpu", 50, 60, "Mensagem de teste")
        assert os.path.exists(os.path.join(temp_dir, "monitoramento.log"))