# SPDX-FileCopyrightText: 2023 PeriHub <https://gitlab.com/dlr-perihub/PeriHub>
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
        filetype="yaml",
        remotepath="",
        output="",
        job="",
        usermail="",
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
        self.filetype = filetype
        self.user = "f_peridi"
        self.account = job.account
        self.mail = usermail
        self.output_dict = output
        self.remotepath = remotepath

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
        string += "#SBATCH --cpus-per-task=" + str(self.cpus_per_task) + "\n"
        string += "#SBATCH --time=" + self.time + "\n"
        string += "#SBATCH --account=" + str(self.account) + "\n"
        string += "#SBATCH --output=simulation-%j.log" + "\n"
        string += "#SBATCH --error=simulation-%j.log" + "\n"
        string += "#SBATCH --open-mode=append" + "\n"

        if self.mail != "":
            string += "#SBATCH --mail-user=" + self.mail + "\n"
            string += "#SBATCH --mail-type ALL" + "\n"

        string += "module purge" + "\n"
        string += "module load GCC" + "\n"
        string += "module load OpenMPI" + "\n"
        string += "module load OpenBLAS" + "\n"
        string += "module load netCDF" + "\n"
        string += "module load ScaLAPACK" + "\n"
        string += "module load GCCcore/8.3.0" + "\n"
        string += "module load HDF5" + "\n"
        string += "module load GCCcore/10.2.0" + "\n"
        string += "module load CMake/3.18.4" + "\n"
        string += "module load Eigen" + "\n"
        string += "module load intel" + "\n"
        string += "export PATH=$PATH:/home/" + self.user + "/software/trilinos/bin" + "\n"

        string += (
            "srun --ntasks="
            + str(self.tasks)
            + " /home/"
            + self.user
            + "/software/peridigm/bin/Peridigm "
            + self.filename
            + ".yaml"
            + "\n"
        )

        for out in self.output_dict:
            string += (
                "python /home/"
                + self.user
                + "/peridigm/build/scripts/MergeFiles.py "
                + out.name
                + " "
                + str(self.tasks)
                + "\n"
            )

        string += "rm *.e." + str(self.tasks) + ".*" + "\n"
        string += "rm Output*.log" + "\n"

        return string

    def create_sh(self):
        """doc"""
        string = "#!/bin/sh" + "\n"
        # if self.tasks == 1:
        string += ". /opt/intel/oneapi/mkl/latest/env/vars.sh \n"
        string += "/Peridigm/build/src/Peridigm " + self.filename + "." + self.filetype + "& echo $! > pid.txt \n"
        string += "pid=`cat pid.txt` \n"
        string += "tail --pid=$pid -f /dev/null \n"
        string += "rm pid.txt \n"

        return string
