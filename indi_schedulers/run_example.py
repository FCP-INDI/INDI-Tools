# indi_schedulers/run_example.py
#
# Author: Daniel Clark, 2016

'''
Example module showing how to create and submit a batch file for
running a job via a cluster job scheduler
'''

# Function to submit a job to the scheduler
def cluster_job_submit():
    '''
    '''

    # Import packages
    import commands
    from indi_schedulers import cluster_templates

    # Init variables
    timestamp = str(strftime("%Y_%m_%d_%H_%M_%S"))
    job_scheduler = 'sge' # could also be 'slurm' or 'pbs'
    cluster_files_dir = '/home/ubuntu/cluster_logs'

    # Batch file variables
    shell = commands.getoutput('echo $SHELL')
    user_account = getpass.getuser()

    # Set up config dictionary
    config_dict = {'timestamp' : timestamp,
                   'shell' : shell,
                   'job_name' : 'run_example',
                   'num_tasks' : 24,
                   'queue' : 'all.q',
                   'par_env' : 'mpi_smp',
                   'cores_per_task' : 8,
                   'user' : user_account,
                   'work_dir' : cluster_files_dir}

    # Get string template for job scheduler
    if job_scheduler == 'pbs':
        env_arr_idx = '$PBS_ARRAYID'
        batch_file_contents = cluster_templates.pbs_template
        confirm_str = '(?<=Your job-array )\d+'
        exec_cmd = 'qsub'
    elif job_scheduler == 'sge':
        env_arr_idx = '$SGE_TASK_ID'
        batch_file_contents = cluster_templates.sge_template
        confirm_str = '(?<=Your job-array )\d+'
        exec_cmd = 'qsub'
    elif job_scheduler == 'slurm':
        env_arr_idx = '$SLURM_ARRAY_TASK_ID'
        batch_file_contents = cluster_templates.slurm_template
        confirm_str = '(?<=Submitted batch job )\d+'
        exec_cmd = 'sbatch'

    # Populate rest of dictionary
    config_dict['env_arr_idx'] = env_arr_idx

    # Populate string from config dict values
    batch_file_contents = batch_file_contents % config_dict
    # Write file
    batch_filepath = os.path.join(cluster_files_dir, 'job_submit_%s.%s' \
                                  % (timestamp, job_scheduler))
    with open(batch_filepath, 'w') as f:
        f.write(batch_file_contents)

    # Get output response from job submission
    out = commands.getoutput('%s %s' % (exec_cmd, batch_filepath))

    # Check for successful qsub submission
    if re.search(confirm_str, out) == None:
        err_msg = 'Error submitting %s run to %s queue' % \
                  (config_dict['job_name'], job_scheduler)
        raise Exception(err_msg)

    # Get pid and send to pid file
    pid = re.search(confirm_str, out).group(0)
    pid_file = os.path.join(cluster_files_dir, 'pid.txt')
    with open(pid_file, 'w') as f:
        f.write(pid)
