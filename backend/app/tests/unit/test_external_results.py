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


class _BatchClient:
    """Fake PeriLab API for a deviation batch: the default deck's job plus one job per sample."""

    def list_files(self, job_id):
        suffix = "" if job_id == "j0" else "_" + job_id[1:]
        return [f"M_Exodus{suffix}.e", f"M_CSV{suffix}.csv", "M_deviations.json"]

    def download_file(self, job_id, name, dest, known_version=None):
        with open(dest, "w") as file:
            file.write(f"{job_id}:{name}")
        return "v1"


class _Backend:
    def __init__(self, shares_local_filesystem):
        self.shares_local_filesystem = shares_local_filesystem

    def client(self):
        return _BatchClient()


def test_collect_batch_results_merges_all_samples(monkeypatch, tmp_path):
    monkeypatch.setattr(FileHandler, "get_local_simulation_path", staticmethod(lambda: str(tmp_path)))
    ids, variants = ["j0", "j1", "j2"], ["-1", "1", "2"]

    folder = solver_backend.collect_batch_results(_Backend(False), "run1", ids, variants, finished=True)
    names = sorted(p.name for p in (tmp_path / "_runs/run1").iterdir())
    assert names == ["M_CSV.csv", "M_CSV_1.csv", "M_CSV_2.csv", "M_Exodus.e", "M_deviations.json"]  # no sample .e
    assert (tmp_path / "_runs/run1/M_deviations.json").read_text() == "j0:M_deviations.json"  # first copy wins

    solver_backend.drop_run_results("run1")
    assert not (tmp_path / "_runs/run1").exists() and not list((tmp_path / "_runs").iterdir())

    for job_id in ids:  # local solver: each job writes simulations/<job_id>/ on the shared volume
        (tmp_path / job_id).mkdir()
        (tmp_path / job_id / f"M_CSV_{job_id}.csv").write_text(job_id)
    folder = solver_backend.collect_batch_results(_Backend(True), "run2", ids, variants, finished=True)
    assert (tmp_path / "_runs/run2/M_CSV_j2.csv").read_text() == "j2"
    assert (tmp_path / "_runs/run2/M_CSV_j2.csv").is_symlink() and folder.endswith("run2")
