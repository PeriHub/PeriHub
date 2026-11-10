from backend.app.support import solver_backend
from backend.app.support.file_handler import FileHandler


class _Client:
    """Fake PeriLab API: `version` is every file's ETag; downloads only counts real transfers."""

    def __init__(self):
        self.downloads = 0
        self.version = "v1"

    def list_files(self, job_id):
        return ["Dogbone.e", "out/Dogbone.csv", "../escape.txt"]

    def download_file(self, job_id, name, dest, known_version=None):
        if known_version == self.version:
            return self.version
        self.downloads += 1
        with open(dest, "w") as file:
            file.write(f"{name} {self.version}")
        return self.version


def test_fetch_external_results_keeps_traffic_down(monkeypatch, tmp_path):
    monkeypatch.setattr(FileHandler, "get_local_simulation_path", staticmethod(lambda: str(tmp_path)))
    client = _Client()
    fetch = solver_backend.fetch_external_results

    folder = fetch(client, "j1", finished=False)
    assert (tmp_path / "_external/j1/out/Dogbone.csv").read_text() == "out/Dogbone.csv v1"
    assert not (tmp_path / "_external/escape.txt").exists()  # never written outside the job folder
    assert client.downloads == 2

    fetch(client, "j1", finished=False)  # running, polled again right away: throttled
    assert client.downloads == 2

    monkeypatch.setattr(solver_backend, "EXTERNAL_REFRESH_SECONDS", 0)
    fetch(client, "j1", finished=False)  # refresh due, but nothing changed: no transfer
    assert client.downloads == 2

    client.version = "v2"
    fetch(client, "j1", finished=True)  # finished with new output: downloaded once more...
    fetch(client, "j1", finished=True)  # ...then served from disk
    assert client.downloads == 4
    assert (tmp_path / "_external/j1/Dogbone.e").read_text() == "Dogbone.e v2"

    solver_backend.drop_result_cache("j1")
    assert not (tmp_path / "_external/j1").exists() and not (tmp_path / "_external/j1.json").exists()
    assert folder.endswith("j1")
