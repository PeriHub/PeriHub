# SPDX-FileCopyrightText: 2023 PeriHub <https://github.com/PeriHub/PeriHub>
#
# SPDX-License-Identifier: Apache-2.0

"""
doc
"""


class SbatchCreator:
    """doc"""

    def __init__(
        self,
        filename="Model",
        model_folder_name="Default",
        remotepath="",
        output="",
        job="",
        usermail="",
        trial=True,
        job_ids="-1",
    ):
        """doc"""
        self.nodes = job.nodes
        self.tasks = job.tasks
        self.tasks_per_node = job.tasksPerNode
        self.cpus_per_task = job.cpusPerTask
        self.multithread = job.multithread
        self.time = job.time
        self.filename = filename
        self.model_folder_name = model_folder_name
        self.user = "f_peridi"
        self.account = job.account
        self.mail = usermail
        self.output_dict = output
        self.remotepath = remotepath
        self.trial = trial
        self.job_ids = job_ids

    def create_sbatch(self):
        """doc"""
        nodes = -(-int(self.tasks) // 64)
        string = "#!/bin/bash" + "\n"
        string += "#SBATCH --job-name=" + str(self.filename + "_" + self.model_folder_name) + "\n"
        string += "#SBATCH --nodes=" + str(nodes) + "\n"
        # string += "#SBATCH --nodes=" + str(self.nodes) + "\n"
        # string += "#SBATCH --tasks-per-node=" + str(self.tasks_per_node) + "\n"
        if self.multithread:
            string += "#SBATCH --hint=multithread" + "\n"
        else:
            string += "#SBATCH --hint=nomultithread" + "\n"
        string += "#SBATCH --ntasks=" + str(self.tasks) + "\n"
        string += "#SBATCH --cpus-per-task=" + str(self.cpus_per_task) + "\n"
        string += "#SBATCH --time=" + self.time + "\n"
        string += "#SBATCH --account=" + str(self.account) + "\n"
        string += "#SBATCH --partition=rome" + "\n"
        string += "#SBATCH --constraint=mhz-3200" + "\n"

        if self.mail != "":
            string += "#SBATCH --mail-user=" + self.mail + "\n"
            string += "#SBATCH --mail-type ALL" + "\n"

        string += "module purge" + "\n"
        string += "module use /home/f_peridi/julia/easybuild-installed/modules/all" + "\n"
        string += "module load Julia/1.9.3-linux-x86_64" + "\n"
        string += "module load GCC/12.2.0" + "\n"
        string += "module load OpenMPI/4.1.5" + "\n"

        string += "srun julia -e '" + 'using PeriLab; PeriLab.main("' + self.filename + '.yaml"' + ";silent=true) \n"

        return string

    def create_sh(self, verbose, docker=True, cluster_perilab_path=""):
        """doc"""

        string = "#!/bin/sh \n"
        string = "> pid.txt \n"
        for job_id in self.job_ids.split(","):
            filename = self.filename + ".yaml"
            if job_id != "-1":
                filename = self.filename + "_" + job_id + ".yaml"
            if self.trial:
                string += "timeout 600s "
            if docker:
                string += "/app/PeriLab/bin/PeriLab -s "
                if verbose:
                    string += "-v "
                string += filename
            else:
                if self.tasks > 1:
                    string += "mpiexecjl -n " + str(self.tasks) + " "
                string += "julia -e '" + 'using PeriLab; PeriLab.main("' + filename + '";silent=true'
                if verbose:
                    string += ";verbose=true"
                string += ")'"
            string += " & echo $! >> pid.txt \n"
        string += "while read -r pid; do \n"
        string += "    wait $pid \n"
        string += "    echo 'Job $pid finished.' \n"
        string += "done < pid.txt \n"
        string += "rm pid.txt \n"
        string += "echo 'All simulations finished.'"

        return string
